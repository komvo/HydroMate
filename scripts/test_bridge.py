"""Offline bridge contract checks; no MQTT, VPS or database changes."""
import unittest
from unittest.mock import patch, Mock
from datetime import datetime, timezone, timedelta
from argparse import Namespace
from mqtt_bridge import measurement_matches_payload, validate_transport, relay_sample_requests


class BridgeContractTest(unittest.TestCase):
    def test_sample_requests_use_specific_non_retained_topic_and_expire(self):
        identity = '12345678-1234-1234-1234-123456789abc'
        item = dict(id=identity, device_id='hydromate-01',
                    expires_at=(datetime.now(timezone.utc)+timedelta(seconds=25)).isoformat())
        client = Mock()
        client.publish.return_value.rc = 0
        sent = {}
        with patch('mqtt_bridge.request', return_value=(200, [item])):
            relay_sample_requests(client, 'http://api:8080', sent, clock=lambda: 10)
            relay_sample_requests(client, 'http://api:8080', sent, clock=lambda: 11)
        self.assertEqual(client.publish.call_count, 1)
        args, kwargs = client.publish.call_args
        self.assertEqual(args[0], 'hydromate/hydromate-01/commands/measure')
        self.assertEqual(kwargs, dict(qos=1, retain=False))
        item['expires_at'] = (datetime.now(timezone.utc)-timedelta(seconds=1)).isoformat()
        with patch('mqtt_bridge.request', return_value=(200, [item])):
            relay_sample_requests(client, 'http://api:8080', sent, clock=lambda: 15)
        self.assertEqual(client.publish.call_count, 1)
        self.assertFalse(sent)

    def test_sampling_rejects_topic_injection_and_survives_previous_backend(self):
        client = Mock()
        with patch('mqtt_bridge.request', return_value=(200, [dict(id='x', device_id='other/commands', expires_at='x')])):
            relay_sample_requests(client, 'http://api:8080', {})
        with patch('mqtt_bridge.request', return_value=(404, {})):
            relay_sample_requests(client, 'http://api:8080', {})
        client.publish.assert_not_called()

    def test_datetime_serialization_and_nulls_are_equivalent(self):
        payload = dict(captured_at='2026-10-14T19:00:00Z', ph=None, water_present=False)
        row = payload | dict(captured_at='2026-10-14T19:00:00.000000Z', id=123)
        self.assertTrue(measurement_matches_payload(row, payload))
        self.assertFalse(measurement_matches_payload(row | dict(ph=0), payload))
        self.assertFalse(measurement_matches_payload(row | dict(captured_at='2026-10-14T19:00:01Z'), payload))

    def test_public_mqtt_requires_tls_and_public_api_https(self):
        for host, api in [('broker.example.org', 'https://api.example.org'), ('mosquitto', 'http://api.example.org')]:
            with self.assertRaises(ValueError):
                validate_transport(Namespace(host=host, api=api, ca=None))
        validate_transport(Namespace(host='broker.example.org', api='https://api.example.org', ca='private-ca.pem'))
        validate_transport(Namespace(host='mosquitto', api='http://api:8080', ca=None))
        validate_transport(Namespace(host='192.168.1.20', api='http://127.0.0.1:8000', ca=None))

    def test_credentials_in_api_url_are_rejected(self):
        with self.assertRaises(ValueError):
            validate_transport(Namespace(host='localhost', api='https://user:password@example.org', ca=None))


if __name__ == '__main__':
    unittest.main()
