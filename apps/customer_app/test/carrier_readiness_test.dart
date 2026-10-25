import 'dart:convert';
import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:nayvelo_customer/carrier_readiness.dart';

void main() {
  const sample = '''{"schema_version":1,"mode":"SIMULATION_ONLY","source":"PUBLIC_FIXED_INTERFACE_DESIGN","integration_state":"NOT_AUTHORIZED","network_connected":false,"esim_provisioning_enabled":false,"real_subscribers_enabled":false,"payments_enabled":false,"description":"Architecture exercise only. No service.","boundaries":[{"code":"network_access","label":"Host-network interfaces","state":"BLOCKED","detail":"Commercial agreement required"},{"code":"esim_provisioning","label":"eSIM profile provisioning","state":"BLOCKED","detail":"Authorized provider required"},{"code":"service_management","label":"Voice and SMS","state":"BLOCKED","detail":"Licensing is required"},{"code":"usage_reporting","label":"Usage and billing","state":"BLOCKED","detail":"Partner feeds required"},{"code":"subscriber_registration","label":"Subscriber identity","state":"BLOCKED","detail":"Registration rules required"}],"certification_gates":[{"code":"ncc_licensing","label":"NCC authorization","status":"NOT_VERIFIED"},{"code":"wholesale_contract","label":"Wholesale agreement","status":"NOT_VERIFIED"},{"code":"rsp_partner","label":"SM-DP+ partner","status":"NOT_VERIFIED"},{"code":"subscriber_compliance","label":"Registration compliance","status":"NOT_VERIFIED"},{"code":"security_assurance","label":"Security review","status":"NOT_VERIFIED"},{"code":"interoperability","label":"Interoperability","status":"NOT_VERIFIED"},{"code":"service_operations","label":"Operations","status":"NOT_VERIFIED"},{"code":"commercial_assurance","label":"Commercial review","status":"NOT_VERIFIED"}],"disclaimer":"PUBLIC DESIGN DEMONSTRATION ONLY. Not operational."}''';
  final json = jsonDecode(sample) as Map<String, dynamic>;
  test('public document keeps every boundary blocked', () {
    final doc=CarrierReadinessDocument.fromJson(json);
    expect(doc.boundaries.length,5);
    expect(doc.gates.length,8);
  });
  test('unknown identities, network operations and fraudulent approvals denied', () {
    expect(()=>CarrierReadinessDocument.fromJson({...json,'nin':'bad'}),throwsFormatException);
    expect(()=>CarrierReadinessDocument.fromJson({...json,'network_connected':true}),throwsFormatException);
    expect(()=>CarrierReadinessDocument.fromJson({...json,'mode':'LIVE'}),throwsFormatException);
    final bad=jsonDecode(sample) as Map<String,dynamic>;
    (bad['certification_gates'] as List)[0]['status']='CERTIFIED';
    expect(()=>CarrierReadinessDocument.fromJson(bad),throwsFormatException);
  });
  testWidgets('read-only Flutter readiness and evidence screen', (tester) async {
    final doc=CarrierReadinessDocument.fromJson(json);
    await tester.pumpWidget(MaterialApp(home:Scaffold(body:SingleChildScrollView(child:CarrierReadinessDemo(fixture:doc)))));
    await tester.pumpAndSettle();
    expect(find.byKey(const Key('carrier-blocked')),findsOneWidget);
    expect(find.text('All evidence is NOT VERIFIED'),findsNothing);
    await tester.ensureVisible(find.byKey(const Key('carrier-show-evidence')));
    await tester.tap(find.byKey(const Key('carrier-show-evidence')));
    await tester.pumpAndSettle();
    expect(find.text('All evidence is NOT VERIFIED'),findsOneWidget);
  });
}
