import 'package:flutter/material.dart';
import 'plan_catalog_view.dart';
import 'esim_readiness_wizard.dart';
import 'account_lab.dart';
import 'billing_sandbox.dart';

void main() => runApp(const NayveloApp());

class NayveloApp extends StatelessWidget {
  const NayveloApp({super.key});
  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'NAYVELO Mobile — Prototype',
      debugShowCheckedModeBanner: false,
      theme: ThemeData(
        colorScheme: ColorScheme.fromSeed(seedColor: const Color(0xFF1769FF)),
        scaffoldBackgroundColor: const Color(0xFFF7FAFF),
        useMaterial3: true,
      ),
      home: const NayveloHome(),
    );
  }
}

class NayveloHome extends StatefulWidget {
  const NayveloHome({super.key});
  @override
  State<NayveloHome> createState() => _NayveloHomeState();
}

class _NayveloHomeState extends State<NayveloHome> {
  int tab = 0;
  static const navy = Color(0xFF071D45);
  static const titles = ['Experience', 'Plans', 'eSIM', 'Account lab', 'Usage lab'];

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('◈ NAYVELO', style: TextStyle(fontWeight: FontWeight.w800, letterSpacing: 2, color: navy))),
      body: SafeArea(
        child: ListView(
          key: ValueKey('page-$tab'),
          padding: const EdgeInsets.all(24),
          children: [
            const Text('PROTOTYPE · NO ACTIVE NETWORK', style: TextStyle(color: Color(0xFF1769FF), fontWeight: FontWeight.w800, fontSize: 11)),
            const SizedBox(height: 18),
            Text(titles[tab], style: const TextStyle(fontSize: 35, letterSpacing: -1.3, fontWeight: FontWeight.bold, color: navy)),
            const SizedBox(height: 16),
            if (tab == 0) ...[
              const Text('Mobile, made digital.', style: TextStyle(fontSize: 23, color: navy, fontWeight: FontWeight.w700)),
              const SizedBox(height: 14),
              const Text('Meet a future mobile connectivity experience designed for Nigeria, without physical SIM cards.'),
              const SizedBox(height: 24),
              const Card(child: Padding(padding: EdgeInsets.all(20), child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
                Text('A simpler digital journey', style: TextStyle(fontWeight: FontWeight.bold, fontSize: 17)),
                SizedBox(height: 8),
                Text('Explore plan concepts and eSIM-readiness guidance. Purchases and activation are not available.'),
              ]))),
            ] else if (tab == 1) ...[
              const PlanCatalogView(),
            ] else if (tab == 2) ...[
              const Text('eSIM is a digital network profile for supported phones.'),
              const SizedBox(height: 16),
              const Card(child: ListTile(leading: Icon(Icons.phonelink_setup), title: Text('Check your phone settings'), subtitle: Text('Look for Add eSIM or Add mobile plan. Device and licensed carrier verification is still required.'))),
              const SizedBox(height: 8),
              const Text('NAYVELO cannot issue an eSIM, verify a device or activate service at this stage.'),
              const SizedBox(height: 16),
              const EsimReadinessWizard(),
            ] else if (tab == 3) ...[
              const AccountLab(),
            ] else ...[
              const BillingSandbox(),
            ],
          ],
        ),
      ),
      bottomNavigationBar: NavigationBar(
        selectedIndex: tab,
        onDestinationSelected: (i) => setState(() => tab = i),
        destinations: const [
          NavigationDestination(icon: Icon(Icons.home_outlined), label: 'Home'),
          NavigationDestination(icon: Icon(Icons.layers_outlined), label: 'Plans'),
          NavigationDestination(icon: Icon(Icons.sim_card_outlined), label: 'eSIM'),
          NavigationDestination(icon: Icon(Icons.manage_accounts_outlined), label: 'Account'),
          NavigationDestination(icon: Icon(Icons.bar_chart_outlined), label: 'Usage'),
        ],
      ),
    );
  }
}
