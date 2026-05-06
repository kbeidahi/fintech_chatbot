// lib/screens/wallet_screen.dart
import 'package:flutter/material.dart';
import 'package:google_fonts/google_fonts.dart';
import 'package:intl/intl.dart';
import '../services/api_service.dart';

class WalletScreen extends StatefulWidget {
  const WalletScreen({super.key});

  @override
  State<WalletScreen> createState() => _WalletScreenState();
}

class _WalletScreenState extends State<WalletScreen> {
  Map<String, dynamic>? _wallet;
  List<dynamic> _transactions = [];
  bool _loading = true;

  @override
  void initState() {
    super.initState();
    _load();
  }

  Future<void> _load() async {
    final wallet = await apiService.getWalletBalance();
    final txns = await apiService.getTransactions();
    if (mounted) {
      setState(() {
        _wallet = wallet;
        _transactions = txns;
        _loading = false;
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: const Color(0xFFF5F7FA),
      appBar: AppBar(title: const Text('My Wallet / محفظتي')),
      body: _loading
          ? const Center(child: CircularProgressIndicator())
          : RefreshIndicator(
              onRefresh: _load,
              child: SingleChildScrollView(
                physics: const AlwaysScrollableScrollPhysics(),
                padding: const EdgeInsets.all(16),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    _buildBalanceCard(),
                    const SizedBox(height: 24),
                    _buildQuickActions(),
                    const SizedBox(height: 24),
                    _buildTransactions(),
                  ],
                ),
              ),
            ),
    );
  }

  Widget _buildBalanceCard() {
    final balance = _wallet?['balance'] ?? '0.00';
    final currency = _wallet?['currency'] ?? 'MRU';

    return Container(
      width: double.infinity,
      padding: const EdgeInsets.all(24),
      decoration: BoxDecoration(
        gradient: const LinearGradient(
          colors: [Color(0xFF1B4FD8), Color(0xFF3B6FFF)],
          begin: Alignment.topLeft,
          end: Alignment.bottomRight,
        ),
        borderRadius: BorderRadius.circular(20),
        boxShadow: [
          BoxShadow(
            color: const Color(0xFF1B4FD8).withOpacity(0.3),
            blurRadius: 20,
            offset: const Offset(0, 8),
          ),
        ],
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              Text('Available Balance / الرصيد المتاح',
                  style: GoogleFonts.cairo(
                      color: Colors.white70, fontSize: 13)),
              const Icon(Icons.account_balance_wallet,
                  color: Colors.white70, size: 20),
            ],
          ),
          const SizedBox(height: 12),
          Text('$balance $currency',
              style: GoogleFonts.inter(
                  color: Colors.white,
                  fontSize: 32,
                  fontWeight: FontWeight.w700)),
          const SizedBox(height: 8),
          Text(_wallet?['username'] ?? '',
              style: GoogleFonts.inter(
                  color: Colors.white60, fontSize: 13)),
        ],
      ),
    );
  }

  Widget _buildQuickActions() {
    final actions = [
      {'icon': Icons.send_rounded, 'label': 'Transfer\nتحويل', 'color': const Color(0xFF1B4FD8)},
      {'icon': Icons.phone_android_rounded, 'label': 'Top Up\nشحن', 'color': const Color(0xFF0EA875)},
      {'icon': Icons.receipt_long_rounded, 'label': 'Bills\nفواتير', 'color': const Color(0xFFF59E0B)},
      {'icon': Icons.atm_rounded, 'label': 'Withdraw\nسحب', 'color': const Color(0xFFEF4444)},
    ];

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text('Quick Actions / إجراءات سريعة',
            style: GoogleFonts.cairo(
                fontSize: 16,
                fontWeight: FontWeight.w600,
                color: const Color(0xFF1A1A2E))),
        const SizedBox(height: 12),
        Row(
          mainAxisAlignment: MainAxisAlignment.spaceBetween,
          children: actions.map((a) => _ActionButton(
            icon: a['icon'] as IconData,
            label: a['label'] as String,
            color: a['color'] as Color,
            onTap: () {},
          )).toList(),
        ),
      ],
    );
  }

  Widget _buildTransactions() {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text('Recent Transactions / المعاملات الأخيرة',
            style: GoogleFonts.cairo(
                fontSize: 16,
                fontWeight: FontWeight.w600,
                color: const Color(0xFF1A1A2E))),
        const SizedBox(height: 12),
        if (_transactions.isEmpty)
          Center(
            child: Padding(
              padding: const EdgeInsets.all(32),
              child: Text('No transactions yet\nلا توجد معاملات بعد',
                  textAlign: TextAlign.center,
                  style: GoogleFonts.cairo(
                      color: Colors.grey[400], fontSize: 14)),
            ),
          )
        else
          ...(_transactions.map((t) => _TransactionTile(transaction: t))),
      ],
    );
  }
}

