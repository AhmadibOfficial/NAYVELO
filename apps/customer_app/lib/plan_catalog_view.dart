import 'dart:convert';
import 'package:flutter/material.dart';
import 'package:flutter/services.dart';

/// Completely offline proposed plans; no carrier or payment networking.
class ConceptPlan {
  const ConceptPlan(this.data);
  final Map<String, dynamic> data;
  String get code => data['code'] as String;
  String get title => data['title'] as String;
  String get period => data['period'] as String;
  String get audience => data['audience'] as String;
  String get description => data['description'] as String;
  String get unconfirmed => 'Not confirmed';
}

List<ConceptPlan> parseConceptPlans(String raw) {
  final doc = jsonDecode(raw);
  if (doc is! Map<String, dynamic> ||
      doc['mode'] != 'SIMULATION_ONLY' || doc['schema_version'] != 1 ||
      doc['plans'] is! List || (doc['plans'] as List).isEmpty) {
    throw const FormatException('Unsafe catalog');
  }
  final plans = <ConceptPlan>[];
  final seen = <String>{};
  for (final entry in doc['plans'] as List) {
    if (entry is! Map<String, dynamic>) throw const FormatException('Invalid plan');
    for (final k in ['code', 'title', 'period', 'audience', 'description']) {
      if (entry[k] is! String || (entry[k] as String).trim().isEmpty) {
        throw const FormatException('Invalid plan description');
      }
    }
    if (!['Daily', 'Weekly', 'Monthly', 'Trip-based'].contains(entry['period']) ||
        !seen.add(entry['code'] as String) ||
        entry['data_gb'] != null || entry['voice_minutes'] != null ||
        entry['sms_count'] != null || entry['price_ngn'] != null ||
        entry['available_for_purchase'] != false ||
        entry['hotspot'] != 'Not confirmed' ||
        entry['rollover'] != 'Not confirmed') {
      throw const FormatException('Catalog terms not approved');
    }
    plans.add(ConceptPlan(entry));
  }
  return plans;
}

class PlanCatalogView extends StatefulWidget {
  const PlanCatalogView({super.key});
  @override
  State<PlanCatalogView> createState() => _PlanCatalogViewState();
}

class _PlanCatalogViewState extends State<PlanCatalogView> {
  late final Future<List<ConceptPlan>> plansFuture =
      rootBundle.loadString('assets/plans.json').then(parseConceptPlans);
  String duration = 'All durations';
  final Set<String> selected = {};
  bool comparisonOpen = false;
  @override
  Widget build(BuildContext context) {
    return FutureBuilder<List<ConceptPlan>>(
      future: plansFuture,
      builder: (context, snapshot) {
        if (snapshot.hasError) {
          return const Text('Plan concepts unavailable. Purchases and activation are disabled.');
        }
        if (!snapshot.hasData) return const Center(child: CircularProgressIndicator());
        final all = snapshot.data!;
        final visible = all.where((p) => duration == 'All durations' || p.period == duration).toList();
        final compared = all.where((p) => selected.contains(p.code)).toList();
        return Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
          const Text('PLAN CONCEPTS ONLY · NO ACTIVE NETWORK',
              style: TextStyle(fontSize: 12, fontWeight: FontWeight.w700, color: Color(0xFF1769FF))),
          const SizedBox(height: 8),
          const Text('Prices, data, calls and SMS allowances are not confirmed. No purchase or activation is available.'),
          const SizedBox(height: 16),
          DropdownButtonFormField<String>(
            initialValue: duration,
            decoration: const InputDecoration(labelText: 'Filter by duration', border: OutlineInputBorder()),
            items: ['All durations', 'Daily', 'Weekly', 'Monthly', 'Trip-based']
                .map((d) => DropdownMenuItem(value: d, child: Text(d))).toList(),
            onChanged: (value) => setState(() { duration = value ?? 'All durations'; }),
          ),
          const SizedBox(height: 8),
          Text('${visible.length} concept plans shown'),
          const SizedBox(height: 12),
          ...visible.map((p) => Card(
            child: Padding(padding: const EdgeInsets.all(14), child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(p.title, style: Theme.of(context).textTheme.titleLarge),
                Text('${p.period} · ${p.audience}'),
                const SizedBox(height: 6),
                Text(p.description),
                const SizedBox(height: 8),
                const Text('Data: Not confirmed · Voice: Not confirmed · SMS: Not confirmed'),
                const Text('Price: Not confirmed · Hotspot: Not confirmed · Rollover: Not confirmed'),
                const Text('Concept only · Not purchasable',
                    style: TextStyle(fontWeight: FontWeight.w600)),
                CheckboxListTile(
                  contentPadding: EdgeInsets.zero,
                  title: Text('Compare ${p.title}'),
                  value: selected.contains(p.code),
                  onChanged: !selected.contains(p.code) && selected.length >= 3
                      ? null
                      : (bool? value) => setState(() {
                          if (value == true) { selected.add(p.code); }
                          else { selected.remove(p.code); }
                          comparisonOpen = false;
                        }),
                ),
              ],
            )),
          )),
          const SizedBox(height: 12),
          Text('${selected.length} of 3 selected. Choose 2 or 3 plans.'),
          const SizedBox(height: 8),
          FilledButton(
            onPressed: selected.length < 2 ? null : () => setState(() => comparisonOpen = true),
            child: const Text('Compare selected plans'),
          ),
          if (comparisonOpen && compared.length >= 2) ...[
            const SizedBox(height: 18),
            const Text('All prices and allowances are unconfirmed. Comparison is informational only.'),
            SingleChildScrollView(scrollDirection: Axis.horizontal, child: DataTable(
              columns: [const DataColumn(label: Text('Detail')),
                ...compared.map((p) => DataColumn(label: Text(p.title)))],
              rows: [
                _row('Duration', compared.map((p) => p.period)),
                _row('Intended audience', compared.map((p) => p.audience)),
                _row('Mobile data', compared.map((p) => p.unconfirmed)),
                _row('Voice minutes', compared.map((p) => p.unconfirmed)),
                _row('SMS', compared.map((p) => p.unconfirmed)),
                _row('Price (NGN)', compared.map((p) => p.unconfirmed)),
                _row('Purchase', compared.map((p) => 'Unavailable')),
              ],
            )),
          ],
        ]);
      },
    );
  }

  DataRow _row(String title, Iterable<String> values) => DataRow(cells: [
    DataCell(Text(title)), ...values.map((value) => DataCell(Text(value)))
  ]);
}
