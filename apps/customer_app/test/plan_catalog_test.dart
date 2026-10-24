import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:nayvelo_customer/plan_catalog_view.dart';

void main() {
  test('catalog parser rejects unauthorized or priced data', () {
    const fixture = '{"mode":"SIMULATION_ONLY","schema_version":1,"plans":['
        '{"code":"demo","title":"Demo","period":"Daily","audience":"Testing",'
        '"description":"Example","data_gb":null,"voice_minutes":null,"sms_count":null,'
        '"price_ngn":null,"available_for_purchase":false,"hotspot":"Not confirmed",'
        '"rollover":"Not confirmed"}]}';
    expect(parseConceptPlans(fixture).length, 1);
    expect(() => parseConceptPlans(fixture.replaceFirst('"price_ngn":null', '"price_ngn":1000')),
        throwsFormatException);
    expect(() => parseConceptPlans(fixture.replaceFirst('"available_for_purchase":false', '"available_for_purchase":true')),
        throwsFormatException);
  });

  testWidgets('read-only catalog filters and compares', (tester) async {
    await tester.pumpWidget(const MaterialApp(home: Scaffold(body: SingleChildScrollView(child: PlanCatalogView()))));
    await tester.pumpAndSettle();
    expect(find.text('Daily Flex'), findsOneWidget);
    expect(find.textContaining('Not purchasable'), findsWidgets);
    await tester.tap(find.text('Compare Daily Flex'));
    await tester.pumpAndSettle();
    await tester.ensureVisible(find.text('Compare Smart Weekly'));
    await tester.tap(find.text('Compare Smart Weekly'));
    await tester.pumpAndSettle();
    await tester.ensureVisible(find.text('Compare selected plans'));
    await tester.tap(find.text('Compare selected plans'));
    await tester.pumpAndSettle();
    expect(find.textContaining('informational only'), findsOneWidget);
    expect(find.text('Purchase'), findsOneWidget);
  });
}
