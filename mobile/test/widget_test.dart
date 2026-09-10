import 'dart:convert';
import 'package:flutter_test/flutter_test.dart';
import 'package:http/http.dart' as http;
import 'package:http/testing.dart';
import 'package:lux_mobile/main.dart';
import 'package:lux_mobile/services/lux_api_service.dart';

void main() {
  testWidgets('LuxApp smoke test', (WidgetTester tester) async {
    final client = MockClient((request) async {
      return http.Response(
        jsonEncode([
          {
            'id': '1',
            'title': 'Smoke Test Puzzle',
            'description': 'Smoke test description',
            'category': 'Smoke',
            'difficulty': 'easy',
            'tags': ['smoke'],
          }
        ]),
        200,
      );
    });

    final service = LuxApiService(client: client);

    await tester.pumpWidget(LuxApp(apiService: service));
    await tester.pumpAndSettle();

    expect(find.text('Lux Puzzle Catalog'), findsOneWidget);
    expect(find.text('Smoke Test Puzzle'), findsOneWidget);
  });
}
