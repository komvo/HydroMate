"""Port validation must fail before contacting any protected/shared service."""
from argparse import Namespace
from unittest.mock import patch
import unittest
from verify_public_access import run


class PublicPortTest(unittest.TestCase):
    def test_rejects_old_and_other_https_ports_without_network_access(self):
        for port in ['', ':443', ':8443', ':8883', ':8884']:
            with self.subTest(port=port), patch('verify_public_access.ssl.create_default_context') as tls:
                with self.assertRaisesRegex(ValueError, 'HTTPS port must be 9443'):
                    run(Namespace(api='https://example.invalid'+port, mqtt_port=8884))
                tls.assert_not_called()

    def test_rejects_changed_mqtt_port_without_network_access(self):
        with patch('verify_public_access.ssl.create_default_context') as tls:
            with self.assertRaisesRegex(ValueError, 'MQTT TLS port must be 8884'):
                run(Namespace(api='https://example.invalid:9443', mqtt_port=8883))
            tls.assert_not_called()


if __name__ == '__main__':
    unittest.main()
