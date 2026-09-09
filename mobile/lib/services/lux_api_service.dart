import 'dart:async';
import 'dart:convert';
import 'dart:io';
import 'package:http/http.dart' as http;
import '../models/level.dart';

/// Base exception class for Lux API errors.
abstract class LuxApiException implements Exception {
  final String message;
  final dynamic details;

  const LuxApiException(this.message, [this.details]);

  @override
  String toString() => message;
}

/// Thrown when network connection fails, times out, or server is unreachable.
class LuxNetworkException extends LuxApiException {
  final String serverUrl;

  const LuxNetworkException({
    required this.serverUrl,
    String? message,
    dynamic details,
  }) : super(
          message ??
              'Unable to connect to the Lux server at $serverUrl.\n\n'
                  'Please ensure the Lux server is running (e.g., run "python server.py") '
                  'or verify the server URL in settings.',
          details,
        );
}

/// Thrown when the server returns a non-200 HTTP status code.
class LuxHttpException extends LuxApiException {
  final int statusCode;
  final String responseBody;

  const LuxHttpException({
    required this.statusCode,
    required this.responseBody,
    String? message,
  }) : super(
          message ??
              'Server returned HTTP $statusCode error. Please verify the API status.',
          responseBody,
        );
}

/// Thrown when the API response cannot be decoded or is not in the expected list format.
class LuxFormatException extends LuxApiException {
  const LuxFormatException({
    String? message,
    dynamic details,
  }) : super(
          message ??
              'Received invalid or malformed data from the server. '
                  'Expected a list of puzzle levels.',
          details,
        );
}

/// Service for interacting with the Lux API server.
class LuxApiService {
  static const String defaultBaseUrl = String.fromEnvironment(
    'LUX_BASE_URL',
    defaultValue: 'http://127.0.0.1:5050',
  );

  String _baseUrl;
  final http.Client _client;
  final Duration timeout;

  LuxApiService({
    String baseUrl = defaultBaseUrl,
    http.Client? client,
    this.timeout = const Duration(seconds: 10),
  })  : _baseUrl = _normalizeBaseUrl(baseUrl),
        _client = client ?? http.Client();

  /// Gets the currently configured base URL.
  String get baseUrl => _baseUrl;

  /// Updates the base URL used by the client.
  set baseUrl(String url) {
    _baseUrl = _normalizeBaseUrl(url);
  }

  static String _normalizeBaseUrl(String url) {
    final trimmed = url.trim();
    if (trimmed.endsWith('/')) {
      return trimmed.substring(0, trimmed.length - 1);
    }
    return trimmed;
  }

  /// Fetches the list of puzzle levels from `/api/v1/levels`.
  ///
  /// Optionally accepts [customBaseUrl] to override base URL for this call.
  Future<List<Level>> fetchLevels({String? customBaseUrl}) async {
    final effectiveBaseUrl = customBaseUrl != null
        ? _normalizeBaseUrl(customBaseUrl)
        : _baseUrl;

    final Uri uri;
    try {
      uri = Uri.parse('$effectiveBaseUrl/api/v1/levels');
    } catch (e) {
      throw LuxFormatException(
        message: 'Invalid base URL format: $effectiveBaseUrl',
        details: e,
      );
    }

    try {
      final response = await _client
          .get(uri, headers: {
            'Accept': 'application/json',
          })
          .timeout(timeout);

      if (response.statusCode != 200) {
        throw LuxHttpException(
          statusCode: response.statusCode,
          responseBody: response.body,
        );
      }

      final dynamic decoded;
      try {
        decoded = jsonDecode(response.body);
      } catch (e) {
        throw LuxFormatException(
          message: 'Malformed JSON returned from server at $effectiveBaseUrl.',
          details: e,
        );
      }

      if (decoded is! List) {
        throw LuxFormatException(
          message: 'Expected a JSON array of levels, but received ${decoded.runtimeType}.',
          details: decoded,
        );
      }

      final levels = <Level>[];
      for (final item in decoded) {
        if (item is Map<String, dynamic>) {
          levels.add(Level.fromJson(item));
        } else if (item is Map) {
          levels.add(Level.fromJson(Map<String, dynamic>.from(item)));
        }
      }

      return levels;
    } on LuxApiException {
      rethrow;
    } on SocketException catch (e) {
      throw LuxNetworkException(
        serverUrl: effectiveBaseUrl,
        details: e,
      );
    } on TimeoutException catch (e) {
      throw LuxNetworkException(
        serverUrl: effectiveBaseUrl,
        message: 'Connection timed out while connecting to Lux server at $effectiveBaseUrl.\n\n'
            'Please verify that the server is active and accessible.',
        details: e,
      );
    } on http.ClientException catch (e) {
      throw LuxNetworkException(
        serverUrl: effectiveBaseUrl,
        details: e,
      );
    } catch (e) {
      throw LuxNetworkException(
        serverUrl: effectiveBaseUrl,
        message: 'Unexpected network or connection error occurred while contacting $effectiveBaseUrl:\n$e',
        details: e,
      );
    }
  }

