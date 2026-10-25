"""NAY-009 deterministic fake-partner conformance + strict no-network controls."""
from __future__ import annotations

import ast
import copy
import json
from http.server import ThreadingHTTPServer
from pathlib import Path
import socket
from threading import Thread
import unittest
from unittest.mock import patch
from urllib.error import HTTPError
from urllib.request import Request, urlopen

from backend.nayvelo.partner_lab import (
    SCENARIOS, REQUEST_TAG, LabContractViolation, inspect_replies, load_fixture,
    public_report, replay_scenario, validate_fixture,
)
from backend.nayvelo.server import Handler, SIMULATION_ONLY

ROOT = Path(__file__).resolve().parents[1]
BASE = {'request_tag': REQUEST_TAG, 'sequence':1, 'operation':'READINESS_ONLY',
        'result':'ACK', 'latency_ms':10, 'simulation_only':True}


class PartnerLabTests(unittest.TestCase):
    def test_fixture_rejects_identity_and_false_operational_claims(self):
        fixture=load_fixture()
        self.assertTrue(SIMULATION_ONLY)
        self.assertEqual(fixture['certification_status'],'NOT_VERIFIED')
        self.assertFalse(fixture['network_connected'])
        self.assertEqual(len(fixture['scenarios']),9)
        self.assertEqual((ROOT/'shared/partner_lab.json').read_bytes(),
                         (ROOT/'apps/customer_app/assets/partner_lab.json').read_bytes())
        for k,v in [('nin','00000000000'),('eid','012345'),('iccid','012345'),
                    ('imsi','012345'),('msisdn','08011111111'),('bearer_token','abc'),
                    ('partner_url','https://example.invalid'),('customer_id','client'),
                    ('activation_enabled',True),('network_connected',True),
                    ('payments_enabled',True),('real_subscribers_enabled',True),
                    ('certification_status','CERTIFIED'),('schema_version',True)]:
            with self.subTest(k=k),self.assertRaises(LabContractViolation):
                validate_fixture({**fixture,k:v})
        bad=copy.deepcopy(fixture)
        bad['scenarios'][0]['expected']='NETWORK_ACTIVE'
        with self.assertRaises(LabContractViolation):validate_fixture(bad)
        bad=copy.deepcopy(fixture)
        bad['scenarios'][0]['subscriber_id']='any'
        with self.assertRaises(LabContractViolation):validate_fixture(bad)

    def test_all_scenarios_match_expected_fail_closed_verdict(self):
        for code,_,_,expected in SCENARIOS:
            with self.subTest(code=code):
                verdict=replay_scenario(code)
                self.assertEqual(verdict.outcome,expected)
                self.assertEqual(verdict.accepted,code=='nominal_ack')
        with self.assertRaises(LabContractViolation):replay_scenario('carrier-activation')
        report=public_report()
        self.assertEqual(report['integration_state'],'NOT_AUTHORIZED')
        self.assertEqual(report['scenario_count'],9)
        self.assertEqual(sum(x['accepted'] for x in report['scenarios']),1)

    def test_schema_enforces_exact_fields_and_strict_types(self):
        for event in ({**BASE,'imei':'123'}, {**BASE,'url':'https://example.invalid'},
                      {**BASE,'sim_token':'SECRET'}, {**BASE,'sequence':True},
                      {**BASE,'simulation_only':1}, {**BASE,'operation':'PROVISION_PROFILE'},
                      {**BASE,'latency_ms':float('nan')}, {**BASE,'result':None},
                      {**BASE,'sequence':'1'}):
            with self.subTest(event=event):
                self.assertFalse(inspect_replies([event]).accepted)
        self.assertEqual(inspect_replies([BASE]) .outcome,'ACCEPTED')
        self.assertEqual(inspect_replies([BASE,BASE]).outcome,'REJECTED_DUPLICATE')
        self.assertEqual(inspect_replies([]).outcome,'REJECTED_NO_RESPONSE')
        self.assertEqual(inspect_replies('not a response list').outcome,'REJECTED_SCHEMA')

    def test_deterministic_latency_sequence_and_correlation(self):
        cases=[({**BASE,'latency_ms':500},'ACCEPTED'),
               ({**BASE,'latency_ms':501},'REJECTED_TIMEOUT'),
               ({**BASE,'latency_ms':-1},'REJECTED_TIMEOUT'),
               ({**BASE,'sequence':2},'REJECTED_SEQUENCE'),
               ({**BASE,'request_tag':'WRONG'},'REJECTED_CORRELATION'),
               ({**BASE,'result':'ERROR'},'REJECTED_PARTNER_ERROR')]
        for event,expected in cases:
            with self.subTest(expected=expected):self.assertEqual(inspect_replies([event]).outcome,expected)

    def test_no_socket_or_external_dependencies_used_by_replay(self):
        path=ROOT/'backend/nayvelo/partner_lab.py'
        tree=ast.parse(path.read_text())
        imported={alias.name.split('.')[0] for item in ast.walk(tree) if isinstance(item,ast.Import) for alias in item.names}
        imported.update(item.module.split('.')[0] for item in ast.walk(tree) if isinstance(item,ast.ImportFrom) and item.module)
        self.assertTrue(imported.isdisjoint({'socket','ssl','requests','urllib','http',
                                                'httpx','aiohttp','subprocess','os','ftplib'}))
        with patch.object(socket,'socket',side_effect=AssertionError('A network socket was requested')) as raw:
            with patch.object(socket,'create_connection',side_effect=AssertionError('Remote call attempted')) as conn:
                public_report()
                for code,_,_,_ in SCENARIOS:replay_scenario(code)
                raw.assert_not_called();conn.assert_not_called()

    def test_read_only_demo_route_and_privileged_path_block(self):
        service=ThreadingHTTPServer(('127.0.0.1',0),Handler)
        thread=Thread(target=service.serve_forever,daemon=True)
        thread.start()
        base=f'http://127.0.0.1:{service.server_port}'
        try:
            with urlopen(base+'/api/v1/demo-partner-lab') as r:
                self.assertEqual(r.status,200)
                self.assertEqual(r.headers.get('Cache-Control'),'no-store')
                self.assertEqual(json.load(r)['scenario_count'],9)
            for path in ('/partner_lab.js','/partner_lab.css'):
                with urlopen(base+path) as r:self.assertEqual(r.status,200)
            for path in ('/api/v1/partner','/api/v1/partner/callback','/api/v1/carrier',
                         '/api/v1/smdp','/api/v1/activate','/api/v1/payments',
                         '/api/v1/subscribers','/api/v1/partner-sandbox'):
                with self.subTest(path=path),self.assertRaises(HTTPError) as err:
                    urlopen(base+path)
                self.assertEqual(err.exception.code,403);err.exception.close()
            for method in ('POST','PATCH','PUT','DELETE'):
                with self.subTest(method=method),self.assertRaises(HTTPError) as err:
                    urlopen(Request(base+'/api/v1/demo-partner-lab',method=method,data=b'{}'))
                self.assertEqual(err.exception.code,403);err.exception.close()
        finally:
            service.shutdown();service.server_close();thread.join(timeout=3)

    def test_schema_is_fictional_and_cannot_expand(self):
        schema=json.loads((ROOT/'contracts/partner_lab_response.schema.json').read_text())
        self.assertIs(schema['additionalProperties'],False)
        self.assertEqual(schema['properties']['operation']['const'],'READINESS_ONLY')
        self.assertEqual(schema['properties']['simulation_only']['const'],True)
        self.assertEqual(schema['properties']['request_tag']['const'],REQUEST_TAG)


if __name__=='__main__':unittest.main()
