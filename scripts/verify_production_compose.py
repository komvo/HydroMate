"""Validate production resource isolation using fake values; does not start Docker services."""
import base64
import json
import os
from pathlib import Path
import subprocess


def main():
    root = Path(__file__).resolve().parent.parent
    env = os.environ.copy()
    # Always override required values with test fixtures; never print real config.
    env.update(HYDROMATE_APP_KEY='base64:' + base64.b64encode(b'x' * 32).decode(),
               HYDROMATE_POSTGRES_PASSWORD='validation-admin-only',
               HYDROMATE_DB_PASSWORD='validation-app-only',
               HYDROMATE_DB_DATABASE='hydromate', HYDROMATE_DB_USERNAME='hydromate',
               HYDROMATE_MQTT_SECRETS_DIR=str(root / 'deployment/secrets/mqtt'),
               HYDROMATE_MQTT_BRIDGE_PASSWORD='validation-bridge-only',
               HYDROMATE_MQTT_BIND_ADDRESS='127.0.0.1', HYDROMATE_HTTPS_BIND_ADDRESS='127.0.0.1',
               HYDROMATE_HTTPS_SECRETS_DIR=str(root / 'deployment/secrets/https'),
               HYDROMATE_APP_URL='https://example.invalid:8443')
    result = subprocess.run(['docker', 'compose', '-p', 'hydromate', '-f', str(root / 'compose.production.yml'),
                             '--env-file', str(root / '.env.example'), '--profile', 'mqtt', '--profile', 'public',
                             'config', '--format', 'json'], env=env, capture_output=True, text=True, check=True)
    config = json.loads(result.stdout)
    assert config['name'] == 'hydromate'
    assert set(config['services']) == {'api', 'db', 'mosquitto', 'bridge', 'https'}
    assert config['networks']['database']['internal'] is True
    assert set(config['services']['db']['networks']) == {'database'}
    assert not config['services']['db'].get('ports')
    assert config['services']['api']['ports'][0]['host_ip'] == '127.0.0.1'
    assert str(config['services']['api']['ports'][0]['published']) == '8081'
    assert str(config['services']['mosquitto']['ports'][0]['published']) == '8884'
    assert str(config['services']['https']['ports'][0]['published']) == '8443'
    assert set(config['services']['https']['networks']) == {'application'}
    assert config['services']['api']['environment']['APP_URL'] == 'https://example.invalid:8443'
    for service in config['services'].values():
        assert service.get('network_mode') != 'host'
        assert not service.get('container_name')
        assert not service.get('privileged')
        for port in service.get('ports', []):
            assert int(port['published']) not in {80, 443, 8883, 5432, 1883, 1884}
        for mount in service.get('volumes', []):
            assert 'docker.sock' not in mount['source']
    for kind in ['volumes', 'networks']:
        for resource in config[kind].values():
            assert resource['name'].startswith('hydromate_')
            assert not resource.get('external')
    assert config['services']['api']['environment']['APP_DEBUG'] == 'false'
    print('Production Compose isolation checks passed; no services started, fake credentials only.')


if __name__ == '__main__':
    main()
