import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:nayvelo_customer/billing_sandbox.dart';

void main() {
  final safe = <String, dynamic>{
    'schema_version': 1, 'mode': 'SIMULATION_ONLY', 'source': 'FIXED_SYNTHETIC_FIXTURE',
    'currency': 'NGN', 'usage_unit': 'MiB', 'forecast_days': 30,
    'sample_allowance_mib': 8192, 'sample_rate_kobo_per_gib': 125000,
    'disclaimer': 'Fictional usage for testing only',
    'days': List.generate(7, (i) => {'date': '2026-10-${(i + 1).toString().padLeft(2,'0')}', 'usage_mib': 100}),
    'illustrative_history': List.generate(3, (i) => {
      'period':'2026-${(i + 7).toString().padLeft(2,'0')}',
      'usage_mib': 1024, 'estimate_kobo': 125000,
    }),
  };
  test('integer kobo math and 30 day projection', () {
    final demo = BillingFixture.fromJson(safe);
    expect(demo.sevenDayMiB, 700);
    expect(demo.forecast30MiB, 3000);
    expect(BillingFixture.estimateKobo(1024, 125000), 125000);
    expect(BillingFixture.estimateKobo(1, 125000), 122);
  });
  test('unexpected identity and non-simulation policies rejected', () {
    expect(() => BillingFixture.fromJson({...safe, 'msisdn': 'REDACTED'}), throwsFormatException);
    expect(() => BillingFixture.fromJson({...safe, 'mode': 'LIVE'}), throwsFormatException);
    expect(() => BillingFixture.fromJson({...safe, 'days': []}), throwsFormatException);
  });
  testWidgets('shows fictional usage and no purchase controls', (tester) async {
    final demo = BillingFixture.fromJson(safe);
    await tester.pumpWidget(MaterialApp(home: Scaffold(body: SingleChildScrollView(child: BillingSandbox(demoFixture: demo)))));
    await tester.pumpAndSettle();
    expect(find.byKey(const Key('billing-used')), findsOneWidget);
    expect(find.textContaining('Illustrative 30-day expense'), findsOneWidget);
    expect(find.textContaining('no actual invoices'), findsOneWidget);
    expect(find.text('Pay now'), findsNothing);
    expect(find.text('Activate eSIM'), findsNothing);
  });
}
