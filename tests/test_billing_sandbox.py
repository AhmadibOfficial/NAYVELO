"""NAY-006 synthetic fixture arithmetic, fail-closed endpoints, no PII."""
from __future__ import annotations

import copy
import json
import shutil
import subprocess
import unittest
from http.server import ThreadingHTTPServer
from pathlib import Path
from tempfile import TemporaryDirectory
from threading import Thread
from unittest.mock import patch
from urllib.error import HTTPError
from urllib.request import Request, urlopen

from backend.nayvelo import billing_sandbox as lab
from backend.nayvelo.server import Handler

ROOT = Path(__file__).resolve().parents[1]


class BillingSandboxTests(unittest.TestCase):
    def test_fixture_no_identity_and_matches_flutter(self):
        data = lab.get_fixture()
        self.assertEqual(data['mode'], 'SIMULATION_ONLY')
        self.assertEqual(data['source'], 'FIXED_SYNTHETIC_FIXTURE')
        self.assertEqual(data['sample_rate_kobo_per_gib'], 125000)
        self.assertEqual(data['sample_allowance_mib'], 8192)
        self.assertEqual(data, json.loads((ROOT/'apps/customer_app/assets/synthetic_billing.json').read_text()))
        self.assertEqual(lab.validate_fixture(data), data)
        self.assertIsNot(lab.validate_fixture(data), data)
        serialized = json.dumps(data).lower()
        for disallowed in ('"name"', '"email"', '"phone"', '"nin"', '"imei"', '"eid"',
                           '"msisdn"', '"token"', '"password"', '"subscriber_id"', '"imsi"'):
            self.assertNotIn(disallowed, serialized)

    def test_exact_integer_arithmetic(self):
        self.assertEqual(lab.estimate_kobo(0, 125000), 0)
        self.assertEqual(lab.estimate_kobo(1024, 125000), 125000)
        self.assertEqual(lab.estimate_kobo(1, 125000), 122)
        self.assertEqual(lab.estimate_kobo(6144, 200000), 1200000)
        self.assertEqual(lab.forecast_mib([{'usage_mib':100}] * 7), 3000)
        self.assertEqual(lab.forecast_mib(lab.get_fixture()['days']), (sum([384,672,512,896,256,704,512])*30+3)//7)
        sample = lab.scenario()
        self.assertEqual(sample['mode'], 'SIMULATION_ONLY')
        self.assertEqual(sample['simulated_usage_mib'], 3936)
        self.assertEqual(sample['simulated_allowance_mib'], 8192)
        self.assertEqual(sample['projected_kobo'], lab.estimate_kobo(sample['projected_30_day_mib'], 125000))
        self.assertTrue(lab.scenario(rate_ngn_per_gib=5000, cap_ngn=1000)['over_hypothetical_cap'])
        self.assertFalse(lab.scenario(rate_ngn_per_gib=500, cap_ngn=50000)['over_hypothetical_cap'])

    def test_bad_inputs_are_not_interpreted_as_payments(self):
        for args in ((True, 10000),(-1,10000),(1,False),(1000001,10000),(100,0),(10,10000001)):
            with self.subTest(args=args), self.assertRaises(lab.UnsafeFixture):
                lab.estimate_kobo(*args)
        for rate,cap in ((1,5000),(500,0),(20000,2000),(True,5000)):
            with self.subTest(rate=rate,cap=cap), self.assertRaises(lab.UnsafeFixture):
                lab.scenario(rate,cap)

    def test_injected_fields_and_real_mode_rejected(self):
        for alteration in (
            lambda x: x.update({'phone': 'not-a-number'}),
            lambda x: x.update({'mode':'LIVE'}),
            lambda x: x['days'][0].update({'subscriber_id':'s1'}),
            lambda x: x['illustrative_history'][0].update({'payment_reference':'fake'}),
            lambda x: x['days'][0].update({'usage_mib':-1}),
            lambda x: x['days'][1].update({'date':'2026-10-01'}),
            lambda x: x['illustrative_history'][0].update({'estimate_kobo':1}),
            lambda x: x.update({'sample_rate_kobo_per_gib':0}),
            lambda x: x.update({'disclaimer':''}),
        ):
            data = copy.deepcopy(lab.get_fixture())
            alteration(data)
            with self.subTest(alteration=str(alteration)), self.assertRaises(lab.UnsafeFixture):
                lab.validate_fixture(data)
        original=lab.get_fixture()
        with TemporaryDirectory() as temp:
            path=Path(temp)/'poison.json'
            original['days'][0]['msisdn']='malicious'
            path.write_text(json.dumps(original))
            with patch.object(lab,'FIXTURE',path),self.assertRaises(lab.UnsafeFixture):
                lab.get_fixture()

    def test_node_ui_and_read_only_contract(self):
        if shutil.which('node'):
            subprocess.run(['node','tests/billing_sandbox_test.cjs'],cwd=ROOT,check=True,timeout=10,
                           stdout=subprocess.DEVNULL)
        server=ThreadingHTTPServer(('127.0.0.1',0),Handler)
        thread=Thread(target=server.serve_forever,daemon=True)
        thread.start()
        host=f'http://127.0.0.1:{server.server_port}'
        try:
            with urlopen(host+'/api/v1/demo-usage',timeout=3) as r:
                self.assertEqual(r.status,200)
                self.assertEqual(r.headers['Cache-Control'],'no-store')
                self.assertEqual(json.load(r),lab.get_fixture())
            for path in ('/billing_sandbox.js','/billing_sandbox.css'):
                with urlopen(host+path,timeout=3) as r:
                    self.assertEqual(r.status,200)
            for path in ('/api/v1/payments','/api/v1/billing','/api/v1/usage',
                         '/api/v1/transactions','/api/v1/checkout','/api/v1/topup',
                         '/api/v1/renew','/api/v1/invoices','/api/v1/wallet'):
                for method in ('GET','POST'):
                    with self.subTest(path=path,method=method):
                        try:
                            req=Request(host+path,method=method,data=b'{}' if method=='POST' else None)
                            with urlopen(req,timeout=3):
                                self.fail('Live billing path unexpectedly permitted')
                        except HTTPError as err:
                            self.assertEqual(err.code,403)
                            err.close()
            for method in ('POST','PUT','PATCH','DELETE'):
                with self.subTest(method=method):
                    try:
                        req=Request(host+'/api/v1/demo-usage',data=b'{}',method=method)
                        with urlopen(req,timeout=3):
                            self.fail('Demo fixture unexpectedly mutable')
                    except HTTPError as err:
                        self.assertEqual(err.code,403)
                        err.close()
        finally:
            server.shutdown();server.server_close();thread.join(timeout=3)


if __name__=='__main__':
    unittest.main()
