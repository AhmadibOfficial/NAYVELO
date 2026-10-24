"""Local development server ONLY: never a production telecommunications service."""
from __future__ import annotations

import json
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlsplit

from .catalog import get_plans
from .billing_sandbox import get_fixture
from .admin_intelligence import load_fixture as get_admin_demo

ROOT = Path(__file__).resolve().parents[2]
WEB = ROOT / 'web'
STATIC_FILES = {
    '/admin_dashboard.js': ('admin_dashboard.js', 'application/javascript; charset=utf-8'),
    '/admin_dashboard.css': ('admin_dashboard.css', 'text/css; charset=utf-8'),
    '/billing_sandbox.js': ('billing_sandbox.js', 'application/javascript; charset=utf-8'),
    '/billing_sandbox.css': ('billing_sandbox.css', 'text/css; charset=utf-8'),
    '/account_lab.js': ('account_lab.js', 'application/javascript; charset=utf-8'),
    '/account_lab.css': ('account_lab.css', 'text/css; charset=utf-8'),
    '/esim_wizard.js': ('esim_wizard.js', 'application/javascript; charset=utf-8'),
    '/esim_wizard.css': ('esim_wizard.css', 'text/css; charset=utf-8'),
    '/plan_compare.js': ('plan_compare.js', 'application/javascript; charset=utf-8'),
    '/plan_compare.css': ('plan_compare.css', 'text/css; charset=utf-8'),
    '/': ('index.html', 'text/html; charset=utf-8'),
    '/index.html': ('index.html', 'text/html; charset=utf-8'),
    '/styles.css': ('styles.css', 'text/css; charset=utf-8'),
    '/onboarding.js': ('onboarding.js', 'application/javascript; charset=utf-8'),
    '/app.js': ('app.js', 'application/javascript; charset=utf-8'),
}
SIMULATION_ONLY = True
BLOCKED_PREFIXES = ('/api/v1/subscribers', '/api/v1/activate', '/api/v1/esim', '/api/v1/payments', '/api/v1/register', '/api/v1/kyc', '/api/v1/provision', '/api/v1/subscribe', '/api/v1/voice', '/api/v1/sms', '/api/v1/accounts', '/api/v1/subscribers', '/api/v1/login', '/api/v1/sessions', '/api/v1/recovery', '/api/v1/sim-swap', '/api/v1/otp', '/api/v1/reset-password', '/api/v1/billing', '/api/v1/usage', '/api/v1/transactions', '/api/v1/invoices', '/api/v1/checkout', '/api/v1/wallet', '/api/v1/topup', '/api/v1/recharge', '/api/v1/renew', '/api/v1/admin', '/api/v1/metrics', '/api/v1/audit', '/api/v1/exports', '/api/v1/subscriber-admin', '/api/v1/provisioning', '/api/v1/telemetry', '/api/v1/admin-sessions', '/api/v1/analytics-live')


class Handler(BaseHTTPRequestHandler):
    def _headers(self, code: int, typ: str, size: int) -> None:
        self.send_response(code)
        self.send_header('Content-Type', typ)
        self.send_header('Content-Length', str(size))
        self.send_header('X-Content-Type-Options', 'nosniff')
        self.send_header('X-Frame-Options', 'DENY')
        self.send_header('Referrer-Policy', 'no-referrer')
        self.send_header('Cache-Control', 'no-store')
        self.send_header('Content-Security-Policy', "default-src 'self'; script-src 'self'; style-src 'self'; img-src 'self' data:; connect-src 'self'; object-src 'none'; base-uri 'none'; form-action 'none'; frame-ancestors 'none'")
        self.end_headers()

    def _json(self, code: int, data: dict | list) -> None:
        body = json.dumps(data, separators=(',', ':')).encode('utf-8')
        self._headers(code, 'application/json; charset=utf-8', len(body))
        self.wfile.write(body)

    def _blocked(self, path: str) -> bool:
        return any(path == p or path.startswith(p + '/') for p in BLOCKED_PREFIXES)

    def do_GET(self) -> None:  # noqa: N802
        path = urlsplit(self.path).path
        if self._blocked(path):
            return self._json(HTTPStatus.FORBIDDEN, {'error':'NOT_AVAILABLE','message':'NAYVELO is a simulation. Live telecom services and payments are disabled.'})
        if path == '/api/v1/demo-admin':
            return self._json(HTTPStatus.OK, get_admin_demo())
        if path == '/api/v1/demo-usage':
            return self._json(HTTPStatus.OK, get_fixture())
        if path == '/api/v1/health':
            return self._json(HTTPStatus.OK, {'service':'nayvelo-simulator','mode':'SIMULATION_ONLY','liveActivationEnabled':False,'paymentsEnabled':False})
        if path == '/api/v1/plans':
            return self._json(HTTPStatus.OK, {'plans':get_plans(), 'disclaimer':'Concept plans; no prices or real service available.'})
        if path == '/api/v1/esim-readiness':
            return self._json(HTTPStatus.OK, {'compatibilityVerified':False,'guidance':['Look for Add eSIM or Add mobile plan in your phone settings','Confirm device unlock and eSIM eligibility with your phone maker and future licensed carrier','No device or subscriber ID is collected by this demo']})
        item = STATIC_FILES.get(path)
        if item:
            filename, typ = item
            body = (WEB / filename).read_bytes()
            self._headers(HTTPStatus.OK, typ, len(body))
            return self.wfile.write(body)
        return self._json(HTTPStatus.NOT_FOUND, {'error':'NOT_FOUND'})

    def do_POST(self) -> None:  # noqa: N802
        return self._json(HTTPStatus.FORBIDDEN, {'error':'SIMULATION_ONLY','message':'This prototype cannot create subscribers, charge payments or activate network service.'})

    def do_PUT(self) -> None:  # noqa: N802
        return self.do_POST()

    def do_PATCH(self) -> None:  # noqa: N802
        return self.do_POST()

    def do_DELETE(self) -> None:  # noqa: N802
        return self.do_POST()

    def log_message(self, format: str, *args) -> None:
        # Avoid logging untrusted paths/query strings containing accidental sensitive data.
        pass


def main() -> None:
    print('NAYVELO prototype at http://127.0.0.1:8765 — SIMULATION_ONLY; do not expose publicly')
    server = ThreadingHTTPServer(('127.0.0.1', 8765), Handler)
    server.serve_forever()

if __name__ == '__main__':
    main()
