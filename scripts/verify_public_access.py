"""Read-only HTTPS API + MQTT TLS preflight. Does not publish, deploy or use secrets."""
import argparse
from datetime import datetime, timezone
import json
from pathlib import Path
import socket
import ssl
import urllib.parse
import urllib.request


def run(args):
    url = urllib.parse.urlsplit(args.api.rstrip('/'))
    if url.scheme != 'https' or not url.hostname or url.username or url.password or url.query or url.fragment or url.path:
        raise ValueError('Provide an HTTPS base URL without credentials or /api')
    if args.mqtt_port != 8884:
        raise ValueError('Production MQTT TLS port must be 8884')
    api = args.api.rstrip('/')
    context = ssl.create_default_context(cafile=str(args.api_ca) if args.api_ca else None)
    report = dict(at=datetime.now(timezone.utc).isoformat(), passed=False,
                  scope='Read-only API/TLS check; historical rows are not proof of new physical transmissions',
                  api=api, mqtt_host=args.mqtt_host, mqtt_port=args.mqtt_port)

    class NoRedirect(urllib.request.HTTPRedirectHandler):
        def redirect_request(self, req, fp, code, msg, headers, newurl):
            return None

    opener = urllib.request.build_opener(urllib.request.HTTPSHandler(context=context), NoRedirect())

    def get(path):
        req = urllib.request.Request(api + path, headers={'Accept': 'application/json'})
        with opener.open(req, timeout=10) as response:
            if response.geturl() != api + path:
                raise ValueError('Unexpected redirect; validate the final base URL directly')
            body = response.read(1_000_001)
            if len(body) > 1_000_000:
                raise ValueError('Response exceeds limit')
            return response.status, body

    try:
        code, _ = get('/up')
        assert code == 200
        query = urllib.parse.urlencode(dict(device_id=args.device, real_only=1, limit=20))
        code, body = get('/api/measurements?' + query)
        rows = json.loads(body)
        assert code == 200 and isinstance(rows, list) and len(rows) <= 20
        keys = ['temperature_c', 'light_lux', 'water_present', 'ph', 'tds_ppm', 'ec_us_cm']
        verified = []
        for row in rows:
            assert row['device_id'] == args.device
            assert 'synthetic_test' not in (row.get('reason') or [])
            if row.get('message_version') != 3:
                continue
            sources = row['sources']
            assert set(sources) == set(keys)
            assert all(sources[k] in ('real', 'unavailable', 'invalid') for k in keys)
            assert all((row[k] is None) == (sources[k] in ('unavailable', 'invalid')) for k in keys)
            assert type(row['sequence']) is int and row['sequence'] > 0
            assert row['created_at']
            if any(sources[k] == 'real' for k in keys):
                verified.append(row['sequence'])
        assert len(verified) >= args.min_real_records, 'Not enough v3 rows with declared real readings'
        code, body = get('/api/devices/' + urllib.parse.quote(args.device, safe='') + '/status?real_only=1')
        state = json.loads(body)
        assert code == 200 and state['state'] in ('no_data', 'recent', 'stale')
        mqtt_context = ssl.create_default_context(cafile=str(args.mqtt_ca) if args.mqtt_ca else None)
        with socket.create_connection((args.mqtt_host, args.mqtt_port), timeout=10) as raw:
            with mqtt_context.wrap_socket(raw, server_hostname=args.mqtt_host) as wire:
                report['mqtt_tls_version'] = wire.version()
        report.update(passed=True, api_health=200, verified_v3_sequences=verified, device_state=state['state'],
                      mqtt_scope='Verified certificate chain/hostname and TLS socket; authentication confirmed separately by ESP32/bridge')
    except Exception as error:
        report['error'] = str(error)
    finally:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(report, indent=2), encoding='utf-8')
        print(json.dumps(dict(passed=report['passed'], output=str(args.output))))
    return report['passed']


if __name__ == '__main__':
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--api', required=True)
    p.add_argument('--mqtt-host', required=True)
    p.add_argument('--mqtt-port', type=int, default=8884)
    p.add_argument('--device', default='hydromate-01')
    p.add_argument('--min-real-records', type=int, choices=range(0, 21), default=10)
    p.add_argument('--api-ca', type=Path, help='Optional trusted CA for isolated tests/private PKI; never disables verification')
    p.add_argument('--mqtt-ca', type=Path, help='Trusted MQTT CA; omit for system trusted public CA')
    p.add_argument('--output', type=Path, required=True)
    raise SystemExit(0 if run(p.parse_args()) else 1)
