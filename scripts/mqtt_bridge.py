"""MQTT -> durable local inbox -> Laravel. Run from repository root; no DB credentials."""
import argparse
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import queue
import re
import sqlite3
import time
import urllib.error
import urllib.parse
import urllib.request
import paho.mqtt.client as mqtt


def log(event, **fields):
    print(json.dumps(dict(at=datetime.now(timezone.utc).isoformat(), event=event, **fields)), flush=True)


def request(api, method, suffix, payload=None):
    data = json.dumps(payload, allow_nan=False).encode() if payload is not None else None
    req = urllib.request.Request(api + suffix, data=data, method=method,
                                 headers={'Accept': 'application/json', 'Content-Type': 'application/json'})
    try:
        response = urllib.request.urlopen(req, timeout=8)
    except urllib.error.HTTPError as error:
        response = error
    with response:
        body = response.read(1_000_001)
        if len(body) > 1_000_000:
            raise ValueError('API response exceeds limit')
        return response.status, json.loads(body)


def run(args):
    args.state.parent.mkdir(parents=True, exist_ok=True)
    db = sqlite3.connect(args.state)
    db.execute('CREATE TABLE IF NOT EXISTS inbox (device TEXT, seq INTEGER, payload TEXT, state TEXT, attempts INTEGER DEFAULT 0, next_try REAL DEFAULT 0, PRIMARY KEY(device,seq))')
    incoming = queue.Queue(maxsize=1000)
    client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, client_id=args.client_id,
                         clean_session=False, manual_ack=True)
    if os.getenv('MQTT_USERNAME'):
        client.username_pw_set(os.environ['MQTT_USERNAME'], os.getenv('MQTT_PASSWORD'))
    if args.ca:
        client.tls_set(ca_certs=str(args.ca))
    client.reconnect_delay_set(1, 30)

    def connected(client, userdata, flags, reason_code, properties):
        log('mqtt_connected', code=str(reason_code))
        if reason_code == 0:
            client.subscribe('hydromate/+/telemetry', qos=1)

    def message(client, userdata, msg):
        try:
            incoming.put_nowait(msg)
        except queue.Full:
            log('inbox_busy')  # Do not ACK: QoS 1 sender may redeliver.

    client.on_connect = connected
    client.on_subscribe = lambda c, u, mid, codes, props: log('mqtt_subscribed', codes=[str(code) for code in codes])
    client.on_message = message
    client.connect_async(args.host, args.port, keepalive=30)
    client.loop_start()

    def ack(device, seq, status):
        client.publish(f'hydromate/{device}/ack', json.dumps(dict(sequence=seq, status=status)), qos=1, retain=False)

    try:
        while True:
            try:
                msg = incoming.get(timeout=.2)
            except queue.Empty:
                msg = None
            if msg is not None:
                try:
                    match = re.fullmatch(r'hydromate/([A-Za-z0-9_-]{1,64})/telemetry', msg.topic)
                    if not match or len(msg.payload) > 8192 or msg.retain:
                        raise ValueError('invalid topic, size or retained telemetry')
                    payload = json.loads(msg.payload, parse_constant=lambda _: (_ for _ in ()).throw(ValueError('nonfinite')))
                    device = match.group(1)
                    seq = payload.get('sequence')
                    if payload.get('device_id') != device or type(seq) is not int or not 1 <= seq <= 9223372036854775807:
                        raise ValueError('identity/sequence mismatch')
                    canonical = json.dumps(payload, sort_keys=True, separators=(',', ':'), allow_nan=False)
                    row = db.execute('SELECT payload,state FROM inbox WHERE device=? AND seq=?', (device, seq)).fetchone()
                    if row:
                        if row[0] != canonical:
                            log('identity_conflict', device=device, sequence=seq)
                            ack(device, seq, 'conflict')
                        elif row[1] != 'pending':
                            ack(device, seq, row[1])
                    else:
                        db.execute('INSERT INTO inbox(device,seq,payload,state) VALUES(?,?,?,?)', (device, seq, canonical, 'pending'))
                        db.commit()
                        log('queued', device=device, sequence=seq)
                except (ValueError, TypeError, AttributeError, UnicodeError) as error:
                    log('invalid_mqtt', detail=str(error))
                # Inbox is committed before acknowledging transport delivery.
                if msg.qos:
                    client.ack(msg.mid, msg.qos)
            row = db.execute("SELECT device,seq,payload,attempts FROM inbox WHERE state='pending' AND next_try<=? ORDER BY rowid LIMIT 1", (time.time(),)).fetchone()
            if not row:
                continue
            device, seq, canonical, attempts = row
            payload = json.loads(canonical)
            started = time.perf_counter()
            try:
                status, result = request(args.api, 'POST', '/api/measurements', payload)
                outcome = 'pending'
                if status == 201:
                    outcome = 'stored'
                elif status == 409:
                    query = urllib.parse.urlencode(dict(device_id=device, limit=100))
                    code, rows = request(args.api, 'GET', '/api/measurements?' + query)
                    existing = next((r for r in rows if r['sequence'] == seq), None) if code == 200 and isinstance(rows, list) else None
                    # Conflict is success only if the persisted content is identical.
                    outcome = 'stored' if existing and all(existing.get(k) == v for k, v in payload.items()) else 'conflict'
                elif 400 <= status < 500:
                    outcome = 'rejected'
                log('http_result', device=device, sequence=seq, status=status, outcome=outcome,
                    elapsed_ms=round((time.perf_counter()-started)*1000, 2),
                    invalid_fields=list(result.get('errors', {})) if isinstance(result, dict) else [])
            except (OSError, ValueError) as error:
                outcome = 'pending'
                log('http_unavailable', device=device, sequence=seq, error_type=type(error).__name__)
            db.execute('UPDATE inbox SET state=?,attempts=?,next_try=? WHERE device=? AND seq=?',
                       (outcome, attempts+1, time.time()+min(30, 2**min(attempts, 5)), device, seq))
            db.commit()
            if outcome != 'pending':
                ack(device, seq, outcome)
    except KeyboardInterrupt:
        log('stopped')
    finally:
        client.disconnect()
        client.loop_stop()
        db.close()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--host', default='127.0.0.1')
    parser.add_argument('--port', type=int, default=1883)
    parser.add_argument('--api', default='http://127.0.0.1:8000')
    parser.add_argument('--client-id', default='hydromate-local-bridge')
    parser.add_argument('--state', type=Path, default=Path('.local/mqtt-inbox.sqlite'))
    parser.add_argument('--ca', type=Path)
    args = parser.parse_args()
    args.api = args.api.rstrip('/')
    run(args)
