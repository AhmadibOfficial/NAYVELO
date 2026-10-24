import 'package:flutter/material.dart';

/// NAY-004 offline-only educational guide. No hardware probing, IDs, analytics or networking.
enum EsimDevice { iphone, android, unsure }
enum EsimAnswer { yes, no, unsure }

class ReadinessSummary {
  const ReadinessSummary(this.title, this.explanation);
  final String title;
  final String explanation;
}

ReadinessSummary describeReadiness({
  required EsimDevice? device,
  required EsimAnswer? setting,
  required EsimAnswer? unlocked,
}) {
  if (device == null || setting == null || unlocked == null) {
    return const ReadinessSummary('Complete the guide', 'Answer each question for next steps.');
  }
  if (setting == EsimAnswer.no) {
    return const ReadinessSummary('Check manufacturer guidance',
        'You did not find an eSIM setting. Your specific model or region may not support eSIM. Confirm with your manufacturer.');
  }
  if (unlocked == EsimAnswer.no) {
    return const ReadinessSummary('Ask about network unlocking',
        'Carrier restrictions may prevent another mobile service. Contact your current operator or seller.');
  }
  if (setting == EsimAnswer.yes && unlocked == EsimAnswer.yes) {
    return const ReadinessSummary('Potentially ready for further verification',
        'Your answers suggest eSIM might be available. This is NOT verified compatibility. Carrier verification is still required.');
  }
  return const ReadinessSummary('More checking is needed',
      'You have not confirmed enough details. Carrier verification is still required.');
}

class EsimReadinessWizard extends StatefulWidget {
  const EsimReadinessWizard({super.key});
  @override
  State<EsimReadinessWizard> createState() => _EsimReadinessWizardState();
}

class _EsimReadinessWizardState extends State<EsimReadinessWizard> {
  int _step = 0;
  EsimDevice? _device;
  EsimAnswer? _setting;
  EsimAnswer? _unlocked;

  bool get _canContinue => switch (_step) {
    0 => _device != null,
    1 => _setting != null,
    2 => _unlocked != null,
    _ => false,
  };

  Widget _choice(String text, bool chosen, VoidCallback onTap, String key) =>
      Padding(
        padding: const EdgeInsets.symmetric(vertical: 4),
        child: Semantics(
          selected: chosen,
          button: true,
          child: OutlinedButton.icon(
            key: Key(key),
            onPressed: onTap,
            icon: Icon(chosen ? Icons.radio_button_checked : Icons.radio_button_unchecked),
            label: Text(text),
            style: OutlinedButton.styleFrom(
              alignment: Alignment.centerLeft,
              minimumSize: const Size(double.infinity, 48),
            ),
          ),
        ),
      );

  @override
  Widget build(BuildContext context) {
    final result = describeReadiness(device: _device, setting: _setting, unlocked: _unlocked);
    return Card(
      key: const Key('esim-readiness-wizard'),
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
          const Text('eSIM readiness · self-check only', style: TextStyle(fontWeight: FontWeight.w800, fontSize: 19)),
          const SizedBox(height: 8),
          const Text('Educational simulator. No device scanning, sign-up, activation, or personal data collection.'),
          const SizedBox(height: 14),
          Text(_step == 3 ? 'Step 4 of 4 · Guidance' : 'Step ${_step + 1} of 4',
              key: const Key('wizard-progress'), style: const TextStyle(fontWeight: FontWeight.w600)),
          const SizedBox(height: 10),
          if (_step == 0) ...[
            const Text('Which type of phone do you use?', style: TextStyle(fontWeight: FontWeight.w700)),
            _choice('iPhone (iOS)', _device == EsimDevice.iphone, () => setState(() => _device = EsimDevice.iphone), 'platform-iphone'),
            _choice('Android', _device == EsimDevice.android, () => setState(() => _device = EsimDevice.android), 'platform-android'),
            _choice('Not sure', _device == EsimDevice.unsure, () => setState(() => _device = EsimDevice.unsure), 'platform-unsure'),
          ] else if (_step == 1) ...[
            const Text('Can you see an option to add eSIM in phone settings?', style: TextStyle(fontWeight: FontWeight.w700)),
            if (_device == EsimDevice.iphone)
              const Text('iPhone: Settings → Cellular / Mobile Data → Add eSIM. Regional models may differ.'),
            if (_device == EsimDevice.android)
              const Text('Samsung: Settings → Connections → SIM manager. Pixel: Settings → Network & internet → SIMs. Menus may differ.'),
            if (_device == EsimDevice.unsure)
              const Text('Look up your manufacturer’s device guide. Do not enter or share a device ID.'),
            _answerChoices('setting'),
          ] else if (_step == 2) ...[
            const Text('Is the phone unlocked for other network operators?', style: TextStyle(fontWeight: FontWeight.w700)),
            const Text('iPhone: Settings → General → About → Carrier Lock. Android: ask your mobile operator or seller.'),
            _answerChoices('unlocked'),
          ] else ...[
            Text(result.title, key: const Key('wizard-result-title'), style: const TextStyle(fontSize: 18, fontWeight: FontWeight.w800)),
            const SizedBox(height: 6),
            Text(result.explanation, key: const Key('wizard-result-description')),
            const SizedBox(height: 8),
            const Text('NAYVELO cannot verify a phone, install an eSIM, provide a QR code, sell plans, or activate a line.'),
          ],
          const SizedBox(height: 8),
          Wrap(spacing: 8, runSpacing: 8, children: [
            if (_step > 0) OutlinedButton(
              key: const Key('wizard-back'),
              onPressed: () => setState(() => _step -= 1),
              child: const Text('Back'),
            ),
            if (_step < 3) FilledButton(
              key: const Key('wizard-next'),
              onPressed: _canContinue ? () => setState(() => _step += 1) : null,
              child: Text(_step == 2 ? 'Show guidance' : 'Continue'),
            ),
            if (_step == 3) OutlinedButton(
              key: const Key('wizard-restart'),
              onPressed: () => setState(() {
                _step = 0; _device = null; _setting = null; _unlocked = null;
              }),
              child: const Text('Restart guide'),
            ),
          ]),
          const SizedBox(height: 10),
          const Text('No network or carrier readiness is verified. Carrier verification is still required.',
              style: TextStyle(fontSize: 12, fontWeight: FontWeight.w600)),
        ]),
      ),
    );
  }

  Widget _answerChoices(String kind) {
    final value = kind == 'setting' ? _setting : _unlocked;
    void select(EsimAnswer answer) => setState(() {
      if (kind == 'setting') _setting = answer;
      else _unlocked = answer;
    });
    return Column(children: [
      _choice('Yes', value == EsimAnswer.yes, () => select(EsimAnswer.yes), '$kind-yes'),
      _choice('No', value == EsimAnswer.no, () => select(EsimAnswer.no), '$kind-no'),
      _choice('Not sure', value == EsimAnswer.unsure, () => select(EsimAnswer.unsure), '$kind-unsure'),
    ]);
  }
}
