"""NAY-008 negative tests: no network, no authorization, no privileged endpoints."""
from __future__ import annotations

import ast
import copy
from http.server import ThreadingHTTPServer
import json
from pathlib import Path
import socket
from threading import Thread
import unittest
from unittest.mock import patch
from urllib.error import HTTPError
from urllib.request import Request, urlopen

from backend.nayvelo.carrier_contracts import (
    BlockedCarrierAdapter, CarrierAction, CarrierOperationDenied,
    ContractRejected, FictionalCommand, public_readiness, validate_readiness,
)
from backend.nayvelo.server import Handler, SIMULATION_ONLY

ROOT=Path(__file__).resolve().parents[1]


class CarrierContractTests(unittest.TestCase):
    def test_fictional_fixed_fixture_and_flutter_asset_match(self):
        report=public_readiness()
        self.assertTrue(SIMULATION_ONLY)
        self.assertEqual(report['integration_state'],'NOT_AUTHORIZED')
        self.assertFalse(any(report[k] for k in ('network_connected','esim_provisioning_enabled','real_subscribers_enabled','payments_enabled')))
        self.assertEqual([x['state'] for x in report['boundaries']],['BLOCKED']*5)
        self.assertEqual([x['status'] for x in report['certification_gates']],['NOT_VERIFIED']*8)
        self.assertEqual((ROOT/'shared/carrier_readiness.json').read_bytes(),
                         (ROOT/'apps/customer_app/assets/carrier_readiness.json').read_bytes())
        mutated=BlockedCarrierAdapter().describe();mutated['boundaries'][0]['state']='CONNECTED'
        self.assertEqual(BlockedCarrierAdapter().describe()['boundaries'][0]['state'],'BLOCKED')

    def test_poisoned_fixture_rejected(self):
        f=public_readiness()
        for added in ({'nin':'12345678900'}, {'eid':'890000'}, {'phone':'080000'},
                      {'iccid':'0123456789'}, {'operator_token':'secret'},
                      {'network_endpoint':'https://example.invalid'}, {'credentials':{}}):
            with self.subTest(added=added), self.assertRaises(ContractRejected):
                validate_readiness({**f,**added})
        for key,value in [('mode','LIVE'), ('integration_state','CONNECTED'),('network_connected',True),
                          ('payments_enabled',True),('esim_provisioning_enabled',True),
                          ('real_subscribers_enabled',True),('schema_version',True)]:
            with self.subTest(key=key),self.assertRaises(ContractRejected):
                validate_readiness({**f,key:value})
        bad=copy.deepcopy(f);bad['certification_gates'][0]['status']='CERTIFIED'
        with self.assertRaises(ContractRejected):validate_readiness(bad)
        bad=copy.deepcopy(f);bad['boundaries'][0]['state']='ACTIVE'
        with self.assertRaises(ContractRejected):validate_readiness(bad)
        bad=copy.deepcopy(f);bad['boundaries'][0]['subscriber_id']='invented'
        with self.assertRaises(ContractRejected):validate_readiness(bad)

    def test_adapter_can_never_create_carrier_connections(self):
        adapter=BlockedCarrierAdapter()
        with patch.object(socket,'create_connection',side_effect=AssertionError('OUTBOUND NETWORK DETECTED')) as conn:
            with patch.object(socket,'socket',side_effect=AssertionError('OUTBOUND SOCKET DETECTED')) as raw:
                for action in CarrierAction:
                    with self.subTest(action=action),self.assertRaises(CarrierOperationDenied):
                        adapter.execute(FictionalCommand(action))
                with self.assertRaises(CarrierOperationDenied):adapter.execute(object())
                self.assertEqual(adapter.describe()['mode'],'SIMULATION_ONLY')
                conn.assert_not_called();raw.assert_not_called()
        with self.assertRaises(ContractRejected):FictionalCommand(CarrierAction.PROVISION_PROFILE,'REAL_PROFILE')
        with self.assertRaises(ContractRejected):FictionalCommand('PROVISION_PROFILE')
        source=(ROOT/'backend/nayvelo/carrier_contracts.py').read_text()
        tree=ast.parse(source)
        imports={alias.name.split('.')[0] for node in ast.walk(tree) if isinstance(node,ast.Import) for alias in node.names}
        imports.update(node.module.split('.')[0] for node in ast.walk(tree) if isinstance(node,ast.ImportFrom) and node.module)
        self.assertTrue(imports.isdisjoint({'socket','urllib','requests','http','httpx','aiohttp','subprocess'}))

    def test_contract_only_has_fictional_fields(self):
        schema=json.loads((ROOT/'contracts/carrier_interface_design.schema.json').read_text())
        self.assertIs(schema['additionalProperties'],False)
        self.assertEqual(schema['properties']['mode']['const'],'SIMULATION_ONLY')
        self.assertEqual(schema['properties']['scenario']['const'],'EXAMPLE_ONLY')
        examples=json.loads((ROOT/'contracts/fictional_commands.json').read_text())
        self.assertEqual(len(examples),len(CarrierAction))
        for item in examples:
            self.assertEqual(set(item),{'schema_version','mode','action','scenario'})
            self.assertEqual(item['mode'],'SIMULATION_ONLY')
            self.assertEqual(item['scenario'],'EXAMPLE_ONLY')

    def test_read_only_demo_not_privileged_carrier_endpoints(self):
        server=ThreadingHTTPServer(('127.0.0.1',0),Handler)
        thread=Thread(target=server.serve_forever,daemon=True);thread.start()
        base=f'http://127.0.0.1:{server.server_port}'
        try:
            with urlopen(base+'/api/v1/demo-carrier-readiness') as r:
                self.assertEqual(r.status,200)
                self.assertEqual(r.headers.get('Cache-Control'),'no-store')
                self.assertEqual(json.load(r)['network_connected'],False)
            for path in ('/carrier_readiness.css','/carrier_readiness.js'):
                with urlopen(base+path) as r:self.assertEqual(r.status,200)
            forbidden=('/api/v1/carrier','/api/v1/carrier/activate','/api/v1/partner',
                '/api/v1/partner/sessions','/api/v1/operator','/api/v1/smdp',
                '/api/v1/sm-dp-plus','/api/v1/profile-download','/api/v1/esim',
                '/api/v1/provision','/api/v1/activate','/api/v1/subscribers',
                '/api/v1/payments','/api/v1/usage','/api/v1/voice')
            for path in forbidden:
                with self.subTest(path=path),self.assertRaises(HTTPError) as err:
                    urlopen(base+path)
                self.assertEqual(err.exception.code,403);err.exception.close()
            for method in ('POST','PUT','PATCH','DELETE'):
                with self.subTest(method=method),self.assertRaises(HTTPError) as err:
                    urlopen(Request(base+'/api/v1/demo-carrier-readiness',data=b'{}',method=method))
                self.assertEqual(err.exception.code,403);err.exception.close()
        finally:
            server.shutdown();server.server_close();thread.join(timeout=3)

if __name__=='__main__':unittest.main()
