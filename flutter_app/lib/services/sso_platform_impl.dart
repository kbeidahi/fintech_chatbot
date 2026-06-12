// Mobile implementation using flutter_appauth (flutter_appauth v6 API)
import 'package:flutter_appauth/flutter_appauth.dart';
import 'package:flutter_secure_storage/flutter_secure_storage.dart';
import 'package:http/http.dart' as http;
import 'dart:convert';

const _clientId = 'QXgsahJWT1cLODdVL6VoJA6p4b0N5pDZXQ9nF159';
const _redirectUrl = 'http://localhost';
const _discoveryUrl =
    'https://sso-backend-6b1e.onrender.com/.well-known/openid-configuration';
const _scopes = ['openid', 'profile', 'email'];

final _appAuth = FlutterAppAuth();
final _storage = const FlutterSecureStorage();

Future<Map<String, dynamic>?> platformSsoLogin() async {
  try {
    final result = await _appAuth.authorizeAndExchangeCode(
      AuthorizationTokenRequest(
        _clientId,
        _redirectUrl,
        discoveryUrl: _discoveryUrl,
        scopes: _scopes,
      ),
    );
    if (result == null || result.accessToken == null) return null;

    await _storage.write(key: 'sso_access_token', value: result.accessToken);
    if (result.idToken != null) {
      await _storage.write(key: 'sso_id_token', value: result.idToken);
    }
    if (result.refreshToken != null) {
      await _storage.write(key: 'sso_refresh_token', value: result.refreshToken);
    }
    return await _fetchUserInfo(result.accessToken!);
  } catch (_) {
    return null;
  }
}

Future<Map<String, dynamic>?> _fetchUserInfo(String accessToken) async {
  try {
    final response = await http.get(
      Uri.parse('https://sso-backend-6b1e.onrender.com/o/userinfo/'),
      headers: {'Authorization': 'Bearer $accessToken'},
    );
    if (response.statusCode == 200) {
      return json.decode(response.body) as Map<String, dynamic>;
    }
    return null;
  } catch (_) {
    return null;
  }
}

Future<void> platformSsoLogout() async {
  await _storage.delete(key: 'sso_access_token');
  await _storage.delete(key: 'sso_id_token');
  await _storage.delete(key: 'sso_refresh_token');
}

Future<bool> get platformSsoIsLoggedIn async {
  final token = await _storage.read(key: 'sso_access_token');
  return token != null;
}

// No-op on mobile — only used on web
Future<Map<String, dynamic>?> handleWebCallback() async => null;
