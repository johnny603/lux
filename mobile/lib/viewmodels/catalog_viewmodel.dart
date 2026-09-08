import 'package:flutter/foundation.dart';
import '../models/level.dart';
import '../services/lux_api_service.dart';

/// States representing the current lifecycle of catalog data loading.
enum CatalogViewState {
  initial,
  loading,
  loaded,
  empty,
  error,
}

/// ViewModel for the puzzle level catalog screen, implementing the MVVM pattern.
///
/// Encapsulates state management, search/category filtering, and communication
/// with [LuxApiService].
class CatalogViewModel extends ChangeNotifier {
  final LuxApiService apiService;

  CatalogViewState _state = CatalogViewState.initial;
  List<Level> _levels = [];
  String? _errorMessage;
  String _searchQuery = '';
  String _selectedCategory = 'All';

  CatalogViewModel({required this.apiService});

  // --- Getters ---

  CatalogViewState get state => _state;
  bool get isLoading => _state == CatalogViewState.loading;
  bool get hasError => _state == CatalogViewState.error;
  bool get isEmpty => _state == CatalogViewState.empty;
  bool get isLoaded => _state == CatalogViewState.loaded;

  String? get errorMessage => _errorMessage;
  String get searchQuery => _searchQuery;
  String get selectedCategory => _selectedCategory;
  List<Level> get levels => List.unmodifiable(_levels);
  String get baseUrl => apiService.baseUrl;

  /// Returns distinct categories present in [_levels] prefixed with 'All'.
  List<String> get categories {
    final categorySet = <String>{'All'};
    for (final level in _levels) {
      if (level.category.isNotEmpty) {
        categorySet.add(level.category);
      }
    }
    return categorySet.toList();
  }

  /// Returns levels filtered by [_selectedCategory] and [_searchQuery].
  List<Level> get filteredLevels {
    return _levels.where((level) {
      final matchesCategory =
          _selectedCategory == 'All' || level.category == _selectedCategory;

      final query = _searchQuery.trim().toLowerCase();
      final matchesQuery = query.isEmpty ||
          level.title.toLowerCase().contains(query) ||
          level.description.toLowerCase().contains(query) ||
          level.id.toLowerCase().contains(query) ||
          level.tags.any((t) => t.toLowerCase().contains(query));

      return matchesCategory && matchesQuery;
    }).toList();
  }

  // --- Actions ---

  /// Fetches levels from the Lux backend API and updates the state.
  Future<void> loadLevels() async {
    _state = CatalogViewState.loading;
    _errorMessage = null;
    notifyListeners();

    try {
      final fetchedLevels = await apiService.fetchLevels();
      _levels = fetchedLevels;
      _state = _levels.isEmpty ? CatalogViewState.empty : CatalogViewState.loaded;
      _errorMessage = null;
    } on LuxApiException catch (e) {
      _state = CatalogViewState.error;
      _errorMessage = e.message;
    } catch (e) {
      _state = CatalogViewState.error;
      _errorMessage = 'An unexpected error occurred: $e';
    }

    notifyListeners();
  }

  /// Alias to reload levels for pull-to-refresh.
  Future<void> refresh() => loadLevels();

  /// Updates the current search query filter.
  void setSearchQuery(String query) {
    if (_searchQuery == query) return;
    _searchQuery = query;
    notifyListeners();
  }

  /// Updates the category filter.
  void setSelectedCategory(String category) {
    if (_selectedCategory == category) return;
    _selectedCategory = category;
    notifyListeners();
  }

  /// Updates base URL in [LuxApiService] and triggers reload.
  Future<void> updateBaseUrl(String newUrl) async {
    apiService.baseUrl = newUrl;
    notifyListeners();
    await loadLevels();
  }
}
