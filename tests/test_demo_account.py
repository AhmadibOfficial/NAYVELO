"""NAY-005 memory-only accounts and fail-closed API regression."""
from __future__ import annotations

import json
import unittest
import shutil
import subprocess
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch
import backend.nayvelo.demo_account as domain
from urllib.error import HTTPError
from urllib.request import Request, urlopen
from http.server import ThreadingHTTPServer
from threading import Thread

from backend.nayvelo.demo_account import DemoAccount, InvalidDemoAction, policy
from backend.nayvelo.server import Handler

ROOT = Path(__file__).resolve().parents[1]


class DemoAccountTests(unittest.TestCase):
    def test_policy_contains_no_identity_and_has_safe_defaults(self):
        data = policy()
        self.assertTrue(data['simulationOnly'])
        self.assertEqual(data['persistence'], 'memory_only')
        self.assertFalse(data['personalDataCollected'])
        self.assertEqual(set(data['optionalPrivacyDefaults'].values()), {False})
        self.assertEqual([p['alias'] for p in data['profiles']], ['DEMO-ALPHA', 'DEMO-BETA'])
        serialized = (ROOT / 'shared/demo_accounts.json').read_text()
        for word in ('"nin"', '"imei"', '"eid"', '"email"', '"phone"', '"password"', '"token"'):
            self.assertNotIn(word, serialized.lower())

    def test_extra_identity_field_fails_closed(self):
        data = policy()
        data['nin'] = 'no-real-value'
        with TemporaryDirectory() as directory:
            poisoned = Path(directory) / 'policy.json'
            poisoned.write_text(json.dumps(data))
            with patch.object(domain, 'POLICY_PATH', poisoned):
                with self.assertRaises(InvalidDemoAction):
                    domain.policy()
        data = policy()
        data['profiles'][0]['phone'] = 'not-an-actual-number'
        with TemporaryDirectory() as directory:
            poisoned = Path(directory) / 'policy.json'
            poisoned.write_text(json.dumps(data))
            with patch.object(domain, 'POLICY_PATH', poisoned):
                with self.assertRaises(InvalidDemoAction):
                    domain.policy()

    def test_isolation_and_reset(self):
        a, b = DemoAccount('DEMO-ALPHA'), DemoAccount('DEMO-ALPHA')
        a.set_privacy('productAnalytics', True)
        a.transition('paused')
        self.assertFalse(b.privacy['productAnalytics'])
        self.assertEqual(b.state, 'preview')
        a.reset()
        self.assertEqual(a.state, 'preview')
        self.assertFalse(any(a.privacy.values()))
        self.assertIs(a.public_view()['saved'], False)

    def test_rejects_unknown_actions_and_terminal_recovery(self):
        a = DemoAccount('DEMO-ALPHA')
        with self.assertRaises(InvalidDemoAction):
            a.transition('activated')
        with self.assertRaises(InvalidDemoAction):
            a.transition('preview')
        with self.assertRaises(InvalidDemoAction):
            a.set_privacy('tracking', True)
        with self.assertRaises(InvalidDemoAction):
            a.set_privacy('productNews', 'yes')
        a.transition('locked')
        with self.assertRaises(InvalidDemoAction):
            a.transition('preview')
        with self.assertRaises(InvalidDemoAction):
            DemoAccount('REAL-USER')

    def test_browser_logic_when_node_available(self):
        if not shutil.which('node'):
            self.skipTest('Node.js not available in this runner')
        subprocess.run(['node', 'tests/account_lab_test.cjs'], cwd=ROOT, check=True, timeout=10,
                       stdout=subprocess.DEVNULL)

    def test_web_assets_read_only_account_routes_blocked(self):
        server = ThreadingHTTPServer(('127.0.0.1', 0), Handler)
        thread = Thread(target=server.serve_forever, daemon=True)
        thread.start()
        base = f'http://127.0.0.1:{server.server_port}'
        try:
            for path in ('/account_lab.js','/account_lab.css'):
                with urlopen(base+path, timeout=3) as response:
                    self.assertEqual(response.status, 200)
                    self.assertEqual(response.headers.get('Cache-Control'), 'no-store')
            for path in ('/api/v1/accounts','/api/v1/subscribers','/api/v1/login',
                         '/api/v1/sessions','/api/v1/recovery','/api/v1/sim-swap',
                         '/api/v1/register','/api/v1/esim','/api/v1/payments'):
                for method in ('GET','POST'):
                    with self.subTest(path=path, method=method):
                        try:
                            with urlopen(Request(base+path,method=method,data=b'{}' if method=='POST' else None),timeout=3):
                                self.fail('Live subscriber/auth route unexpectedly allowed')
                        except HTTPError as err:
                            self.assertEqual(err.code, 403)
                            err.close()
        finally:
            server.shutdown()
            server.server_close()
            thread.join(timeout=3)


if __name__ == '__main__':
    unittest.main()
