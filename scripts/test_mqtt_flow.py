"""Synthetic MQTT/API integration evidence. Never claims physical sensor readings."""
import argparse
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import queue
import time
import urllib.parse
import uuid
import paho.mqtt.client as mqtt
from mqtt_bridge import request, validate_transport


def run(args):
    validate_transport(args)
    device = args.device or 'test-mqtt-' + uuid.uuid4().hex[:10]
    replies = queue.Queue()
    ready = queue.Queue()
    client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
    if os.getenv('MQTT_USERNAME'):
        client.username_pw_set(os.environ['MQTT_USERNAME'], os.getenv('MQTT_PASSWORD'))
    if args.ca:
        client.tls_set(ca_certs=str(args.ca))
    def connected(c, u, f, code, props):
        c.subscribe(f'hydromate/{device}/ack', 1)
    def subscribed(c, u, mid, codes, props):
        ready.put(True)
    client.on_connect = connected
    client.on_subscribe = subscribed
    client.on_message = lambda c, u, msg: replies.put(json.loads(msg.payload))
    client.connect(args.host, args.port)
    client.loop_start()
    events = []
    passed = False
    first = int(time.time()) if args.device else 1
    payload = dict(message_version=3, device_id=device, sequence=first, reason=['synthetic_test'],
                   captured_at=datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ'),
                   temperature_c=24.3, ph=6.2, tds_ppm=None, ec_us_cm=None, light_lux=450.5, water_present=False,
                   sources={k:'simulated' for k in ['temperature_c','ph','light_lux','water_present']} |
                           dict(tds_ppm='unavailable', ec_us_cm='unavailable'))
    def send(value, expected):
        start = time.perf_counter()
        client.publish(f'hydromate/{device}/telemetry', json.dumps(value), qos=1).wait_for_publish(5)
        deadline = time.monotonic()+20
        while True:
            try:
                ack = replies.get(timeout=min(2, max(.01, deadline-time.monotonic())))
            except queue.Empty:
                if time.monotonic() >= deadline:
                    raise TimeoutError('No persistence ACK within 20 seconds')
                # Same object and sequence: model the ESP32 retry, never invent a new reading.
                client.publish(f'hydromate/{device}/telemetry', json.dumps(value), qos=1).wait_for_publish(5)
                continue
            if ack['sequence'] == value['sequence']:
                break
        events.append(dict(sequence=value['sequence'], expected=expected, ack=ack['status'],
                           mqtt_to_persistence_ack_ms=round((time.perf_counter()-start)*1000,2)))
        assert ack['status'] == expected, ack
    try:
        ready.get(timeout=8)
        for seq in range(first,first+10):
            send(payload | {'sequence':seq}, 'stored')
        send(payload, 'stored')
        send(payload | {'ph':7}, 'conflict')
        send(payload | {'sequence':first+10, 'ph':50}, 'rejected')
        code, history = request(args.api, 'GET', '/api/measurements?' + urllib.parse.urlencode(dict(device_id=device,limit=20)))
        assert code == 200
        history = [r for r in history if first <= r['sequence'] < first+10]
        assert len(history) == 10
        assert {r['sequence'] for r in history} == set(range(first,first+10))
        assert all(r['tds_ppm'] is None and r['sources']['tds_ppm'] == 'unavailable' for r in history)
        if args.response_output:
            args.response_output.parent.mkdir(parents=True, exist_ok=True)
            args.response_output.write_text(json.dumps(history, indent=2), encoding='utf-8')
        passed = True
    finally:
        client.disconnect(); client.loop_stop()
        report = dict(at=datetime.now(timezone.utc).isoformat(), device_id=device, synthetic=True,
                      passed=passed, scope='PC producer -> Mosquitto -> bridge -> Laravel -> PostgreSQL; API GET checked; excludes sensor and Android display latency', events=events)
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(report, indent=2), encoding='utf-8')
        print(json.dumps(dict(passed=passed, device_id=device, output=str(args.output))))

if __name__ == '__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--host',default='127.0.0.1')
    parser.add_argument('--port',type=int,default=1883)
    parser.add_argument('--api',default='http://127.0.0.1:8000')
    parser.add_argument('--ca',type=Path,help='Trusted CA for MQTT TLS; never disables verification')
    parser.add_argument('--device',help='Only for an isolated test stack with a restricted test ACL; messages remain synthetic')
    parser.add_argument('--response-output',type=Path,help='API response fixture for the Android parser test')
    parser.add_argument('--output',type=Path,required=True)
    run(parser.parse_args())
