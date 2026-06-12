import 'sso_platform_impl.dart'
    if (dart.library.html) 'sso_web_impl.dart';

class SsoService {
  Future<Map<String, dynamic>?> login() => platformSsoLogin();
  Future<void> logout() => platformSsoLogout();
  Future<bool> get isLoggedIn => platformSsoIsLoggedIn;

  /// Checks for a SSO callback in the URL on web startup.
  /// Returns userInfo map if a code was exchanged, null otherwise.
  Future<Map<String, dynamic>?> checkWebCallback() => handleWebCallback();
}

final ssoService = SsoService();
