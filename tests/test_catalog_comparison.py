"""NAY-003: offline catalog integrity, web serving and blocked writes."""
import copy
import json
import shutil
import subprocess
import threading
import unittest
from http.server import ThreadingHTTPServer
from pathlib import Path
from urllib.error import HTTPError
from urllib.request import Request, urlopen

from backend.nayvelo.catalog import get_plans, validate_catalog_data, CATALOG
from backend.nayvelo.server import Handler, SIMULATION_ONLY

ROOT = Path(__file__).resolve().parents[1]


class CatalogComparisonTests(unittest.TestCase):
    def test_one_source_for_api_and_flutter(self):
        canonical = CATALOG.read_bytes()
        self.assertEqual(canonical, (ROOT / 'apps/customer_app/assets/plans.json').read_bytes())
        data = json.loads(canonical)
        self.assertEqual(data['mode'], 'SIMULATION_ONLY')
        self.assertGreaterEqual(len(get_plans()), 6)
        self.assertEqual(data['plans'], get_plans())

    def test_every_allowance_unconfirmed_and_purchase_disabled(self):
        for p in get_plans():
            with self.subTest(code=p['code']):
                for key in ('data_gb', 'voice_minutes', 'sms_count', 'price_ngn'):
                    self.assertIsNone(p[key])
                self.assertIs(p['available_for_purchase'], False)
                self.assertEqual(p['hotspot'], 'Not confirmed')
                self.assertEqual(p['rollover'], 'Not confirmed')

    def test_malformed_or_commercial_data_rejected(self):
        source = json.loads(CATALOG.read_text())
        bad_cases = []
        for field, value in [('data_gb', 5), ('voice_minutes', 100), ('price_ngn', 1000), ('available_for_purchase', True), ('sms_count', 10), ('hotspot', 'Included')]:
            other = copy.deepcopy(source)
            other['plans'][0][field] = value
            bad_cases.append(other)
        other = copy.deepcopy(source)
        other['mode'] = 'LIVE'
        bad_cases.append(other)
        other = copy.deepcopy(source)
        other['plans'].append(copy.deepcopy(other['plans'][0]))
        bad_cases.append(other)
        for bad in bad_cases:
            with self.subTest(bad=bad['plans'][0]['code']):
                with self.assertRaises(ValueError):
                    validate_catalog_data(bad)

    def test_web_assets_and_api_are_local_read_only(self):
        self.assertTrue(SIMULATION_ONLY)
        server = ThreadingHTTPServer(('127.0.0.1', 0), Handler)
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        base = f'http://127.0.0.1:{server.server_address[1]}'
        try:
            for route in ('/plan_compare.js', '/plan_compare.css'):
                with urlopen(base + route, timeout=3) as response:
                    self.assertEqual(response.status, 200)
                    self.assertTrue(response.read())
            with urlopen(base + '/api/v1/plans', timeout=3) as response:
                result = json.load(response)
                self.assertEqual(result['plans'], get_plans())
            for path in ('/api/v1/payments', '/api/v1/subscribe', '/api/v1/esim/issue'):
                for method in ('GET', 'POST'):
                    req = Request(base + path, method=method, data=(b'{}' if method == 'POST' else None))
                    with self.subTest(path=path, method=method):
                        with self.assertRaises(HTTPError) as error:
                            urlopen(req, timeout=3)
                        with error.exception as response:
                            self.assertEqual(response.code, 403)
        finally:
            server.shutdown(); server.server_close(); thread.join(timeout=3)

    @unittest.skipUnless(shutil.which('node'), 'Node.js not installed')
    def test_browser_filter_and_comparison_logic(self):
        subprocess.run(['node', 'tests/plan_compare_test.cjs'], cwd=ROOT, check=True)

    def test_web_has_accessible_filters_and_disclaimer(self):
        page = (ROOT / 'web/index.html').read_text()
        for marker in ('id="plan-period"', 'id="plan-compare"', 'id="plan-selection"', 'id="plan-compare-output"', 'plan_compare.js'):
            self.assertIn(marker, page)
        js = (ROOT / 'web/plan_compare.js').read_text()
        self.assertNotIn("fetch('/api/v1/payments", js)
        self.assertNotIn("fetch('/api/v1/subscribe", js)
        self.assertIn("textContent", js)


if __name__ == '__main__':
    unittest.main()
