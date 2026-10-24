import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:nayvelo_customer/account_lab.dart';

void main() {
  test('fictional state cannot activate or self-recover from lock', () {
    final account = DemoAccountState('DEMO-ALPHA');
    expect(account.productAnalytics, isFalse);
    expect(account.productNews, isFalse);
    expect(account.permits('activated'), isFalse);
    expect(() => account.transition('activated'), throwsStateError);
    account.transition('locked');
    expect(account.permits('preview'), isFalse);
    expect(() => account.transition('preview'), throwsStateError);
    expect(DemoAccountState('DEMO-BETA').status, 'paused');
  });

  testWidgets('simulation switches accounts and resets privacy preferences', (tester) async {
    await tester.pumpWidget(const MaterialApp(
      home: Scaffold(body: SingleChildScrollView(child: AccountLab())),
    ));
    expect(find.textContaining('Fictional subscriber profiles only'), findsOneWidget);
    expect(find.text('Local state: PREVIEW'), findsOneWidget);
    await tester.ensureVisible(find.byKey(const Key('demo-to-paused')));
    await tester.tap(find.byKey(const Key('demo-to-paused')));
    await tester.pumpAndSettle();
    expect(find.text('Local state: PAUSED'), findsOneWidget);
    await tester.ensureVisible(find.byKey(const Key('demo-analytics')));
    await tester.tap(find.byKey(const Key('demo-analytics')));
    await tester.pumpAndSettle();
    expect(tester.widget<SwitchListTile>(find.byKey(const Key('demo-analytics'))).value, isTrue);
    await tester.ensureVisible(find.byKey(const Key('demo-reset')));
    await tester.tap(find.byKey(const Key('demo-reset')));
    await tester.pumpAndSettle();
    expect(find.text('Local state: PREVIEW'), findsOneWidget);
    expect(tester.widget<SwitchListTile>(find.byKey(const Key('demo-analytics'))).value, isFalse);
  });
}
