// lib/services/api_service.dart
import 'package:dio/dio.dart';
import 'package:flutter_secure_storage/flutter_secure_storage.dart';

const _baseUrl = 'http://localhost:8000/api';

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
        if (token != null) {
          options.headers['Authorization'] = 'Bearer $token';
        }
        handler.next(options);
      },
      onError: (error, handler) async {
        if (error.response?.statusCode == 401) {
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

  // ── Auth ──────────────────────────────────────────────────────────────────

  Future<bool> login(String username, String password) async {
    try {
      final res = await _dio.post('/auth/login/', data: {
        'username': username,
        'password': password,
      });
      await _storage.write(key: 'access_token', value: res.data['access']);
      await _storage.write(key: 'refresh_token', value: res.data['refresh']);
      return true;
    } catch (_) {
      return false;
    }
  }

  Future<bool> register(String username, String email, String password,
      {String phone = ''}) async {
    try {
      await _dio.post('/auth/register/', data: {
        'username': username,
        'email': email,
        'password': password,
        'phone': phone,
      });
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

  Future<void> logout() async => await _storage.deleteAll();

  Future<bool> get isLoggedIn async {
    final token = await _storage.read(key: 'access_token');
    return token != null;
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
    } catch (_) {
      return null;
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
      String username, double amount) async {
    try {
      final res = await _dio.post('/wallet/transfer/', data: {
        'username': username,
        'amount': amount,
      });
      return res.data as Map<String, dynamic>;
    } catch (_) {
      return null;
    }
  }
}

final apiService = ApiService();
