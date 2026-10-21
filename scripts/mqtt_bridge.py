"""MQTT -> durable local inbox -> Laravel. Run from repository root; no DB credentials."""
import argparse
from datetime import datetime, timezone
import json
import ipaddress
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


def measurement_matches_payload(row, payload):
    """Compare acquisition time by instant: Laravel serializes UTC with microseconds."""
    for key, value in payload.items():
        actual = row.get(key)
        if key == 'captured_at' and value is not None:
            try:
                if datetime.fromisoformat(value.replace('Z', '+00:00')) != datetime.fromisoformat(actual.replace('Z', '+00:00')):
                    return False
            except (ValueError, AttributeError, TypeError):
                return False
        elif actual != value:
            return False
    return True


def private_host(host, aliases=()):
    if host in ('localhost', *aliases):
        return True
    try:
        address = ipaddress.ip_address(host)
        return address.is_loopback or (address.version == 4 and any(address in ipaddress.ip_network(n)
            for n in ('10.0.0.0/8', '172.16.0.0/12', '192.168.0.0/16')))
    except ValueError:
        return False


def validate_transport(args):
    if not args.ca and not private_host(args.host, ('mosquitto',)):
        raise ValueError('Public MQTT requires TLS and --ca; no insecure Internet connection')
    url = urllib.parse.urlsplit(args.api)
    if url.scheme not in ('http', 'https') or not url.hostname or url.username or url.password or url.query or url.fragment:
        raise ValueError('Provide an HTTP(S) API base without credentials/query/fragment')
    if url.scheme == 'http' and not private_host(url.hostname, ('api',)):
        raise ValueError('Public API requires HTTPS')


def relay_sample_requests(client, api, sent, clock=time.monotonic):
    """Resend short-lived acquisition requests until persistence; never retained."""
    status, items = request(api, 'GET', '/api/internal/measurement-requests')
    if status == 404:  # Compatible with the previous backend during rollout.
        return
    if status != 200 or not isinstance(items, list) or len(items) > 100:
        raise ValueError('invalid measurement request response')
    now = datetime.now(timezone.utc)
    tick = clock()
    active = set()
    for item in items:
        if not isinstance(item, dict):
            continue
        device, identity = item.get('device_id'), item.get('id')
        if not isinstance(device, str) or not re.fullmatch(r'[A-Za-z0-9_-]{1,64}', device):
            continue
        if not isinstance(identity, str) or not re.fullmatch(r'[0-9a-fA-F]{8}(?:-[0-9a-fA-F]{4}){3}-[0-9a-fA-F]{12}', identity):
            continue
        try:
            expires = datetime.fromisoformat(item['expires_at'].replace('Z', '+00:00'))
            remaining = (expires - now).total_seconds()
        except (ValueError, TypeError, KeyError, AttributeError):
            continue
        if not 0 < remaining <= 35:
            continue
        active.add(identity)
        if tick - sent.get(identity, float('-inf')) < 2:
            continue
        body = json.dumps(dict(action='measure', request_id=identity, expires_at=int(expires.timestamp())))
        result = client.publish(f'hydromate/{device}/commands/measure', body, qos=1, retain=False)
        if result.rc == mqtt.MQTT_ERR_SUCCESS:
            sent[identity] = tick
            log('sample_request_published', device=device, request_id=identity)
    for identity in set(sent) - active:
        del sent[identity]


def run(args):
    validate_transport(args)
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
    last_requests_poll = float('-inf')
    sent_requests = {}

    def ack(device, seq, status):
        client.publish(f'hydromate/{device}/ack', json.dumps(dict(sequence=seq, status=status)), qos=1, retain=False)

    try:
        while True:
            if client.is_connected() and time.monotonic() - last_requests_poll >= 1:
                last_requests_poll = time.monotonic()
                try:
                    relay_sample_requests(client, args.api, sent_requests)
                except (OSError, ValueError) as error:
                    log('sample_requests_unavailable', error_type=type(error).__name__)
                    last_requests_poll += 4
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
                    query = urllib.parse.urlencode(dict(device_id=device, sequence=seq, limit=1))
                    code, rows = request(args.api, 'GET', '/api/measurements?' + query)
                    existing = next((r for r in rows if r['sequence'] == seq), None) if code == 200 and isinstance(rows, list) else None
                    # Conflict is success only if the persisted content is identical.
                    outcome = 'stored' if existing and measurement_matches_payload(existing, payload) else 'conflict'
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
