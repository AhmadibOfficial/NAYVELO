import 'dart:convert';

import 'package:flutter/material.dart';
import 'package:flutter/services.dart';

/// NAY-006: strictly fictional fixture. Not a price, charge or subscriber record.
class BillingFixture {
  const BillingFixture(this.days, this.history, this.sampleAllowanceMiB);

  final List<int> days;
  final List<Map<String, int>> history;
  final int sampleAllowanceMiB;

  static int estimateKobo(int mib, int rateKoboPerGiB) {
    if (mib < 0 || mib > 1000000 || rateKoboPerGiB <= 0 || rateKoboPerGiB > 10000000) {
      throw const FormatException('Invalid hypothetical quantities');
    }
    return (mib * rateKoboPerGiB + 512) ~/ 1024;
  }

  int get sevenDayMiB => days.fold(0, (a, b) => a + b);
  int get forecast30MiB => (sevenDayMiB * 30 + days.length ~/ 2) ~/ days.length;
  int get remainingMiB => (sampleAllowanceMiB - sevenDayMiB).clamp(0, sampleAllowanceMiB).toInt();

  factory BillingFixture.fromJson(Map<String, dynamic> data) {
    final expectedFields = {
      'schema_version', 'mode', 'source', 'currency', 'usage_unit', 'forecast_days',
      'sample_allowance_mib', 'sample_rate_kobo_per_gib', 'days', 'illustrative_history', 'disclaimer'
    };
    if (data.keys.toSet().difference(expectedFields).isNotEmpty || data.keys.length != expectedFields.length ||
        data['schema_version'] != 1 || data['mode'] != 'SIMULATION_ONLY' ||
        data['source'] != 'FIXED_SYNTHETIC_FIXTURE' || data['currency'] != 'NGN' ||
        data['usage_unit'] != 'MiB' || data['forecast_days'] != 30 ||
        data['sample_allowance_mib'] != 8192 || data['sample_rate_kobo_per_gib'] != 125000 ||
        data['disclaimer'] is! String || !(data['disclaimer'] as String).startsWith('Fictional usage')) {
      throw const FormatException('Unsafe or unexpected simulation fixture');
    }
    final sourceDays = data['days'];
    final sourceHistory = data['illustrative_history'];
    if (sourceDays is! List || sourceDays.length != 7 || sourceHistory is! List || sourceHistory.length != 3) {
      throw const FormatException('Invalid fixture series');
    }
    final days = <int>[];
    for (var i = 0; i < 7; i++) {
      final row = sourceDays[i];
      if (row is! Map || row.keys.toSet().difference({'date', 'usage_mib'}).isNotEmpty ||
          row.length != 2 || row['date'] != '2026-10-${(i + 1).toString().padLeft(2, '0')}' ||
          row['usage_mib'] is! int || row['usage_mib'] < 0 || row['usage_mib'] > 4096) {
        throw const FormatException('Non-synthetic day found');
      }
      days.add(row['usage_mib'] as int);
    }
    final history = <Map<String, int>>[];
    for (var i = 0; i < 3; i++) {
      final row = sourceHistory[i];
      if (row is! Map || row.keys.toSet().difference({'period','usage_mib','estimate_kobo'}).isNotEmpty ||
          row.length != 3 || row['period'] != '2026-${(i + 7).toString().padLeft(2, '0')}' ||
          row['usage_mib'] is! int || row['usage_mib'] < 0 || row['usage_mib'] > 100000 ||
          row['estimate_kobo'] is! int ||
          row['estimate_kobo'] != estimateKobo(row['usage_mib'] as int, 125000)) {
        throw const FormatException('Unsafe historical example');
      }
      history.add({'month': i + 7, 'usage': row['usage_mib'] as int, 'estimate': row['estimate_kobo'] as int});
    }
    return BillingFixture(days, history, 8192);
  }

  static Future<BillingFixture> loadAsset() async {
    final raw = await rootBundle.loadString('assets/synthetic_billing.json');
    return BillingFixture.fromJson(jsonDecode(raw) as Map<String, dynamic>);
  }
}

class BillingSandbox extends StatefulWidget {
  const BillingSandbox({super.key, this.demoFixture});
  final BillingFixture? demoFixture;

  @override
  State<BillingSandbox> createState() => _BillingSandboxState();
}

class _BillingSandboxState extends State<BillingSandbox> {
  late final Future<BillingFixture> _loaded;
  int rateNgnPerGiB = 1250;
  int hypotheticalCapNgn = 5000;

  @override
  void initState() {
    super.initState();
    _loaded = widget.demoFixture == null ? BillingFixture.loadAsset() : Future.value(widget.demoFixture!);
  }

