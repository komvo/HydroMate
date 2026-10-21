"""Synthetic end-to-end fixture, restricted to the local hydromate-validation stack.

Never targets the VPS. Uses private local test.env and local test certificates;
does not print credentials or delete database/volume contents.
"""
from datetime import datetime, timezone
import json
from pathlib import Path
import queue
import ssl
import subprocess
import time
import urllib.error
import urllib.request

import paho.mqtt.client as mqtt


def main():
    root = Path(__file__).resolve().parent.parent
    fixtures = root / '.local/realtime-validation'
    compose = ['docker', 'compose', '-p', 'hydromate-validation', '-f',
               str(root / 'compose.production.yml'), '--env-file', str(fixtures / 'test.env'),
               '--profile', 'mqtt', '--profile', 'public']
    config = json.loads(subprocess.check_output(compose + ['config', '--format', 'json']))
    assert config['name'] == 'hydromate-validation'
    for name in ('https', 'mosquitto'):
        assert all(port['host_ip'] == '127.0.0.1' for port in config['services'][name]['ports'])
    context = ssl.create_default_context(cafile=str(fixtures / 'https/fullchain.pem'))

    def api(path, method='GET', body=None):
        data = json.dumps(body).encode() if body is not None else None
        req = urllib.request.Request('https://localhost:9443' + path, data=data, method=method,
            headers={'Accept': 'application/json', 'Content-Type': 'application/json'})
        try:
            response = urllib.request.urlopen(req, context=context, timeout=8)
        except urllib.error.HTTPError as error:
            response = error
        with response:
            content = response.read()
            return response.status, json.loads(content) if content.startswith((b'{', b'[')) else None

    # Existing local fixtures use the same fictional password for both test accounts.
    password = config['services']['bridge']['environment']['MQTT_PASSWORD']
    commands, acknowledgements = queue.Queue(), queue.Queue()
    client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, client_id='hydromate-validation-acquisition')
    client.username_pw_set('hydromate-device', password)
    client.tls_set(ca_certs=str(fixtures / 'mqtt/fullchain.pem'))
    def connected(c, userdata, flags, reason, properties):
        assert reason == 0, 'Local fixture MQTT authentication failed'
        c.subscribe([('hydromate/hydromate-01/commands/measure', 1), ('hydromate/hydromate-01/ack', 1)])
    def message(c, userdata, msg):
        (commands if msg.topic.endswith('/commands/measure') else acknowledgements).put(
            (json.loads(msg.payload), msg.retain))
    client.on_connect, client.on_message = connected, message
    client.connect('localhost', 8884)
    client.loop_start()
    sequence = int(time.time() * 1000)

    def publish(number, reasons):
        # Real-format values test validation/correlation in an isolated fixture DB.
        # They are generated data and never evidence of a physical sensor.
        payload = dict(message_version=3, device_id='hydromate-01', sequence=number,
            reason=['fixture_realtime_validation'] + reasons, temperature_c=24.5, ph=6.2,
            tds_ppm=367.47, light_lux=180, water_present=True, ec_us_cm=None,
            captured_at=datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ'),
            sources={key: 'real' for key in ('temperature_c', 'ph', 'tds_ppm', 'light_lux', 'water_present')}
                    | {'ec_us_cm': 'unavailable'})
        client.publish('hydromate/hydromate-01/telemetry', json.dumps(payload), qos=1).wait_for_publish()
        deadline = time.monotonic() + 15
        while time.monotonic() < deadline:
            ack, retained = acknowledgements.get(timeout=15)
            if ack.get('sequence') == number:
                assert ack.get('status') == 'stored' and not retained, ack
                return
        raise AssertionError('Missing persistence ACK')

    try:
        time.sleep(1)
        publish(sequence, ['periodic_poc'])
        status, request = api('/api/devices/hydromate-01/measurement-requests', 'POST', {})
        assert status == 202, (status, request)
        identity = request['id']
        path = '/api/measurement-requests/' + identity
        assert api(path)[1]['state'] == 'pending', 'Old measurement fulfilled a fresh request'
        command, retained = commands.get(timeout=10)
        assert command['request_id'] == identity and command['action'] == 'measure' and not retained
        publish(sequence + 1, ['requested', 'request:' + identity])
        result = api(path)[1]
        assert result['state'] == 'stored' and result['measurement']['sequence'] == sequence + 1
        status, rows = api('/api/measurements?device_id=hydromate-01&limit=20&real_only=1')
        assert status == 200 and any(row['sequence'] == sequence + 1 and row['tds_ppm'] == 367.47 for row in rows)
        assert api('/api/internal/measurement-requests')[0] == 404
        assert api('/api/measurements', 'POST', {})[0] == 403
        assert api('/api/devices/hydromate-01/measurement-requests', 'POST', {'action': 'pump'})[0] == 422
        _, waiting = api('/api/devices/hydromate-01/measurement-requests', 'POST', {})
        time.sleep(31)
        assert api('/api/measurement-requests/' + waiting['id'])[1]['state'] == 'expired'
        print('PASS: local HTTPS -> request UUID -> MQTT TLS command -> simulated ESP -> bridge -> PostgreSQL -> GET; timeout and public boundary verified. Synthetic fixture only.')
    finally:
        client.disconnect()
        client.loop_stop()


if __name__ == '__main__':
    main()
