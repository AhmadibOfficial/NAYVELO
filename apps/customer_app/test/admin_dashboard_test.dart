import 'dart:convert';
import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:nayvelo_customer/admin_dashboard.dart';

void main() {
  const fixture = '''{"schema_version":1,"mode":"SIMULATION_ONLY","source":"PUBLIC_FIXED_FICTIONAL_DATA","period":"Four invented example weeks; not current activity","plan_concepts":6,"weeks":[{"label":"Example week 1","visits":120,"onboarding_previews":40,"help_requests":10},{"label":"Example week 2","visits":138,"onboarding_previews":50,"help_requests":12},{"label":"Example week 3","visits":161,"onboarding_previews":58,"help_requests":11},{"label":"Example week 4","visits":180,"onboarding_previews":66,"help_requests":15}],"plan_interest":[{"code":"daily-flex","count":24},{"code":"smart-weekly","count":31},{"code":"monthly-plus","count":43},{"code":"family-connect","count":19},{"code":"business-pro","count":12},{"code":"global-roam","count":9}],"demo_operations":[{"code":"documentation","label":"Readiness guide review","state":"illustrative_only"},{"code":"support","label":"Simulated support queue","state":"illustrative_only"},{"code":"partnership","label":"Carrier integration prerequisite","state":"not_authorized"}],"disclaimer":"Fictional administrative exercise only. No real subscribers, network usage, tickets, activation, revenue, customer events, credentials, or operational access. Role switching is a demonstration, NOT authentication or authorization."}''';
  final data=jsonDecode(fixture) as Map<String,dynamic>;
  test('fixture remains fictional and summary reproducible',(){
    final f=AdminDemoFixture.fromJson(data);
    expect(f.visits,599);
    expect(f.previews,214);
    expect(f.planInterest.length,6);
  });
  test('PII, production and malformed inputs fail closed',(){
    expect(()=>AdminDemoFixture.fromJson({...data,'nin':'not_allowed'}),throwsFormatException);
    expect(()=>AdminDemoFixture.fromJson({...data,'mode':'LIVE'}),throwsFormatException);
    expect(()=>AdminDemoFixture.fromJson({...data,'weeks':[]}),throwsFormatException);
  });
  testWidgets('viewer hides trends and simulated role change reveals them',(tester) async{
    final fixture=AdminDemoFixture.fromJson(data);
    await tester.pumpWidget(MaterialApp(home:Scaffold(body:SingleChildScrollView(child:AdminDashboardDemo(demoFixture:fixture)))));
    await tester.pumpAndSettle();
    expect(find.byKey(const Key('admin-visits')),findsOneWidget);
    expect(find.text('Trends hidden in the viewer demonstration.'),findsOneWidget);
    await tester.tap(find.byKey(const Key('demo-admin-role')));
    await tester.pumpAndSettle();
    await tester.tap(find.text('analyst').last);
    await tester.pumpAndSettle();
    expect(find.text('Synthetic weekly activity'),findsOneWidget);
    expect(find.text('Read-only operational scenarios'),findsNothing);
  });
}
