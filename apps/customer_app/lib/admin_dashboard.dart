import 'dart:convert';

import 'package:flutter/material.dart';
import 'package:flutter/services.dart';

/// Demonstrates fictional role-specific views. NEVER authenticates or grants access.
class AdminDemoFixture {
  const AdminDemoFixture(this.weeks, this.planInterest, this.operations);
  final List<Map<String, int>> weeks;
  final List<Map<String, dynamic>> planInterest;
  final List<Map<String, String>> operations;

  int get visits => weeks.fold(0, (n, w) => n + w['visits']!);
  int get previews => weeks.fold(0, (n, w) => n + w['onboarding_previews']!);

  factory AdminDemoFixture.fromJson(Map<String, dynamic> data) {
    const root = {'schema_version','mode','source','period','plan_concepts','weeks','plan_interest','demo_operations','disclaimer'};
    if (data.keys.toSet().difference(root).isNotEmpty || data.length != root.length ||
        data['schema_version'] != 1 || data['mode'] != 'SIMULATION_ONLY' ||
        data['source'] != 'PUBLIC_FIXED_FICTIONAL_DATA' ||
        data['period'] != 'Four invented example weeks; not current activity' ||
        data['plan_concepts'] != 6 || data['disclaimer'] is! String ||
        !(data['disclaimer'] as String).startsWith('Fictional administrative exercise only.') ||
        !(data['disclaimer'] as String).contains('NOT authentication')) {
      throw const FormatException('Unsafe management fixture');
    }
    final rawWeeks = data['weeks'];
    final rawPlans = data['plan_interest'];
    final rawOps = data['demo_operations'];
    if (rawWeeks is! List || rawWeeks.length != 4 || rawPlans is! List || rawPlans.length != 6 ||
        rawOps is! List || rawOps.length != 3) {
      throw const FormatException('Invalid mock aggregates');
    }
    final weeks = <Map<String, int>>[];
    for (var i = 0; i < 4; i++) {
      final w = rawWeeks[i];
      if (w is! Map || w.keys.toSet().difference({'label','visits','onboarding_previews','help_requests'}).isNotEmpty ||
          w.length != 4 || w['label'] != 'Example week ${i + 1}' ||
          w['visits'] is! int || w['onboarding_previews'] is! int || w['help_requests'] is! int ||
          [w['visits'],w['onboarding_previews'],w['help_requests']].any((v) => v < 0 || v > 10000) ||
          w['onboarding_previews'] > w['visits'] || w['help_requests'] > w['visits']) {
        throw const FormatException('Invalid synthetic week');
      }
      weeks.add({'visits': w['visits'] as int, 'onboarding_previews': w['onboarding_previews'] as int,
        'help_requests': w['help_requests'] as int});
    }
    const codes = ['daily-flex','smart-weekly','monthly-plus','family-connect','business-pro','global-roam'];
    final plans = <Map<String, dynamic>>[];
    for(var i=0;i<6;i++) {
      final p=rawPlans[i];
      if(p is! Map || p.keys.toSet().difference({'code','count'}).isNotEmpty || p.length!=2 ||
         p['code']!=codes[i] || p['count'] is! int || p['count']<0 || p['count']>10000) {
        throw const FormatException('Invalid synthetic plan interest');
      }
      plans.add({'code':p['code'] as String,'count':p['count'] as int});
    }
    const opsCodes=['documentation','support','partnership'];
    const opsLabels=['Readiness guide review','Simulated support queue','Carrier integration prerequisite'];
    final operations=<Map<String,String>>[];
    for(var i=0;i<3;i++) {
      final op=rawOps[i];
      if(op is! Map || op.keys.toSet().difference({'code','label','state'}).isNotEmpty || op.length!=3 ||
        op['code']!=opsCodes[i] || op['label']!=opsLabels[i] ||
        op['state']!=(i==2?'not_authorized':'illustrative_only')) {
        throw const FormatException('Unsafe mock operation');
      }
      operations.add({'label':op['label'] as String,'state':op['state'] as String});
    }
    return AdminDemoFixture(weeks,plans,operations);
  }

