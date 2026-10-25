import 'dart:convert';
import 'package:flutter/material.dart';
import 'package:flutter/services.dart';

/// Local-only fixed report. This never calls carrier APIs or loads personal data.
class PartnerLabDocument {
  const PartnerLabDocument(this.scenarios);
  final List<Map<String, String>> scenarios;

  static const codes = <String>[
    'nominal_ack', 'timeout', 'duplicate_response', 'out_of_order',
    'mismatched_tag', 'schema_drift', 'partner_error', 'pii_injection', 'empty_response'
  ];
  static const faults = <String>[
    'NONE', 'TIMEOUT', 'DUPLICATE', 'OUT_OF_ORDER', 'MISMATCHED_TAG',
    'SCHEMA_DRIFT', 'PARTNER_ERROR', 'PII_INJECTION', 'EMPTY'
  ];
  static const outcomes = <String>[
    'ACCEPTED', 'REJECTED_TIMEOUT', 'REJECTED_DUPLICATE', 'REJECTED_SEQUENCE',
    'REJECTED_CORRELATION', 'REJECTED_SCHEMA', 'REJECTED_PARTNER_ERROR',
    'REJECTED_SCHEMA', 'REJECTED_NO_RESPONSE'
  ];
  static const disclaimer = 'EDUCATIONAL OFFLINE CONTRACT LAB ONLY. All responses are fictional; no carrier, eSIM provisioning, payment, identity or external partner is connected or certified.';

  factory PartnerLabDocument.fromJson(Map<String, dynamic> data) {
    const keys = <String>{'schema_version','mode','source','network_connected','activation_enabled',
      'payments_enabled','real_subscribers_enabled','certification_status','disclaimer','scenarios'};
    if (data.keys.toSet().difference(keys).isNotEmpty || data.length != keys.length ||
        data['schema_version'] != 1 || data['mode'] != 'SIMULATION_ONLY' ||
        data['source'] != 'FIXED_SYNTHETIC_PARTNER_LAB' || data['network_connected'] != false ||
        data['activation_enabled'] != false || data['payments_enabled'] != false ||
        data['real_subscribers_enabled'] != false || data['certification_status'] != 'NOT_VERIFIED' ||
        data['disclaimer'] != disclaimer) {
      throw const FormatException('Invalid NAYVELO offline laboratory fixture');
    }
    final raw = data['scenarios'];
    if (raw is! List || raw.length != codes.length) {
      throw const FormatException('Unexpected fictional scenario list');
    }
    final rows = <Map<String, String>>[];
    for (var i=0; i<codes.length; i++) {
      final item = raw[i];
      if (item is! Map || item.keys.toSet().difference({'code','label','fault','expected','explanation'}).isNotEmpty ||
          item.length != 5 || item['code'] != codes[i] || item['fault'] != faults[i] ||
          item['expected'] != outcomes[i] || item['label'] is! String ||
          item['explanation'] is! String || (item['explanation'] as String).length < 30 ||
          (item['explanation'] as String).length > 180 ||
          (item['explanation'] as String).contains('http')) {
        throw const FormatException('Unsafe fictional scenario');
      }
      rows.add({'label':item['label'] as String,'outcome':outcomes[i],
        'explanation':item['explanation'] as String});
    }
    return PartnerLabDocument(rows);
  }

  static Future<PartnerLabDocument> load() async => PartnerLabDocument.fromJson(
    jsonDecode(await rootBundle.loadString('assets/partner_lab.json')) as Map<String, dynamic>);
}

class PartnerLabDemo extends StatefulWidget {
  const PartnerLabDemo({super.key, this.fixture});
  final PartnerLabDocument? fixture;
  @override
  State<PartnerLabDemo> createState() => _PartnerLabDemoState();
}

class _PartnerLabDemoState extends State<PartnerLabDemo> {
  late final Future<PartnerLabDocument> _future;
  int selected = 0;
  @override
  void initState() {
    super.initState();
    _future = widget.fixture == null ? PartnerLabDocument.load() : Future.value(widget.fixture!);
  }
  @override
  Widget build(BuildContext context) => Scaffold(
    appBar: AppBar(title: const Text('NAY-009 · Partner contract lab')),
    body: FutureBuilder<PartnerLabDocument>(future:_future,builder:(context,snapshot) {
      if (snapshot.hasError) return const Center(child:Text('Offline laboratory unavailable. No services are enabled.'));
      if (!snapshot.hasData) return const Center(child:CircularProgressIndicator());
      final rows = snapshot.data!.scenarios;
      final current = rows[selected];
      return ListView(padding:const EdgeInsets.all(20),children:[
        const Text('SIMULATION_ONLY · NOT CERTIFIED',style:TextStyle(fontWeight:FontWeight.bold,color:Color(0xFF1769FF))),
        const SizedBox(height:12),
        const Text(PartnerLabDocument.disclaimer),
        const SizedBox(height:20),
        DropdownButtonFormField<int>(key:const Key('partner-case'),initialValue:selected,
          decoration:const InputDecoration(labelText:'Fictional test scenario',border:OutlineInputBorder()),
          items:[for(var i=0;i<rows.length;i++) DropdownMenuItem(value:i,child:Text(rows[i]['label']!))],
          onChanged:(value) {if(value!=null)setState(()=>selected=value);}),
        const SizedBox(height:16),
        Card(child:Padding(padding:const EdgeInsets.all(18),child:Column(crossAxisAlignment:CrossAxisAlignment.start,children:[
          Text(current['outcome']!,key:const Key('partner-outcome'),style:const TextStyle(fontSize:18,fontWeight:FontWeight.bold)),
          const SizedBox(height:8),Text(current['explanation']!),
          const SizedBox(height:8),const Text('Expected synthetic outcome only. This does not run an external partner certification test.'),
        ]))),
        const SizedBox(height:12),
        const Text('All provisioning, payments, account registration and real network operations remain blocked.'),
      ]);
    }),
  );
}
