import 'package:dio/dio.dart';
import 'package:flutter/foundation.dart';
import 'package:flutter_secure_storage/flutter_secure_storage.dart';

const _baseUrl = String.fromEnvironment(
  'API_BASE_URL',
  defaultValue: 'https://fintech-chatbot-api.onrender.com/api',
);

class ApiService {
  late final Dio _dio;
  final _storage = const FlutterSecureStorage();

  ApiService() {
    _dio = Dio(BaseOptions(
      baseUrl: _baseUrl,
      connectTimeout: const Duration(seconds: 10),
      receiveTimeout: const Duration(seconds: 15),
      headers: {'Content-Type': 'application/json'},
    ));

    _dio.interceptors.add(InterceptorsWrapper(
      onRequest: (options, handler) async {
        final token = await _storage.read(key: 'access_token');
        if (token != null && !_isAuthEndpoint(options.path)) {
          options.headers['Authorization'] = 'Bearer $token';
        }
        handler.next(options);
      },
      onError: (error, handler) async {
        if (error.response?.statusCode == 401 &&
            !_isAuthEndpoint(error.requestOptions.path)) {
          final refreshed = await _refreshToken();
          if (refreshed) {
            final token = await _storage.read(key: 'access_token');
            error.requestOptions.headers['Authorization'] = 'Bearer $token';
            final response = await _dio.fetch(error.requestOptions);
            handler.resolve(response);
            return;
          }
        }
        handler.next(error);
      },
    ));
  }

  bool _isAuthEndpoint(String path) =>
      path.contains('/auth/login/') ||
      path.contains('/auth/register/') ||
      path.contains('/auth/refresh/');

  // ── Auth ──────────────────────────────────────────────────────────────────

  Future<bool> login(String username, String password) async {
    try {
      await logout();
      final cleanUsername = username.trim();
      final res = await _dio.post('/auth/login/', data: {
        'username': cleanUsername,
        'password': password,
      });
      final access = res.data['access'] as String?;
      final refresh = res.data['refresh'] as String?;
      if (access == null || refresh == null) return false;
      await _storage.write(key: 'access_token', value: access);
      await _storage.write(key: 'refresh_token', value: refresh);

      final profile = await getProfile();
      if (profile == null ||
          (profile['username'] != cleanUsername &&
              profile['email'] != cleanUsername)) {
        await logout();
        return false;
      }

      return true;
    } catch (_) {
      await logout();
      return false;
    }
  }

  Future<bool> register(String username, String email, String password,
      {String phone = ''}) async {
    try {
      final res = await _dio.post('/auth/register/', data: {
        'username': username.trim(),
        'email': email.trim(),
        'password': password,
        'phone': phone.trim(),
      });
      final access = res.data['access'] as String?;
      final refresh = res.data['refresh'] as String?;
      if (access != null && refresh != null) {
        await _storage.write(key: 'access_token', value: access);
        await _storage.write(key: 'refresh_token', value: refresh);
      }
      return true;
    } catch (_) {
      return false;
    }
  }

  Future<bool> _refreshToken() async {
    try {
      final refresh = await _storage.read(key: 'refresh_token');
      if (refresh == null) return false;
      final res = await Dio()
          .post('$_baseUrl/auth/refresh/', data: {'refresh': refresh});
      await _storage.write(key: 'access_token', value: res.data['access']);
      return true;
    } catch (_) {
      return false;
    }
  }

  Future<void> logout() => _storage.deleteAll();

  Future<bool> get isLoggedIn async {
    final token = await _storage.read(key: 'access_token');
    return token != null;
  }

  // ── PIN ──────────────────────────────────────────────────────────────────

  Future<bool> hasPinSet() async {
    try {
      final res = await _dio.get('/auth/pin/status/');
      return res.data['has_pin'] == true;
    } catch (_) { return false; }
  }

  Future<Map<String, dynamic>> setPin(String pin) async {
    try {
      final res = await _dio.post('/auth/pin/set/', data: {'pin': pin});
      return {'success': true, 'message': res.data['message']};
    } on DioException catch (e) {
      return {'success': false, 'error': e.response?.data?['error'] ?? 'Failed to set PIN'};
    } catch (_) {
      return {'success': false, 'error': 'Failed to set PIN'};
    }
  }

  Future<bool> verifyPin(String pin) async {
    try {
      await _dio.post('/auth/pin/verify/', data: {'pin': pin});
      return true;
    } catch (_) { return false; }
  }

  Future<Map<String, dynamic>> findAccountByEmail(String email) async {
    try {
      final res = await _dio.post('/auth/find-account/', data: {'email': email.trim()});
      return {'found': true, 'username': res.data['username']};
    } on DioException catch (e) {
      if (e.response?.statusCode == 404) return {'found': false};
      return {'found': false};
    } catch (_) {
      return {'found': false};
    }
  }

