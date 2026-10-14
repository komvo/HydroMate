"""Offline bridge contract checks; no MQTT, VPS or database changes."""
import unittest
from argparse import Namespace
from mqtt_bridge import measurement_matches_payload, validate_transport


class BridgeContractTest(unittest.TestCase):
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