  /// Fetches a single puzzle level by its [id] from `/api/v1/level/<id>`.
  Future<Level> fetchLevel(String id, {String? customBaseUrl}) async {
    final effectiveBaseUrl = customBaseUrl != null
        ? _normalizeBaseUrl(customBaseUrl)
        : _baseUrl;

    final Uri uri;
    try {
      uri = Uri.parse('$effectiveBaseUrl/api/v1/level/$id');
    } catch (e) {
      throw LuxFormatException(
        message: 'Invalid URL for level $id: $effectiveBaseUrl',
        details: e,
      );
    }

    try {
      final response = await _client
          .get(uri, headers: {'Accept': 'application/json'})
          .timeout(timeout);

      if (response.statusCode != 200) {
        throw LuxHttpException(
          statusCode: response.statusCode,
          responseBody: response.body,
        );
      }

      final dynamic decoded = jsonDecode(response.body);
      if (decoded is Map<String, dynamic>) {
        return Level.fromJson(decoded);
      } else if (decoded is Map) {
        return Level.fromJson(Map<String, dynamic>.from(decoded));
      }
      throw const LuxFormatException(
        message: 'Expected a JSON object for level details.',
      );
    } on LuxApiException {
      rethrow;
    } catch (e) {
      throw LuxNetworkException(
        serverUrl: effectiveBaseUrl,
        details: e,
      );
    }
  }

  /// Submits a solution attempt to `/api/v1/submit`.
  /// Returns a boolean indicating if the attempt was correct.
  Future<Map<String, dynamic>> submitAttempt({
    required String levelId,
    String? attempt,
    Map<String, String>? files,
    String? authToken,
    String? customBaseUrl,
  }) async {
    final effectiveBaseUrl = customBaseUrl != null
        ? _normalizeBaseUrl(customBaseUrl)
        : _baseUrl;

    final uri = Uri.parse('$effectiveBaseUrl/api/v1/submit');
    final payload = <String, dynamic>{
      'level_id': levelId,
      if (attempt != null) 'attempt': attempt,
      if (files != null) 'files': files,
    };

    try {
      final response = await _client
          .post(
            uri,
            headers: {
              'Content-Type': 'application/json',
              'Accept': 'application/json',
              if (authToken != null) 'Authorization': 'Bearer $authToken',
            },
            body: jsonEncode(payload),
          )
          .timeout(timeout);

      if (response.statusCode != 200) {
        throw LuxHttpException(
          statusCode: response.statusCode,
          responseBody: response.body,
        );
      }

      final dynamic decoded = jsonDecode(response.body);
      if (decoded is Map<String, dynamic>) {
        return decoded;
      } else if (decoded is Map) {
        return Map<String, dynamic>.from(decoded);
      }
      return {'correct': false, 'raw': decoded};
    } on LuxApiException {
      rethrow;
    } catch (e) {
      throw LuxNetworkException(
        serverUrl: effectiveBaseUrl,
        details: e,
      );
    }
  }

  /// Checks the service status via `/health`.
  Future<bool> checkHealth({String? customBaseUrl}) async {
    final effectiveBaseUrl = customBaseUrl != null
        ? _normalizeBaseUrl(customBaseUrl)
        : _baseUrl;

    try {
      final uri = Uri.parse('$effectiveBaseUrl/health');
      final response = await _client
          .get(uri, headers: {'Accept': 'application/json'})
          .timeout(const Duration(seconds: 3));
      return response.statusCode == 200;
    } catch (_) {
      return false;
    }
  }

  /// Closes the underlying HTTP client.
  void dispose() {
    _client.close();
  }
}
