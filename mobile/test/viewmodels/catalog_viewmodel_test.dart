import 'package:flutter_test/flutter_test.dart';
import 'package:lux_mobile/models/level.dart';
import 'package:lux_mobile/services/lux_api_service.dart';
import 'package:lux_mobile/viewmodels/catalog_viewmodel.dart';

class MockLuxApiService extends LuxApiService {
  MockLuxApiService({super.baseUrl = 'http://test.local:5050'});

  List<Level> mockLevels = [];
  bool shouldThrow = false;
  String errorMessage = 'Failed to load';

  @override
  Future<List<Level>> fetchLevels({String? customBaseUrl}) async {
    if (shouldThrow) {
      throw LuxNetworkException(serverUrl: baseUrl, message: errorMessage);
    }
    return mockLevels;
  }
}

void main() {
  group('CatalogViewModel Unit Tests (MVVM)', () {
    late MockLuxApiService mockApi;
    late CatalogViewModel viewModel;

    final sampleLevels = [
      const Level(
        id: '1',
        title: 'Beginner Puzzle',
        description: 'Easy intro',
        category: 'Tutorial',
        difficulty: 'Easy',
        tags: ['starter', 'tutorial'],
      ),
      const Level(
        id: '2',
        title: 'Intermediate Logic',
        description: 'Challenging puzzle',
        category: 'Logic',
        difficulty: 'Medium',
        tags: ['medium', 'puzzle'],
      ),
      const Level(
        id: '3',
        title: 'Master Brain',
        description: 'Hard puzzle',
        category: 'Logic',
        difficulty: 'Hard',
        tags: ['expert'],
      ),
    ];

    setUp(() {
      mockApi = MockLuxApiService();
      viewModel = CatalogViewModel(apiService: mockApi);
    });

    test('initial state is correct', () {
      expect(viewModel.state, CatalogViewState.initial);
      expect(viewModel.levels, isEmpty);
      expect(viewModel.errorMessage, isNull);
      expect(viewModel.searchQuery, isEmpty);
      expect(viewModel.selectedCategory, 'All');
      expect(viewModel.isLoading, isFalse);
    });

    test('loadLevels transitions to loaded when API returns data', () async {
      mockApi.mockLevels = sampleLevels;

      final future = viewModel.loadLevels();
      expect(viewModel.isLoading, isTrue);

      await future;

      expect(viewModel.state, CatalogViewState.loaded);
      expect(viewModel.isLoaded, isTrue);
      expect(viewModel.levels.length, 3);
      expect(viewModel.errorMessage, isNull);
    });

    test('loadLevels transitions to empty when API returns empty list', () async {
      mockApi.mockLevels = [];

      await viewModel.loadLevels();

      expect(viewModel.state, CatalogViewState.empty);
      expect(viewModel.isEmpty, isTrue);
      expect(viewModel.levels, isEmpty);
      expect(viewModel.errorMessage, isNull);
    });

    test('loadLevels transitions to error when API throws LuxApiException', () async {
      mockApi.shouldThrow = true;
      mockApi.errorMessage = 'Connection refused by server.py';

      await viewModel.loadLevels();

      expect(viewModel.state, CatalogViewState.error);
      expect(viewModel.hasError, isTrue);
      expect(viewModel.errorMessage, contains('Connection refused'));
    });

    test('categories getter parses unique categories with All prefix', () async {
      mockApi.mockLevels = sampleLevels;
      await viewModel.loadLevels();

      expect(viewModel.categories, ['All', 'Tutorial', 'Logic']);
    });

    test('filteredLevels filters by search query matching title, id, and tags', () async {
      mockApi.mockLevels = sampleLevels;
      await viewModel.loadLevels();

      viewModel.setSearchQuery('Master');
      expect(viewModel.filteredLevels.length, 1);
      expect(viewModel.filteredLevels.first.id, '3');

      viewModel.setSearchQuery('expert');
      expect(viewModel.filteredLevels.length, 1);
      expect(viewModel.filteredLevels.first.id, '3');

      viewModel.setSearchQuery('2');
      expect(viewModel.filteredLevels.length, 1);
      expect(viewModel.filteredLevels.first.id, '2');

      viewModel.setSearchQuery('non-existent');
      expect(viewModel.filteredLevels, isEmpty);
    });

    test('filteredLevels filters by selected category', () async {
      mockApi.mockLevels = sampleLevels;
      await viewModel.loadLevels();

      viewModel.setSelectedCategory('Logic');
      expect(viewModel.filteredLevels.length, 2);
      expect(viewModel.filteredLevels.map((l) => l.id), containsAll(['2', '3']));

      viewModel.setSelectedCategory('All');
      expect(viewModel.filteredLevels.length, 3);
    });

    test('updateBaseUrl updates service and re-fetches levels', () async {
      mockApi.mockLevels = sampleLevels;
      await viewModel.updateBaseUrl('http://192.168.1.50:5050');

      expect(viewModel.baseUrl, 'http://192.168.1.50:5050');
      expect(viewModel.levels.length, 3);
    });
  });
}
