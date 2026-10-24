import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:nayvelo_customer/esim_readiness_wizard.dart';

void main() {
  test('readiness never reports confirmed support', () {
    final likely = describeReadiness(
      device: EsimDevice.iphone,
      setting: EsimAnswer.yes,
      unlocked: EsimAnswer.yes,
    );
    expect(likely.title, contains('Potentially'));
    expect(likely.explanation, contains('NOT verified'));
    expect(describeReadiness(device: EsimDevice.android, setting: EsimAnswer.no, unlocked: EsimAnswer.yes).title,
        'Check manufacturer guidance');
    expect(describeReadiness(device: EsimDevice.android, setting: EsimAnswer.yes, unlocked: EsimAnswer.no).title,
        'Ask about network unlocking');
  });

  testWidgets('wizard is offline, navigable and restartable', (tester) async {
    await tester.pumpWidget(const MaterialApp(home: Scaffold(body: SingleChildScrollView(child: EsimReadinessWizard()))));
    expect(find.textContaining('self-check only'), findsOneWidget);
    expect(tester.widget<FilledButton>(find.byKey(const Key('wizard-next'))).onPressed, isNull);
    await tester.tap(find.byKey(const Key('platform-android')));
    await tester.pumpAndSettle();
    await tester.tap(find.byKey(const Key('wizard-next')));
    await tester.pumpAndSettle();
    expect(find.textContaining('Samsung: Settings'), findsOneWidget);
    await tester.ensureVisible(find.byKey(const Key('setting-yes')));
    await tester.tap(find.byKey(const Key('setting-yes')));
    await tester.pumpAndSettle();
    await tester.ensureVisible(find.byKey(const Key('wizard-next')));
    await tester.tap(find.byKey(const Key('wizard-next')));
    await tester.pumpAndSettle();
    await tester.ensureVisible(find.byKey(const Key('unlocked-yes')));
    await tester.tap(find.byKey(const Key('unlocked-yes')));
    await tester.pumpAndSettle();
    await tester.ensureVisible(find.byKey(const Key('wizard-next')));
    await tester.tap(find.byKey(const Key('wizard-next')));
    await tester.pumpAndSettle();
    expect(find.textContaining('Potentially ready'), findsOneWidget);
    expect(find.textContaining('NOT verified compatibility'), findsOneWidget);
    await tester.ensureVisible(find.byKey(const Key('wizard-restart')));
    await tester.tap(find.byKey(const Key('wizard-restart')));
    await tester.pumpAndSettle();
    expect(tester.widget<FilledButton>(find.byKey(const Key('wizard-next'))).onPressed, isNull);
  });
}