  String money(int kobo) => '₦${(kobo ~/ 100)}.${(kobo % 100).toString().padLeft(2, '0')}';

  @override
  Widget build(BuildContext context) {
    return FutureBuilder<BillingFixture>(
      future: _loaded,
      builder: (context, snap) {
        if (snap.hasError) {
          return const Text('Fictional usage fixture unavailable. No payments or network services can occur.');
        }
        if (!snap.hasData) return const Center(child: CircularProgressIndicator());
        final fixture = snap.data!;
        final estimate = BillingFixture.estimateKobo(fixture.forecast30MiB, rateNgnPerGiB * 100);
        final overCap = estimate > hypotheticalCapNgn * 100;
        return Card(
          child: Padding(
            padding: const EdgeInsets.all(16),
            child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
              const Text('NAY-006 / FICTIONAL USAGE LAB',
                  style: TextStyle(color: Color(0xFF1769FF), fontWeight: FontWeight.bold)),
              const SizedBox(height: 8),
              const Text('Sample usage only. Not your account, network usage, actual tariff, bill or invoice. No payment can be made.'),
              const SizedBox(height: 14),
              Text('Seven-day usage: ${fixture.sevenDayMiB} MiB', key: const Key('billing-used')),
              Text('Remaining fictional allowance: ${fixture.remainingMiB} MiB'),
              Text('30-day projected usage: ${fixture.forecast30MiB} MiB'),
              const SizedBox(height: 12),
              const Text('Synthetic daily usage (MiB)', style: TextStyle(fontWeight: FontWeight.w600)),
              for (var i = 0; i < fixture.days.length; i++)
                Padding(padding: const EdgeInsets.symmetric(vertical: 4), child: Row(children: [
                  SizedBox(width: 50, child: Text('Day ${i + 1}', style: const TextStyle(fontSize: 12))),
                  Expanded(child: LinearProgressIndicator(value: fixture.days[i] / 4096,
                      semanticsLabel: 'Day ${i + 1}: ${fixture.days[i]} MiB')),
                  const SizedBox(width: 10),
                  SizedBox(width: 60, child: Text('${fixture.days[i]} MiB', style: const TextStyle(fontSize: 11))),
                ])),
              const SizedBox(height: 16),
              const Text('Choose hypothetical assumptions (not NAYVELO prices)'),
              DropdownButtonFormField<int>(
                key: const Key('billing-rate'),
                initialValue: rateNgnPerGiB,
                decoration: const InputDecoration(labelText: 'Example rate in ₦ per GiB'),
                items: const [1250, 2000, 3000, 5000].map((v) => DropdownMenuItem(value: v, child: Text('₦$v per GiB'))).toList(),
                onChanged: (v) { if (v != null) setState(() => rateNgnPerGiB = v); },
              ),
              DropdownButtonFormField<int>(
                key: const Key('billing-cap'),
                initialValue: hypotheticalCapNgn,
                decoration: const InputDecoration(labelText: 'Example 30-day spending budget'),
                items: const [3000, 5000, 10000, 20000].map((v) => DropdownMenuItem(value: v, child: Text('₦$v'))).toList(),
                onChanged: (v) { if (v != null) setState(() => hypotheticalCapNgn = v); },
              ),
              const SizedBox(height: 12),
              Text('Illustrative 30-day expense: ${money(estimate)}', key: const Key('billing-estimate'),
                  style: const TextStyle(fontWeight: FontWeight.bold)),
              Semantics(liveRegion: true, child: Text(overCap
                  ? 'Above hypothetical budget — not a charge.' : 'Within hypothetical budget — not a charge.')),
              const SizedBox(height: 12),
              OutlinedButton(onPressed: () => setState(() {rateNgnPerGiB=1250;hypotheticalCapNgn=5000;}),
                  child: const Text('Reset example assumptions')),
              const Divider(height: 26),
              const Text('Fictional historical estimates — no actual invoices',
                  style: TextStyle(fontWeight: FontWeight.w600)),
              for (final h in fixture.history)
                ListTile(dense: true, title: Text('2026-${h['month'].toString().padLeft(2,'0')}'),
                    subtitle: Text('${h['usage']} MiB · Illustration only'),
                    trailing: Text(money(h['estimate']!))),
              const Text('Model: 1 GiB = 1024 MiB. Seven-day average × 30 days. Example rate × projected usage; rounded to kobo. Taxes, fees and live carrier pricing excluded.',
                  style: TextStyle(fontSize: 12)),
            ]),
          ),
        );
      },
    );
  }
}
