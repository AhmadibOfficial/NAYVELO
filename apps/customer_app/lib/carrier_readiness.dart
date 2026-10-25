import 'dart:convert';

import 'package:flutter/material.dart';
import 'package:flutter/services.dart';

/// Offline readiness document. Never connects to a carrier, registers a SIM,
/// verifies subscriber identity, or changes a network service.
class CarrierReadinessDocument {
  CarrierReadinessDocument._(this.boundaries, this.gates);
  final List<Map<String, String>> boundaries;
  final List<Map<String, String>> gates;

  factory CarrierReadinessDocument.fromJson(Map<String, dynamic> data) {
    const root = {'schema_version','mode','source','integration_state','network_connected',
      'esim_provisioning_enabled','real_subscribers_enabled','payments_enabled',
      'description','boundaries','certification_gates','disclaimer'};
    if (data.keys.toSet().difference(root).isNotEmpty || data.length != root.length ||
        data['schema_version'] != 1 || data['mode'] != 'SIMULATION_ONLY' ||
        data['source'] != 'PUBLIC_FIXED_INTERFACE_DESIGN' ||
        data['integration_state'] != 'NOT_AUTHORIZED' ||
        data['network_connected'] != false || data['esim_provisioning_enabled'] != false ||
        data['real_subscribers_enabled'] != false || data['payments_enabled'] != false ||
        data['description'] is! String ||
        !(data['description'] as String).startsWith('Architecture exercise only.') ||
        data['disclaimer'] is! String ||
        !(data['disclaimer'] as String).startsWith('PUBLIC DESIGN DEMONSTRATION ONLY.')) {
      throw const FormatException('NAY-008 readiness fixture is not safe');
    }
    const boundaryCodes = ['network_access','esim_provisioning','service_management',
      'usage_reporting','subscriber_registration'];
    const gateCodes = ['ncc_licensing','wholesale_contract','rsp_partner','subscriber_compliance',
      'security_assurance','interoperability','service_operations','commercial_assurance'];
    final rawBoundaries = data['boundaries'];
    final rawGates = data['certification_gates'];
    if (rawBoundaries is! List || rawBoundaries.length != boundaryCodes.length ||
        rawGates is! List || rawGates.length != gateCodes.length) {
      throw const FormatException('NAY-008 checklist length is invalid');
    }
    final boundaries = <Map<String, String>>[];
    for (var i=0; i<rawBoundaries.length; i++) {
      final item = rawBoundaries[i];
      if (item is! Map || item.keys.toSet().difference({'code','label','state','detail'}).isNotEmpty ||
          item.length != 4 || item['code'] != boundaryCodes[i] || item['state'] != 'BLOCKED' ||
          item['label'] is! String || item['detail'] is! String ||
          (item['detail'] as String).length < 10) {
        throw const FormatException('Unsafe carrier boundary');
      }
      boundaries.add({'label':item['label'] as String, 'detail':item['detail'] as String});
    }
    final gates = <Map<String, String>>[];
    for (var i=0; i<rawGates.length; i++) {
      final item = rawGates[i];
      if (item is! Map || item.keys.toSet().difference({'code','label','status'}).isNotEmpty ||
          item.length != 3 || item['code'] != gateCodes[i] || item['status'] != 'NOT_VERIFIED' ||
          item['label'] is! String) {
        throw const FormatException('Unsafe certification evidence');
      }
      gates.add({'label':item['label'] as String});
    }
    return CarrierReadinessDocument._(boundaries, gates);
  }

  static Future<CarrierReadinessDocument> load() async =>
      CarrierReadinessDocument.fromJson(
        jsonDecode(await rootBundle.loadString('assets/carrier_readiness.json')) as Map<String, dynamic>);
}

class CarrierReadinessDemo extends StatefulWidget {
  const CarrierReadinessDemo({super.key, this.fixture});
  final CarrierReadinessDocument? fixture;
  @override
  State<CarrierReadinessDemo> createState() => _CarrierReadinessDemoState();
}

class _CarrierReadinessDemoState extends State<CarrierReadinessDemo> {
  late final Future<CarrierReadinessDocument> _future;
  bool showEvidence = false;
  @override
  void initState() {
    super.initState();
    _future= widget.fixture == null ? CarrierReadinessDocument.load() : Future.value(widget.fixture!);
  }
  @override
  Widget build(BuildContext context) => FutureBuilder<CarrierReadinessDocument>(
    future:_future,
    builder:(context,snapshot) {
      if (snapshot.hasError) return const Text('No carrier readiness data available. All services remain disabled.');
      if (!snapshot.hasData) return const Center(child:CircularProgressIndicator());
      final report = snapshot.data!;
      return Column(crossAxisAlignment: CrossAxisAlignment.start,children:[
        const Text('NAY-008 / INTERFACE DESIGN ONLY',style:TextStyle(color:Color(0xFF1769FF),fontWeight:FontWeight.bold)),
        const SizedBox(height:8),
        const Text('No license, host-network connection, eSIM provisioning, subscriber registration, payments or certification.'),
        const SizedBox(height:12),
        const Card(child:ListTile(leading:Icon(Icons.lock_outline),
          title:Text('0 connected interfaces · 0 verified gates',key:Key('carrier-blocked')),
          subtitle:Text('SIMULATION_ONLY — all real network operations blocked.'))),
        const SizedBox(height:14),
        const Text('Interface boundaries',style:TextStyle(fontSize:18,fontWeight:FontWeight.bold)),
        for(final item in report.boundaries)
          ListTile(leading:const Icon(Icons.block_outlined),title:Text(item['label']!),
            subtitle:Text('BLOCKED — ${item['detail']}')),
        SwitchListTile.adaptive(key:const Key('carrier-show-evidence'),
          value:showEvidence,onChanged:(v)=>setState(()=>showEvidence=v),
          title:const Text('View missing certification evidence'),
          subtitle:const Text('Educational checklist, not an approval workflow')),
        if(showEvidence) ...[
          const Text('All evidence is NOT VERIFIED',style:TextStyle(fontWeight:FontWeight.bold)),
          for(final item in report.gates) ListTile(title:Text(item['label']!),
            subtitle:const Text('NOT VERIFIED')),
        ],
        const Text('Public design demonstration only. No carrier API requests are made.'),
      ]);
    },
  );
}
