import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:nayvelo_customer/main.dart';

void main() {
  testWidgets('shows simulation notice and plan concepts', (tester) async {
    await tester.pumpWidget(const NayveloApp());
    expect(find.textContaining('NO ACTIVE NETWORK'), findsOneWidget);
    await tester.tap(find.byIcon(Icons.layers_outlined));
    await tester.pumpAndSettle();
    expect(find.text('Daily Flex'), findsOneWidget);
    expect(find.textContaining('Not purchasable'), findsWidgets);
  });
}
