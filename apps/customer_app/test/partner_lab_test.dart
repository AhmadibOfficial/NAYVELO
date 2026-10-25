import 'dart:convert';
import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:nayvelo_customer/partner_lab.dart';

void main() {
  late PartnerLabDocument sample;
  setUp(() {
    final cases = <Map<String, String>>[];
    for (var i=0;i<PartnerLabDocument.codes.length;i++) {
      cases.add({'code':PartnerLabDocument.codes[i], 'fault':PartnerLabDocument.faults[i],
        'label':'Fictional scenario $i', 'expected':PartnerLabDocument.outcomes[i],
        'explanation':'A fixed local demonstration with no live service and no identity data.'});
    }
    sample=PartnerLabDocument.fromJson({
      'schema_version':1,'mode':'SIMULATION_ONLY','source':'FIXED_SYNTHETIC_PARTNER_LAB',
      'network_connected':false,'activation_enabled':false,'payments_enabled':false,
      'real_subscribers_enabled':false,'certification_status':'NOT_VERIFIED',
      'disclaimer':PartnerLabDocument.disclaimer,'scenarios':cases,
    });
  });
  test('fixed synthetic scenarios validate with no real identities', () {
    expect(sample.scenarios.length,9);
    expect(sample.scenarios.first['outcome'],'ACCEPTED');
    expect(sample.scenarios.last['outcome'],'REJECTED_NO_RESPONSE');
  });
  test('rejects live service and injected extra fields', () {
    final data=<String,dynamic>{
      'schema_version':1,'mode':'SIMULATION_ONLY','source':'FIXED_SYNTHETIC_PARTNER_LAB',
      'network_connected':false,'activation_enabled':false,'payments_enabled':false,
      'real_subscribers_enabled':false,'certification_status':'NOT_VERIFIED',
      'disclaimer':PartnerLabDocument.disclaimer,
      'scenarios':List.generate(9,(i)=>{'code':PartnerLabDocument.codes[i],
        'fault':PartnerLabDocument.faults[i], 'expected':PartnerLabDocument.outcomes[i],
        'label':'Fictional scenario $i',
        'explanation':'A fixed local demonstration with no live service and no identity data.'})
    };
    expect(()=>PartnerLabDocument.fromJson({...data, 'network_connected':true}),throwsFormatException);
    expect(()=>PartnerLabDocument.fromJson({...data, 'nin':'PRIVATE'}),throwsFormatException);
    final clone=jsonDecode(jsonEncode(data)) as Map<String,dynamic>;
    (clone['scenarios'] as List)[0]['iccid']='NOT_ALLOWED';
    expect(()=>PartnerLabDocument.fromJson(clone),throwsFormatException);
  });
  testWidgets('read-only user can choose fictional cases', (tester) async {
    await tester.pumpWidget(MaterialApp(home:PartnerLabDemo(fixture:sample)));
    await tester.pumpAndSettle();
    expect(find.text('SIMULATION_ONLY · NOT CERTIFIED'),findsOneWidget);
    expect(find.text('ACCEPTED'),findsOneWidget);
    await tester.tap(find.byKey(const Key('partner-case')));
    await tester.pumpAndSettle();
    await tester.tap(find.text('Fictional scenario 1').last);
    await tester.pumpAndSettle();
    expect(find.text('REJECTED_TIMEOUT'),findsOneWidget);
  });
}
