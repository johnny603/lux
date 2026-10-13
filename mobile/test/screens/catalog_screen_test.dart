import 'dart:convert';
import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:http/http.dart' as http;
import 'package:http/testing.dart';
import 'package:lux_mobile/main.dart';
import 'package:lux_mobile/services/lux_api_service.dart';
import 'package:lux_mobile/widgets/level_card.dart';
import 'package:lux_mobile/widgets/state_views.dart';

void main() {
  group('CatalogScreen Widget Tests', () {
    testWidgets('renders loading state initially while fetching', (tester) async {
      final client = MockClient((request) async {
        // Delay response to check loading indicator
        await Future.delayed(const Duration(milliseconds: 200));
        return http.Response(jsonEncode([]), 200);
      });

      final service = LuxApiService(client: client);

      await tester.pumpWidget(LuxApp(apiService: service));

      expect(find.byType(LoadingView), findsOneWidget);
      expect(find.text('Loading puzzle catalog...'), findsOneWidget);

      await tester.pumpAndSettle();
    });

    testWidgets('renders empty state when server returns empty catalog', (tester) async {
      final client = MockClient((request) async {
        return http.Response(jsonEncode([]), 200);
      });

      final service = LuxApiService(client: client);

      await tester.pumpWidget(LuxApp(apiService: service));
      await tester.pumpAndSettle();

      expect(find.byType(EmptyView), findsOneWidget);
      expect(find.text('Catalog is Empty'), findsOneWidget);
      expect(find.text('Refresh Catalog'), findsOneWidget);
    });

    testWidgets('renders error state with retry on network error', (tester) async {
      var callCount = 0;
      final client = MockClient((request) async {
        callCount++;
        if (callCount == 1) {
          return http.Response('Server Error', 500);
        }
        return http.Response(
          jsonEncode([
            {
              'id': '1',
              'title': 'Recovered Puzzle',
              'description': 'Description after retry',
              'category': 'General',
              'difficulty': 'easy',
              'tags': ['recovered'],
            }
          ]),
          200,
        );
      });

      final service = LuxApiService(client: client);

      await tester.pumpWidget(LuxApp(apiService: service));
      await tester.pumpAndSettle();

      expect(find.byType(ErrorView), findsOneWidget);
      expect(find.text('Connection Error'), findsOneWidget);
      expect(find.text('Retry Connection'), findsOneWidget);

      // Tap Retry
      await tester.tap(find.text('Retry Connection'));
      await tester.pumpAndSettle();

      expect(find.byType(LevelCard), findsOneWidget);
      expect(find.text('Recovered Puzzle'), findsOneWidget);
    });

    testWidgets('renders level list and allows searching', (tester) async {
      final levelsData = [
        {
          'id': '1',
          'title': 'Hello World in C',
          'description': 'Print hello world',
          'hint': 'Use printf',
          'category': 'Basics',
          'difficulty': 'easy',
          'tags': ['c', 'intro'],
        },
        {
          'id': '2',
          'title': 'DevOps Docker Setup',
          'description': 'Configure container sandbox',
          'hint': 'Use docker-compose',
          'category': 'DevOps',
          'difficulty': 'medium',
          'tags': ['docker', 'ci'],
        },
      ];

      final client = MockClient((request) async {
        return http.Response(jsonEncode(levelsData), 200);
      });

      final service = LuxApiService(client: client);

      await tester.pumpWidget(LuxApp(apiService: service));
      await tester.pumpAndSettle();

      expect(find.byType(LevelCard), findsNWidgets(2));
      expect(find.text('Hello World in C'), findsOneWidget);
      expect(find.text('DevOps Docker Setup'), findsOneWidget);

      // Test search filter
      await tester.enterText(find.byType(TextField), 'docker');
      await tester.pumpAndSettle();

      expect(find.text('DevOps Docker Setup'), findsOneWidget);
      expect(find.text('Hello World in C'), findsNothing);

      // Clear search
      await tester.tap(find.byIcon(Icons.clear));
      await tester.pumpAndSettle();

      expect(find.text('Hello World in C'), findsOneWidget);
    });

    testWidgets('opens server configuration dialog and updates URL', (tester) async {
      final client = MockClient((request) async {
        return http.Response(jsonEncode([]), 200);
      });

      final service = LuxApiService(
        baseUrl: 'http://127.0.0.1:5050',
        client: client,
      );

      await tester.pumpWidget(LuxApp(apiService: service));
      await tester.pumpAndSettle();

      // Tap server settings icon in AppBar
      await tester.tap(find.byIcon(Icons.dns_rounded));
      await tester.pumpAndSettle();

      expect(find.text('Server Configuration'), findsOneWidget);
      expect(find.text('Save & Reconnect'), findsOneWidget);

      // Select quick preset for Android Emulator
      await tester.tap(find.textContaining('Android Emulator'));
      await tester.pumpAndSettle();

      await tester.tap(find.text('Save & Reconnect'));
      await tester.pumpAndSettle();

      expect(service.baseUrl, 'http://10.0.2.2:5050');
    });
  });
}