  Future<Map<String, dynamic>> resetPassword(
      String username, String email, String newPassword) async {
    try {
      final res = await _dio.post('/auth/reset-password/', data: {
        'username': username.trim(),
        'email': email.trim(),
        'new_password': newPassword,
      });
      return {'success': true, 'message': res.data['message'] ?? 'Password reset successfully.'};
    } on DioException catch (e) {
      final msg = e.response?.data is Map
          ? (e.response!.data['error'] ?? 'Reset failed.')
          : 'Reset failed.';
      return {'success': false, 'message': msg.toString()};
    } catch (_) {
      return {'success': false, 'message': 'Could not connect to server.'};
    }
  }

  Future<Map<String, dynamic>?> getProfile() async {
    try {
      final res = await _dio.get('/auth/profile/');
      return Map<String, dynamic>.from(res.data as Map);
    } catch (_) {
      return null;
    }
  }

  // ── Chat ──────────────────────────────────────────────────────────────────

  Future<Map<String, dynamic>?> sendMessage(String message,
      {String? sessionId}) async {
    try {
      final res = await _dio.post('/chat/message/', data: {
        'message': message,
        if (sessionId != null) 'session_id': sessionId,
      });
      return res.data as Map<String, dynamic>;
    } on DioException catch (error) {
      final statusCode = error.response?.statusCode;
      final responseData = error.response?.data;
      debugPrint('Chat API failed: ${statusCode ?? error.type} $responseData');
      return {
        'error': responseData is Map && responseData['error'] != null
            ? responseData['error'].toString()
            : 'Chat backend is unavailable. Check that Django is running and the API URL is correct.',
        if (statusCode != null) 'status_code': statusCode,
      };
    } catch (error) {
      debugPrint('Chat API failed: $error');
      return {
        'error': 'Chat backend is unavailable. Check that Django is running and the API URL is correct.',
      };
    }
  }

  Future<List<dynamic>> getSessions() async {
    try {
      final res = await _dio.get('/chat/sessions/');
      return res.data as List<dynamic>;
    } catch (_) {
      return [];
    }
  }

  Future<Map<String, dynamic>?> getSession(String sessionId) async {
    try {
      final res = await _dio.get('/chat/sessions/$sessionId/');
      return res.data as Map<String, dynamic>;
    } catch (_) {
      return null;
    }
  }

  // ── Wallet ────────────────────────────────────────────────────────────────

  Future<Map<String, dynamic>?> getWalletBalance() async {
    try {
      final res = await _dio.get('/wallet/balance/');
      return res.data as Map<String, dynamic>;
    } catch (_) {
      return null;
    }
  }

  Future<List<dynamic>> getTransactions() async {
    try {
      final res = await _dio.get('/wallet/transactions/');
      return res.data as List<dynamic>;
    } catch (_) {
      return [];
    }
  }

  Future<Map<String, dynamic>?> transfer(
      String phone, double amount, {required String pin}) async {
    try {
      final res = await _dio.post('/wallet/transfer/', data: {
        'phone': phone, 'amount': amount, 'pin': pin,
      });
      return res.data as Map<String, dynamic>;
    } on DioException catch (e) {
      return {'success': false, 'error': e.response?.data?['error'] ?? 'Transfer failed'};
    } catch (_) {
      return {'success': false, 'error': 'Transfer failed'};
    }
  }

  Future<Map<String, dynamic>?> topup(String phone, double amount, {required String pin}) async {
    try {
      final res = await _dio.post('/wallet/topup/', data: {
        'phone': phone, 'amount': amount, 'pin': pin,
      });
      return res.data as Map<String, dynamic>;
    } on DioException catch (e) {
      return {'success': false, 'error': e.response?.data?['error'] ?? 'Top-up failed'};
    } catch (_) {
      return {'success': false, 'error': 'Top-up failed'};
    }
  }

  Future<Map<String, dynamic>?> payBill(String billType, double amount,
      {String reference = '', required String pin}) async {
    try {
      final res = await _dio.post('/wallet/pay-bill/', data: {
        'bill_type': billType, 'amount': amount, 'reference': reference, 'pin': pin,
      });
      return res.data as Map<String, dynamic>;
    } on DioException catch (e) {
      return {'success': false, 'error': e.response?.data?['error'] ?? 'Payment failed'};
    } catch (_) {
      return {'success': false, 'error': 'Payment failed'};
    }
  }

  Future<Map<String, dynamic>?> sendMessageWithPin(String message,
      {String? sessionId, String pin = ''}) async {
    try {
      final res = await _dio.post('/chat/message/', data: {
        'message': message,
        if (sessionId != null) 'session_id': sessionId,
        if (pin.isNotEmpty) 'pin': pin,
      });
      return res.data as Map<String, dynamic>;
    } on DioException catch (error) {
      final statusCode = error.response?.statusCode;
      final responseData = error.response?.data;
      return {
        'error': responseData is Map && responseData['error'] != null
            ? responseData['error'].toString()
            : 'Chat backend is unavailable.',
        if (statusCode != null) 'status_code': statusCode,
      };
    } catch (_) {
      return {'error': 'Chat backend is unavailable.'};
    }
  }
}

final apiService = ApiService();
