import json
import threading
import unittest
from http import HTTPStatus
from http.server import ThreadingHTTPServer
from urllib.error import HTTPError
from urllib.request import Request, urlopen

from backend.nayvelo.catalog import get_plans
from backend.nayvelo.server import Handler, SIMULATION_ONLY


class APIContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.server = ThreadingHTTPServer(('127.0.0.1', 0), Handler)
        cls.thread = threading.Thread(target=cls.server.serve_forever, daemon=True)
        cls.thread.start()
        cls.base = 'http://127.0.0.1:' + str(cls.server.server_address[1])

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()
        cls.server.server_close()
        cls.thread.join(timeout=3)

    def request(self, path, method='GET'):
        request = Request(self.base + path, data=(b'{}' if method != 'GET' else None), method=method)
        try:
            with urlopen(request,timeout=3) as response:
                return response.status, json.loads(response.read()) if path.startswith('/api/') else None
        except HTTPError as exc:
            return exc.code, json.loads(exc.read())

    def test_simulation_mode(self):
        self.assertTrue(SIMULATION_ONLY)
        status, health = self.request('/api/v1/health')
        self.assertEqual(status, HTTPStatus.OK)
        self.assertEqual(health['mode'], 'SIMULATION_ONLY')
        self.assertFalse(health['liveActivationEnabled'])
        self.assertFalse(health['paymentsEnabled'])

    def test_all_plans_unpriced_unavailable(self):
        status, data = self.request('/api/v1/plans')
        self.assertEqual(status, 200)
        self.assertEqual(data['plans'], get_plans())
        self.assertGreaterEqual(len(data['plans']), 5)
        for plan in data['plans']:
            self.assertIsNone(plan['price_ngn'])
            self.assertFalse(plan['available_for_purchase'])

    def test_all_writes_fail_closed(self):
        for method in ('POST', 'PUT', 'PATCH', 'DELETE'):
            for path in ('/api/v1/activate','/api/v1/payments','/api/v1/subscribers'):
                with self.subTest(method=method, path=path):
                    status, data = self.request(path, method)
                    self.assertEqual(status, HTTPStatus.FORBIDDEN)
                    self.assertEqual(data['error'], 'SIMULATION_ONLY')

    def test_sensitive_routes_not_available_even_on_get(self):
        for path in ('/api/v1/activate','/api/v1/esim/issue','/api/v1/kyc','/api/v1/payments','/api/v1/provision','/api/v1/subscribe','/api/v1/register','/api/v1/sms/send','/api/v1/subscribers','/api/v1/register/complete?live=true','/api/v1/provision/activate'):
            with self.subTest(path=path):
                status, _ = self.request(path)
                self.assertEqual(status, 403)

    def test_onboarding_cannot_register_or_activate(self):
        for path in ('/api/v1/register', '/api/v1/subscribers', '/api/v1/onboarding',
                     '/api/v1/activate', '/api/v1/provision', '/api/v1/esim/issue'):
            for method in ('POST', 'PUT', 'PATCH', 'DELETE'):
                with self.subTest(path=path, method=method):
                    status, data = self.request(path + '?simulation=false', method)
                    self.assertEqual(status, 403)
                    self.assertEqual(data['error'], 'SIMULATION_ONLY')
        with urlopen(self.base + '/onboarding.js', timeout=3) as response:
            self.assertEqual(response.status, 200)
            self.assertIn("form-action 'none'", response.headers['Content-Security-Policy'])

    def test_readiness_is_not_verification(self):
        status, data = self.request('/api/v1/esim-readiness')
        self.assertEqual(status, 200)
        self.assertFalse(data['compatibilityVerified'])

    def test_web_home_served_with_security_headers(self):
        with urlopen(self.base + '/', timeout=3) as response:
            html = response.read().decode('utf-8')
            self.assertEqual(response.status, 200)
            self.assertIn('Mobile,', html)
            self.assertIn('Content-Security-Policy', response.headers)
            self.assertEqual(response.headers['X-Frame-Options'], 'DENY')

    def test_unknown_endpoint_returns_404(self):
        status, _ = self.request('/api/v1/unknown')
        self.assertEqual(status, 404)


if __name__ == '__main__':
    unittest.main()
