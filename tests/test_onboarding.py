"""Offline onboarding regression checks; no browser packages or external calls."""
from pathlib import Path
import shutil
import subprocess
import unittest
from html.parser import HTMLParser

ROOT = Path(__file__).resolve().parents[1]


class OnboardingTests(unittest.TestCase):
    def test_interactive_simulation(self):
        self.assertIsNotNone(shutil.which('node'), 'Node.js is required for web regression tests')
        subprocess.run(['node', 'tests/onboarding_test.js'], cwd=ROOT, check=True)

    def test_accessible_local_only_markup(self):
        class Markup(HTMLParser):
            def __init__(self):
                super().__init__()
                self.nodes = {}

            def handle_starttag(self, tag, attrs):
                attrs = dict(attrs)
                if attrs.get('id', '').startswith('onboarding-'):
                    self.nodes[attrs['id']] = (tag, attrs)

        parser = Markup()
        html = (ROOT / 'web/index.html').read_text()
        parser.feed(html)
        nodes = parser.nodes
        self.assertEqual(nodes['onboarding-progress'][1]['role'], 'status')
        self.assertEqual(nodes['onboarding-step'][1]['tabindex'], '-1')
        self.assertEqual(nodes['onboarding-flow'][1]['aria-describedby'], 'onboarding-notice')
        for name in ('back', 'next', 'reset'):
            self.assertEqual(nodes['onboarding-' + name][0], 'button')
            self.assertEqual(nodes['onboarding-' + name][1]['type'], 'button')
        self.assertIn('SIMULATION_ONLY — local demo', html)
        self.assertIn('<noscript>', html)

    def test_handlers_fail_closed_without_network(self):
        from unittest.mock import patch
        from backend.nayvelo.server import Handler, SIMULATION_ONLY
        self.assertTrue(SIMULATION_ONLY)
        for path in ('/api/v1/register', '/api/v1/subscribers', '/api/v1/provision',
                     '/api/v1/esim/issue', '/api/v1/activate', '/api/v1/payments'):
            for method in ('GET', 'POST', 'PUT', 'PATCH', 'DELETE'):
                with self.subTest(path=path, method=method):
                    handler = Handler.__new__(Handler)
                    handler.path = path + '?simulation=false'
                    with patch.object(handler, '_json') as reply, patch('socket.socket', side_effect=AssertionError('Outbound socket forbidden')):
                        getattr(handler, 'do_' + method)()
                    self.assertEqual(reply.call_args.args[0], 403)