class _ActionButton extends StatelessWidget {
  final IconData icon;
  final String label;
  final Color color;
  final VoidCallback onTap;

  const _ActionButton({
    required this.icon,
    required this.label,
    required this.color,
    required this.onTap,
  });

  @override
  Widget build(BuildContext context) {
    return InkWell(
      onTap: onTap,
      borderRadius: BorderRadius.circular(16),
      child: Container(
        width: 76,
        padding: const EdgeInsets.symmetric(vertical: 14),
        decoration: BoxDecoration(
          color: Colors.white,
          borderRadius: BorderRadius.circular(16),
          boxShadow: [
            BoxShadow(
                color: Colors.black.withOpacity(0.06),
                blurRadius: 8,
                offset: const Offset(0, 2))
          ],
        ),
        child: Column(
          children: [
            Container(
              padding: const EdgeInsets.all(10),
              decoration: BoxDecoration(
                color: color.withOpacity(0.1),
                shape: BoxShape.circle,
              ),
              child: Icon(icon, color: color, size: 22),
            ),
            const SizedBox(height: 8),
            Text(label,
                textAlign: TextAlign.center,
                style: GoogleFonts.cairo(
                    fontSize: 10,
                    fontWeight: FontWeight.w600,
                    color: const Color(0xFF1A1A2E))),
          ],
        ),
      ),
    );
  }
}

class _TransactionTile extends StatelessWidget {
  final Map<String, dynamic> transaction;
  const _TransactionTile({required this.transaction});

  IconData _getIcon(String type) {
    switch (type) {
      case 'transfer': return Icons.send_rounded;
      case 'phone_topup': return Icons.phone_android_rounded;
      case 'bill_payment': return Icons.receipt_long_rounded;
      case 'withdrawal': return Icons.atm_rounded;
      case 'gimtel': return Icons.swap_horiz_rounded;
      default: return Icons.monetization_on_rounded;
    }
  }

  Color _getColor(String type) {
    switch (type) {
      case 'transfer': return const Color(0xFF1B4FD8);
      case 'phone_topup': return const Color(0xFF0EA875);
      case 'bill_payment': return const Color(0xFFF59E0B);
      case 'withdrawal': return const Color(0xFFEF4444);
      case 'gimtel': return const Color(0xFF8B5CF6);
      default: return Colors.grey;
    }
  }

  @override
  Widget build(BuildContext context) {
    final type = transaction['transaction_type'] ?? 'transfer';
    final amount = transaction['amount'] ?? '0';
    final status = transaction['status'] ?? 'success';
    final date = transaction['created_at'] != null
        ? DateFormat('MMM d, HH:mm').format(DateTime.parse(transaction['created_at']).toLocal())
        : '';
    final color = _getColor(type);

    return Container(
      margin: const EdgeInsets.only(bottom: 10),
      padding: const EdgeInsets.all(14),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(14),
        boxShadow: [
          BoxShadow(
              color: Colors.black.withOpacity(0.05),
              blurRadius: 8,
              offset: const Offset(0, 2))
        ],
      ),
      child: Row(
        children: [
          Container(
            padding: const EdgeInsets.all(10),
            decoration: BoxDecoration(
              color: color.withOpacity(0.1),
              borderRadius: BorderRadius.circular(12),
            ),
            child: Icon(_getIcon(type), color: color, size: 20),
          ),
          const SizedBox(width: 12),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(type.replaceAll('_', ' ').toUpperCase(),
                    style: GoogleFonts.inter(
                        fontWeight: FontWeight.w600,
                        fontSize: 13,
                        color: const Color(0xFF1A1A2E))),
                Text(date,
                    style: GoogleFonts.inter(
                        fontSize: 11, color: Colors.grey[500])),
              ],
            ),
          ),
          Column(
            crossAxisAlignment: CrossAxisAlignment.end,
            children: [
              Text('-$amount MRU',
                  style: GoogleFonts.inter(
                      fontWeight: FontWeight.w700,
                      fontSize: 14,
                      color: const Color(0xFFEF4444))),
              Container(
                padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 2),
                decoration: BoxDecoration(
                  color: status == 'success'
                      ? const Color(0xFF0EA875).withOpacity(0.1)
                      : Colors.red.withOpacity(0.1),
                  borderRadius: BorderRadius.circular(8),
                ),
                child: Text(status,
                    style: GoogleFonts.inter(
                        fontSize: 10,
                        color: status == 'success'
                            ? const Color(0xFF0EA875)
                            : Colors.red)),
              ),
            ],
          ),
        ],
      ),
    );
  }
}
