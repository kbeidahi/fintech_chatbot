import 'sso_platform_impl.dart'
    if (dart.library.html) 'sso_web_impl.dart';
import 'package:http/http.dart' as http;
import 'dart:convert';

const _apiBase = 'https://fintech-chatbot-api.onrender.com/api/auth';

class SsoService {
  Future<Map<String, dynamic>?> login() => platformSsoLogin();
  Future<void> logout() => platformSsoLogout();
  Future<bool> get isLoggedIn => platformSsoIsLoggedIn;
  Future<Map<String, dynamic>?> checkWebCallback() => handleWebCallback();
  bool get hasPendingCallback => platformSsoHasPendingCallback;

  Future<bool> hasPin(String sub) async {
    if (sub.isEmpty) return false;
    try {
      final resp = await http.get(
        Uri.parse('$_apiBase/sso/pin/?sub=${Uri.encodeComponent(sub)}'),
      );
      if (resp.statusCode == 200) {
        return (jsonDecode(resp.body) as Map)['has_pin'] == true;
      }
    } catch (_) {}
    return false;
  }

  Future<void> savePin(String sub) async {
    if (sub.isEmpty) return;
    try {
      await http.post(
        Uri.parse('$_apiBase/sso/pin/'),
        headers: {'Content-Type': 'application/json'},
        body: jsonEncode({'sub': sub}),
      );
    } catch (_) {}
  }
}

final ssoService = SsoService();
