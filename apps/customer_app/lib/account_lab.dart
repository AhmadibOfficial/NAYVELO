import 'package:flutter/material.dart';

/// NAY-005: local synthetic subscriber-account lifecycle. No I/O or credentials.
class DemoAccountState {
  DemoAccountState(this.alias)
      : assert(alias == 'DEMO-ALPHA' || alias == 'DEMO-BETA'),
        status = alias == 'DEMO-BETA' ? 'paused' : 'preview';

  final String alias;
  String status;
  bool productAnalytics = false;
  bool productNews = false;

  static const transitions = <String, List<String>>{
    'preview': ['paused', 'locked', 'closed'],
    'paused': ['preview', 'locked', 'closed'],
    'locked': [],
    'closed': [],
  };

  bool permits(String next) => transitions[status]?.contains(next) ?? false;

  void transition(String next) {
    if (!permits(next)) throw StateError('Simulated transition blocked');
    status = next;
  }
}

class AccountLab extends StatefulWidget {
  const AccountLab({super.key});

  @override
  State<AccountLab> createState() => _AccountLabState();
}

class _AccountLabState extends State<AccountLab> {
  DemoAccountState _demo = DemoAccountState('DEMO-ALPHA');
  String _notice = 'Nothing is saved or transmitted.';

  void _transition(String next) => setState(() {
        if (!_demo.permits(next)) return;
        _demo.transition(next);
        _notice = 'Fictional account state changed in this screen only.';
      });

  void _reset() => setState(() {
        _demo = DemoAccountState(_demo.alias);
        _notice = 'Reset complete. All optional privacy choices are off.';
      });

  @override
  Widget build(BuildContext context) {
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(18),
        child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
          const Text('NAY-005 / PRIVACY-FIRST ACCOUNT LAB',
              style: TextStyle(fontSize: 12, fontWeight: FontWeight.w800, color: Color(0xFF1769FF))),
          const SizedBox(height: 10),
          const Text('Fictional subscriber profiles only. No NIN, phone number, credentials, eSIM, real account, login or service activation.'),
          const SizedBox(height: 12),
          DropdownButton<String>(
            key: const Key('demo-alias'),
            isExpanded: true,
            value: _demo.alias,
            items: const [
              DropdownMenuItem(value: 'DEMO-ALPHA', child: Text('Fictional example A')),
              DropdownMenuItem(value: 'DEMO-BETA', child: Text('Fictional example B')),
            ],
            onChanged: (value) => setState(() {
              if (value == null) return;
              _demo = DemoAccountState(value);
              _notice = 'Changed example. Previous local choices discarded.';
            }),
          ),
          const SizedBox(height: 8),
          Text('Local state: ${_demo.status.toUpperCase()}',
              key: const Key('demo-status'),
              style: const TextStyle(fontSize: 18, fontWeight: FontWeight.bold)),
          const SizedBox(height: 10),
          const Text('Try allowed fictional account transitions:'),
          Wrap(spacing: 8, runSpacing: 4, children: [
            for (final target in ['preview', 'paused', 'locked', 'closed'])
              OutlinedButton(
                key: Key('demo-to-$target'),
                onPressed: _demo.permits(target) ? () => _transition(target) : null,
                child: Text(target.toUpperCase()),
              ),
          ]),
          const SizedBox(height: 12),
          const Text('Optional privacy preferences (off by default)',
              style: TextStyle(fontWeight: FontWeight.w700)),
          SwitchListTile(
            key: const Key('demo-analytics'),
            contentPadding: EdgeInsets.zero,
            title: const Text('Product analytics preference'),
            subtitle: const Text('Local preview only; no analytics are collected.'),
            value: _demo.productAnalytics,
            onChanged: (v) => setState(() {
              _demo.productAnalytics = v;
              _notice = 'Preference changed in memory only.';
            }),
          ),
          SwitchListTile(
            key: const Key('demo-news'),
            contentPadding: EdgeInsets.zero,
            title: const Text('Product updates preference'),
            subtitle: const Text('Local preview only; no messages will be sent.'),
            value: _demo.productNews,
            onChanged: (v) => setState(() {
              _demo.productNews = v;
              _notice = 'Preference changed in memory only.';
            }),
          ),
          OutlinedButton.icon(
            key: const Key('demo-reset'),
            onPressed: _reset,
            icon: const Icon(Icons.restart_alt),
            label: const Text('Reset fictional profile'),
          ),
          const SizedBox(height: 10),
          Semantics(liveRegion: true, child: Text(_notice, key: const Key('demo-notice'))),
          const SizedBox(height: 8),
          const Text('Locked and closed states cannot be unlocked in this demonstration. Reset only creates a fresh fictional example, not account recovery.',
              style: TextStyle(fontSize: 12)),
        ]),
      ),
    );
  }
}
