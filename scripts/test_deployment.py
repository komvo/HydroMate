"""Deployment account/daemon guards, using fake CLI programs and no real secrets."""
import os
from pathlib import Path
import subprocess
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]


@unittest.skipUnless(os.getenv('HYDROMATE_TEST_SHELL'), 'Set HYDROMATE_TEST_SHELL to a POSIX shell')
class RootlessGuardTest(unittest.TestCase):
    def run_guard(self, user='deploy-hydromate', security='["name=rootless"]', docker_status='0'):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / 'id').write_text('#!/bin/sh\ncase "$1" in -un) echo "$MOCK_USER";; -u) echo 1001;; esac\n', encoding='utf-8')
            (root / 'docker').write_text(
                '#!/bin/sh\nprintf "%s|%s" "$DOCKER_HOST" "${DOCKER_CONTEXT-unset}" > "$MOCK_LOG"\n'
                'printf "%s" "$MOCK_SECURITY"\nexit "$MOCK_DOCKER_STATUS"\n', encoding='utf-8')
            for name in ['id', 'docker']:
                (root / name).chmod(0o700)
            env = os.environ | dict(MOCK_USER=user, MOCK_SECURITY=security,
                                     MOCK_DOCKER_STATUS=docker_status, MOCK_LOG=str(root / 'log'),
                                     DOCKER_HOST='unix:///wrong-daemon.sock', DOCKER_CONTEXT='wrong-context')
            result = subprocess.run([os.environ['HYDROMATE_TEST_SHELL'], '-c',
                                     'PATH="$(cd "$1" && pwd):$PATH"; export PATH; . "$2"; echo READY',
                                     'test', str(root), str(ROOT / 'deployment/require-rootless.sh')],
                                    env=env, capture_output=True, text=True)
            log = (root / 'log').read_text() if (root / 'log').exists() else ''
            return result, log

    def test_rootless_selects_own_socket_and_clears_foreign_context(self):
        result, log = self.run_guard()
        self.assertEqual(0, result.returncode, result.stderr)
        self.assertEqual('unix:///run/user/1001/docker.sock|unset', log)
        self.assertIn('READY', result.stdout)

    def test_wrong_account_never_calls_docker(self):
        result, log = self.run_guard(user='root')
        self.assertNotEqual(0, result.returncode)
        self.assertEqual('', log)

    def test_rootful_and_unavailable_daemons_are_rejected(self):
        for security, status in [('["name=seccomp"]', '0'), ('', '1')]:
            result, _ = self.run_guard(security=security, docker_status=status)
            self.assertNotEqual(0, result.returncode)
            self.assertNotIn('READY', result.stdout)


if __name__ == '__main__':
    unittest.main()