  static Future<AdminDemoFixture> loadAsset() async {
    final raw=await rootBundle.loadString('assets/synthetic_admin.json');
    return AdminDemoFixture.fromJson(jsonDecode(raw) as Map<String,dynamic>);
  }
}

class AdminDashboardDemo extends StatefulWidget {
  const AdminDashboardDemo({super.key, this.demoFixture});
  final AdminDemoFixture? demoFixture;

  @override
  State<AdminDashboardDemo> createState()=>_AdminDashboardDemoState();
}

class _AdminDashboardDemoState extends State<AdminDashboardDemo> {
  late final Future<AdminDemoFixture> _loaded;
  String role='viewer';

  @override
  void initState() {
    super.initState();
    _loaded=widget.demoFixture==null?AdminDemoFixture.loadAsset():Future.value(widget.demoFixture!);
  }

  @override
  Widget build(BuildContext context) => FutureBuilder<AdminDemoFixture>(
    future:_loaded,
    builder:(context,snap) {
      if(snap.hasError)return const Text('Fictional admin fixture unavailable. No account or admin services can run.');
      if(!snap.hasData)return const Center(child:CircularProgressIndicator());
      final f=snap.data!;
      return Column(crossAxisAlignment:CrossAxisAlignment.start,children:[
        const Text('NAY-007 / MANAGEMENT EXPERIENCE DEMO',style:TextStyle(fontWeight:FontWeight.bold,color:Color(0xFF1769FF))),
        const SizedBox(height:8),
        const Text('PUBLIC, FICTIONAL EXERCISE ONLY — no real subscriber activity, revenue, telecom operations or authenticated admin access.'),
        const SizedBox(height:8),
        const Text('Changing mock roles only changes this screen. It is NOT authentication or authorization.'),
        const SizedBox(height:12),
        DropdownButtonFormField<String>(
          key:const Key('demo-admin-role'),
          initialValue:role,
          decoration:const InputDecoration(labelText:'Fictional role (no login)'),
          items:const ['viewer','analyst','operator'].map((v)=>DropdownMenuItem(value:v,child:Text(v))).toList(),
          onChanged:(v){if(v!=null)setState(()=>role=v);},
        ),
        const SizedBox(height:16),
        Card(child:Padding(padding:const EdgeInsets.all(14),child:Column(crossAxisAlignment:CrossAxisAlignment.start,children:[
          Text('Example visits: ${f.visits}',key:const Key('admin-visits')),
          Text('Example onboarding previews: ${f.previews}'),
          const Text('Unpriced plan concepts: 6'),
        ]))),
        if(role!='viewer') ...[
          const SizedBox(height:14),
          const Text('Synthetic weekly activity',style:TextStyle(fontWeight:FontWeight.bold)),
          for(var i=0;i<f.weeks.length;i++)
            Padding(padding:const EdgeInsets.symmetric(vertical:5),child:Row(children:[
              SizedBox(width:70,child:Text('Week ${i+1}')),
              Expanded(child:LinearProgressIndicator(value:f.weeks[i]['visits']!/180,
                semanticsLabel:'Fictional visits example week ${i+1}: ${f.weeks[i]['visits']}')),
              const SizedBox(width:10),Text('${f.weeks[i]['visits']}'),
            ])),
          const SizedBox(height:12),
          const Text('Fictional plan interest — no subscriber records',style:TextStyle(fontWeight:FontWeight.bold)),
          for(final p in f.planInterest)Text('${p['code']}: ${p['count']} invented interest events'),
        ] else const Text('Trends hidden in the viewer demonstration.'),
        if(role=='operator') ...[
          const SizedBox(height:12),
          const Text('Read-only operational scenarios',style:TextStyle(fontWeight:FontWeight.bold)),
          for(final item in f.operations)Text('${item['label']}: ${item['state']}'),
        ],
        const SizedBox(height:12),
        Semantics(liveRegion:true,child:Text('Simulated role: $role. No permissions granted.')),
      ]);
    },
  );
}
