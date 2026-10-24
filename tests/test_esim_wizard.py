"""NAY-004 simulator-safe eSIM guidance contract tests."""
import json
import shutil
import subprocess
import unittest
from pathlib import Path
from backend.nayvelo.server import SIMULATION_ONLY, STATIC_FILES, BLOCKED_PREFIXES

ROOT = Path(__file__).resolve().parents[1]

class EsimReadinessTests(unittest.TestCase):
    def test_web_accessibility_and_in_memory_state(self):
        html = (ROOT / 'web/index.html').read_text(encoding='utf8')
        js = (ROOT / 'web/esim_wizard.js').read_text(encoding='utf8')
        css = (ROOT / 'web/esim_wizard.css').read_text(encoding='utf8')
        for part in ('id="esim-wizard"', 'data-wizard-panel', 'data-wizard-progress',
                     'data-wizard-next', 'data-wizard-back', 'data-wizard-reset',
                     'data-wizard-status', 'aria-live="polite"', 'type="button"'):
            self.assertIn(part, html)
        self.assertIn('SIMULATION_ONLY', (ROOT / 'backend/nayvelo/server.py').read_text())
        self.assertIn('legend', js)
        self.assertIn('focus()', js)
        self.assertIn(':focus-visible', css)
        for marker in ('IMEI', 'EID', 'NIN'):
            self.assertIn(marker, html + js)
        self.assertNotIn('type="text"', html[html.index('id="esim-wizard"'):html.index('data-wizard-status')])
        for phrase in ('fetch(', 'localStorage', 'sessionStorage', 'navigator.sendBeacon', 'XMLHttpRequest'):
            self.assertNotIn(phrase, js)

    def test_only_local_static_assets_and_simulated_api(self):
        self.assertTrue(SIMULATION_ONLY)
        self.assertEqual(STATIC_FILES['/esim_wizard.js'][0], 'esim_wizard.js')
        self.assertEqual(STATIC_FILES['/esim_wizard.css'][0], 'esim_wizard.css')
        self.assertIn('/api/v1/esim', BLOCKED_PREFIXES)
        server_source = (ROOT / 'backend/nayvelo/server.py').read_text()
        self.assertIn("'compatibilityVerified':False", server_source)
        self.assertIn("def do_POST", server_source)
        self.assertIn('HTTPStatus.FORBIDDEN', server_source)

    def test_flutter_educational_only(self):
        dart = (ROOT / 'apps/customer_app/lib/esim_readiness_wizard.dart').read_text(encoding='utf8')
        main = (ROOT / 'apps/customer_app/lib/main.dart').read_text(encoding='utf8')
        self.assertIn('EsimReadinessWizard()', main)
        self.assertIn('Carrier verification is still required', dart)
        self.assertNotIn('package:http', dart)
        self.assertNotIn('MethodChannel', dart)
        self.assertNotIn('image_picker', dart)
        self.assertIn('Restart guide', dart)

    def test_js_behavior_if_node_is_available(self):
        if not shutil.which('node'):
            self.skipTest('Node.js unavailable; Python static safety checks executed')
        subprocess.run(['node', 'tests/esim_wizard_test.cjs'], cwd=ROOT,
                       check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=15)

if __name__ == '__main__':
    unittest.main()
