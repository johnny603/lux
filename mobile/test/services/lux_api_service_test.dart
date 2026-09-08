import 'dart:convert';
import 'dart:io';
import 'package:flutter_test/flutter_test.dart';
import 'package:http/http.dart' as http;
import 'package:http/testing.dart';
import 'package:lux_mobile/services/lux_api_service.dart';

void main() {
  group('LuxApiService', () {
    test('fetches and parses list of levels successfully on HTTP 200', () async {
      final mockData = [
        {
          'id': '1',
          'title': 'C Basics',
          'description': 'Introductory level',
          'hint': 'Check main signature',
          'validator': 'equals',
          'category': 'Basics',
          'difficulty': 'easy',
          'tags': ['c', 'beginner'],
        },
        {
          'id': '2',
          'title': 'Pointers & Memory',
          'description': 'Advanced pointer manipulation',
          'hint': null,
          'validator': 'diff',
          'category': 'Memory',
          'difficulty': 'medium',
          'tags': ['c', 'memory'],
        },
      ];

      final client = MockClient((request) async {
        if (request.url.path == '/api/v1/levels') {
          return http.Response(jsonEncode(mockData), 200, headers: {
            'content-type': 'application/json',
          });
        }
        return http.Response('Not Found', 404);
      });

      final service = LuxApiService(
        baseUrl: 'http://127.0.0.1:5050',
        client: client,
      );

      final levels = await service.fetchLevels();

      expect(levels.length, 2);
      expect(levels[0].id, '1');
      expect(levels[0].title, 'C Basics');
      expect(levels[1].id, '2');
      expect(levels[1].difficulty, 'medium');
    });

    test('returns empty list when server returns empty array', () async {
      final client = MockClient((request) async {
        return http.Response(jsonEncode([]), 200);
      });

      final service = LuxApiService(client: client);
      final levels = await service.fetchLevels();

      expect(levels, isEmpty);
    });

    test('throws LuxHttpException on non-200 response code', () async {
      final client = MockClient((request) async {
        return http.Response('Internal Server Error', 500);
      });

      final service = LuxApiService(client: client);

      expect(
        () => service.fetchLevels(),
        throwsA(isA<LuxHttpException>().having(
          (e) => e.statusCode,
          'statusCode',
          500,
        )),
      );
    });

    test('throws LuxFormatException on invalid JSON payload', () async {
      final client = MockClient((request) async {
        return http.Response('<html><body>Error</body></html>', 200);
      });

      final service = LuxApiService(client: client);

      expect(
        () => service.fetchLevels(),
        throwsA(isA<LuxFormatException>()),
      );
    });

    test('throws LuxFormatException when response is not a JSON list', () async {
      final client = MockClient((request) async {
        return http.Response(jsonEncode({'message': 'not a list'}), 200);
      });

      final service = LuxApiService(client: client);

      expect(
        () => service.fetchLevels(),
        throwsA(isA<LuxFormatException>()),
      );
    });

    test('throws LuxNetworkException with actionable guidance on connection failure', () async {
      final client = MockClient((request) async {
        throw const SocketException('Connection refused');
      });

      final service = LuxApiService(
        baseUrl: 'http://127.0.0.1:5050',
        client: client,
      );

      try {
        await service.fetchLevels();
        fail('Expected LuxNetworkException');
      } on LuxNetworkException catch (e) {
        expect(e.serverUrl, 'http://127.0.0.1:5050');
        expect(e.message, contains('Unable to connect to the Lux server'));
        expect(e.message, contains('python server.py'));
      }
    });

    test('supports configuring base URL dynamically and normalizes trailing slashes', () async {
      String? requestedUrl;
      final client = MockClient((request) async {
        requestedUrl = request.url.toString();
        return http.Response('[]', 200);
      });

      final service = LuxApiService(
        baseUrl: 'http://custom-host:8080/',
        client: client,
      );

      expect(service.baseUrl, 'http://custom-host:8080');

      await service.fetchLevels();
      expect(requestedUrl, 'http://custom-host:8080/api/v1/levels');

      service.baseUrl = 'http://10.0.2.2:5050/';
      expect(service.baseUrl, 'http://10.0.2.2:5050');

      await service.fetchLevels();
      expect(requestedUrl, 'http://10.0.2.2:5050/api/v1/levels');
    });
  });
}
