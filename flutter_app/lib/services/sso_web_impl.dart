// Web implementation using dart:html + manual PKCE
// ignore: avoid_web_libraries_in_flutter
import 'dart:html' as html;
import 'dart:convert';
import 'dart:math';
import 'package:crypto/crypto.dart';
import 'package:http/http.dart' as http;

const _clientId = 'QXgsahJWT1cLODdVL6VoJA6p4b0N5pDZXQ9nF159';
const _authEndpoint = 'https://sso-backend-6b1e.onrender.com/o/authorize/';
const _tokenEndpoint = 'https://sso-backend-6b1e.onrender.com/o/token/';
const _userinfoEndpoint = 'https://sso-backend-6b1e.onrender.com/o/userinfo/';
const _scopes = 'openid profile email';

String _generateCodeVerifier() {
  final rand = Random.secure();
  final bytes = List<int>.generate(32, (_) => rand.nextInt(256));
  return base64UrlEncode(bytes).replaceAll('=', '');
}

String _generateCodeChallenge(String verifier) {
  final bytes = utf8.encode(verifier);
  final digest = sha256.convert(bytes);
  return base64UrlEncode(digest.bytes).replaceAll('=', '');
}

String _currentRedirectUri() {
  final uri = Uri.parse(html.window.location.href);
  return '${uri.scheme}://${uri.host}${uri.port != 0 && uri.port != 80 && uri.port != 443 ? ':${uri.port}' : ''}${uri.path.replaceAll(RegExp(r'/+$'), '')}/';
}

Future<Map<String, dynamic>?> platformSsoLogin() async {
  final verifier = _generateCodeVerifier();
  final challenge = _generateCodeChallenge(verifier);
  final redirectUri = _currentRedirectUri();

  html.window.sessionStorage['sso_code_verifier'] = verifier;
  html.window.sessionStorage['sso_redirect_uri'] = redirectUri;

  final authUrl = Uri.parse(_authEndpoint).replace(queryParameters: {
    'response_type': 'code',
    'client_id': _clientId,
    'redirect_uri': redirectUri,
    'scope': _scopes,
    'code_challenge': challenge,
    'code_challenge_method': 'S256',
  });

  html.window.location.href = authUrl.toString();
  return null; // redirect happens, this line never runs
}

Future<Map<String, dynamic>?> handleWebCallback() async {
  final uri = Uri.parse(html.window.location.href);
  final code = uri.queryParameters['code'];
  if (code == null) return null;

  final verifier = html.window.sessionStorage['sso_code_verifier'];
  final redirectUri = html.window.sessionStorage['sso_redirect_uri'] ?? _currentRedirectUri();
  if (verifier == null) return null;

  // Clean the URL (remove ?code= from browser bar)
  html.window.history.replaceState(null, '', uri.path);
  html.window.sessionStorage.remove('sso_code_verifier');
  html.window.sessionStorage.remove('sso_redirect_uri');

  try {
    final tokenResp = await http.post(
      Uri.parse(_tokenEndpoint),
      headers: {'Content-Type': 'application/x-www-form-urlencoded'},
      body: {
        'grant_type': 'authorization_code',
        'code': code,
        'redirect_uri': redirectUri,
        'client_id': _clientId,
        'code_verifier': verifier,
      },
    );
    if (tokenResp.statusCode != 200) return null;
    final tokens = json.decode(tokenResp.body) as Map<String, dynamic>;
    final accessToken = tokens['access_token'] as String?;
    if (accessToken == null) return null;

    // Store in sessionStorage (flutter_secure_storage not available on web)
    html.window.sessionStorage['sso_access_token'] = accessToken;
    if (tokens['id_token'] != null) {
      html.window.sessionStorage['sso_id_token'] = tokens['id_token'].toString();
    }
    if (tokens['refresh_token'] != null) {
      html.window.sessionStorage['sso_refresh_token'] = tokens['refresh_token'].toString();
    }

    final userResp = await http.get(
      Uri.parse(_userinfoEndpoint),
      headers: {'Authorization': 'Bearer $accessToken'},
    );
    if (userResp.statusCode == 200) {
      return json.decode(userResp.body) as Map<String, dynamic>;
    }
    return {'sub': 'unknown'};
  } catch (_) {
    return null;
  }
}

Future<void> platformSsoLogout() async {
  html.window.sessionStorage.remove('sso_access_token');
  html.window.sessionStorage.remove('sso_id_token');
  html.window.sessionStorage.remove('sso_refresh_token');
}

Future<bool> get platformSsoIsLoggedIn async {
  return html.window.sessionStorage.containsKey('sso_access_token');
}
