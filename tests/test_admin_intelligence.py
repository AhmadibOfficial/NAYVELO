"""Strict synthetic admin validation, negative endpoint and role demonstration tests."""
from __future__ import annotations

import copy
import json
from pathlib import Path
import subprocess
import unittest
from unittest.mock import patch
from urllib.error import HTTPError
from urllib.request import Request, urlopen
from http.server import ThreadingHTTPServer
from threading import Thread

from backend.nayvelo import admin_intelligence as a
from backend.nayvelo.server import Handler, SIMULATION_ONLY

ROOT = Path(__file__).resolve().parents[1]

class AdminIntelligenceTests(unittest.TestCase):
    def test_fixture_exact_and_flutter_matches(self):
        data=a.load_fixture()
        raw=(ROOT/'shared/synthetic_admin.json').read_bytes()
        self.assertEqual(raw,(ROOT/'apps/customer_app/assets/synthetic_admin.json').read_bytes())
        self.assertEqual(data['mode'],'SIMULATION_ONLY')
        self.assertEqual(data['source'],'PUBLIC_FIXED_FICTIONAL_DATA')
        self.assertEqual(sum(w['visits'] for w in data['weeks']),599)
        self.assertTrue(SIMULATION_ONLY)

    def test_roles_are_demo_views_without_side_effects(self):
        v=a.role_view('viewer'); self.assertEqual(v['summary']['fictional_previews'],214)
        self.assertNotIn('weekly_trends',v);self.assertNotIn('plan_interest',v)
        analyst=a.role_view('analyst');self.assertIn('plan_interest',analyst)
        self.assertNotIn('demo_operations',analyst)
        op=a.role_view('operator');self.assertEqual(op['demo_operations'][2]['state'],'not_authorized')
        for invalid in ('admin','root','',None,0):
            with self.subTest(invalid=invalid),self.assertRaises(a.InvalidSyntheticAnalytics):
                a.role_view(invalid)
        op['demo_operations'][0]['state']='live'
        self.assertEqual(a.role_view('operator')['demo_operations'][0]['state'],'illustrative_only')

    def test_poisoned_identity_live_mode_and_inconsistent_counts_rejected(self):
        data=a.load_fixture()
        variations=[{'nin':'12345'}, {'phone_number':'000000'}, {'customer_email':'demo@demo.invalid'},
                    {'api_key':'very-bad'}, {'role':'operator'}]
        for extra in variations:
            with self.subTest(extra=extra), self.assertRaises(a.InvalidSyntheticAnalytics):
                a.validate_fixture({**data,**extra})
        for k,v in [('mode','LIVE'),('source','CARRIER'),('plan_concepts',7)]:
            with self.subTest(k=k),self.assertRaises(a.InvalidSyntheticAnalytics):
                a.validate_fixture({**data,k:v})
        poisoned=copy.deepcopy(data);poisoned['weeks'][0]['onboarding_previews']=121
        with self.assertRaises(a.InvalidSyntheticAnalytics):a.validate_fixture(poisoned)
        poisoned=copy.deepcopy(data);poisoned['plan_interest'][0]['subscriber_id']='fake'
        with self.assertRaises(a.InvalidSyntheticAnalytics):a.validate_fixture(poisoned)
        poisoned=copy.deepcopy(data);poisoned['demo_operations'][2]['state']='enabled'
        with self.assertRaises(a.InvalidSyntheticAnalytics):a.validate_fixture(poisoned)

    def test_read_only_fixture_and_sensitive_routes(self):
        server=ThreadingHTTPServer(('127.0.0.1',0),Handler)
        thread=Thread(target=server.serve_forever,daemon=True);thread.start()
        host=f'http://127.0.0.1:{server.server_port}'
        try:
            with urlopen(host+'/api/v1/demo-admin') as resp:
                self.assertEqual(resp.status,200)
                self.assertEqual(resp.headers.get('Cache-Control'),'no-store')
                self.assertEqual(resp.headers.get('Content-Security-Policy','').find("default-src 'self'"),0)
                result=json.load(resp)
                self.assertEqual(result['source'],'PUBLIC_FIXED_FICTIONAL_DATA')
                self.assertEqual(result['disclaimer'].count('NOT authentication'),1)
            for resource in ('/admin_dashboard.js','/admin_dashboard.css'):
                with urlopen(host+resource) as resp:self.assertEqual(resp.status,200)
            paths=['/api/v1/admin','/api/v1/admin/roles','/api/v1/metrics', '/api/v1/audit',
                   '/api/v1/exports','/api/v1/subscriber-admin','/api/v1/provisioning',
                   '/api/v1/payments','/api/v1/activate','/api/v1/billing','/api/v1/usage']
            for path in paths:
                with self.subTest(path=path),self.assertRaises(HTTPError) as err:
                    urlopen(host+path)
                self.assertEqual(err.exception.code,403);err.exception.close()
            for verb in ('POST','PUT','PATCH','DELETE'):
                with self.subTest(method=verb),self.assertRaises(HTTPError) as err:
                    urlopen(Request(host+'/api/v1/demo-admin',data=b'{}',method=verb))
                self.assertEqual(err.exception.code,403);err.exception.close()
        finally:
            server.shutdown();server.server_close();thread.join(timeout=2)

    def test_browser_mock_runner(self):
        if subprocess.run(['node','--version'],capture_output=True).returncode!=0:
            self.skipTest('Node not installed')
        subprocess.run(['node','tests/admin_dashboard_test.cjs'],cwd=ROOT,check=True)

if __name__=='__main__':unittest.main()
