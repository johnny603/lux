import 'package:flutter/material.dart';
import '../models/level.dart';
import '../services/lux_api_service.dart';
import '../widgets/level_card.dart';
import '../widgets/server_config_dialog.dart';
import '../widgets/state_views.dart';

/// Main screen displaying the Lux puzzle catalog.
class CatalogScreen extends StatefulWidget {
  final LuxApiService apiService;

  const CatalogScreen({
    super.key,
    required this.apiService,
  });

  @override
  State<CatalogScreen> createState() => _CatalogScreenState();
}

class _CatalogScreenState extends State<CatalogScreen> {
  List<Level> _levels = [];
  bool _isLoading = true;
  String? _errorMessage;
  String _searchQuery = '';
  String _selectedCategory = 'All';

  @override
  void initState() {
    super.initState();
    _loadLevels();
  }

  Future<void> _loadLevels() async {
    setState(() {
      _isLoading = true;
      _errorMessage = null;
    });

    try {
      final levels = await widget.apiService.fetchLevels();
      if (!mounted) return;
      setState(() {
        _levels = levels;
        _isLoading = false;
        _errorMessage = null;
      });
    } on LuxApiException catch (e) {
      if (!mounted) return;
      setState(() {
        _isLoading = false;
        _errorMessage = e.message;
      });
    } catch (e) {
      if (!mounted) return;
      setState(() {
        _isLoading = false;
        _errorMessage = 'An unexpected error occurred: $e';
      });
    }
  }

  void _openServerConfigDialog() {
    showDialog(
      context: context,
      builder: (ctx) => ServerConfigDialog(
        currentBaseUrl: widget.apiService.baseUrl,
        onSave: (newUrl) {
          widget.apiService.baseUrl = newUrl;
          _loadLevels();
        },
      ),
    );
  }

  List<String> _getCategories() {
    final categories = <String>{'All'};
    for (final level in _levels) {
      if (level.category.isNotEmpty) {
        categories.add(level.category);
      }
    }
    return categories.toList();
  }

  List<Level> _getFilteredLevels() {
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

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final colorScheme = theme.colorScheme;
    final filteredLevels = _getFilteredLevels();
    final categories = _getCategories();

    return Scaffold(
      appBar: AppBar(
        title: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const Text(
              'Lux Puzzle Catalog',
              style: TextStyle(fontWeight: FontWeight.bold, fontSize: 18),
            ),
            Text(
              widget.apiService.baseUrl,
              style: theme.textTheme.labelSmall?.copyWith(
                color: colorScheme.onSurfaceVariant,
              ),
              overflow: TextOverflow.ellipsis,
            ),
          ],
        ),
        actions: [
          IconButton(
            tooltip: 'Server Settings',
            icon: const Icon(Icons.dns_rounded),
            onPressed: _openServerConfigDialog,
          ),
          IconButton(
            tooltip: 'Refresh',
            icon: const Icon(Icons.refresh_rounded),
            onPressed: _isLoading ? null : _loadLevels,
          ),
        ],
      ),
      body: _buildBody(context, filteredLevels, categories),
    );
  }

  Widget _buildBody(
    BuildContext context,
    List<Level> filteredLevels,
    List<String> categories,
  ) {
    if (_isLoading) {
      return const LoadingView();
    }

    if (_errorMessage != null) {
      return ErrorView(
        message: _errorMessage!,
        onRetry: _loadLevels,
        onConfigureServer: _openServerConfigDialog,
      );
    }

    if (_levels.isEmpty) {
      return EmptyView(
        title: 'Catalog is Empty',
        message: 'The Lux server returned no puzzles.',
        onRefresh: _loadLevels,
      );
    }

    return Column(
      children: [
        // Search bar
        Padding(
          padding: const EdgeInsets.fromLTRB(16, 8, 16, 8),
          child: TextField(
            decoration: InputDecoration(
              hintText: 'Search puzzles, tags, id...',
              prefixIcon: const Icon(Icons.search),
              suffixIcon: _searchQuery.isNotEmpty
                  ? IconButton(
                      icon: const Icon(Icons.clear),
                      onPressed: () {
                        setState(() {
                          _searchQuery = '';
                        });
                      },
                    )
                  : null,
              contentPadding: const EdgeInsets.symmetric(vertical: 0),
              border: OutlineInputBorder(
                borderRadius: BorderRadius.circular(12),
              ),
            ),
            onChanged: (val) {
              setState(() {
                _searchQuery = val;
              });
            },
          ),
        ),

        // Category Filter Chips
        if (categories.length > 1)
          SizedBox(
            height: 40,
            child: ListView.separated(
              scrollDirection: Axis.horizontal,
              padding: const EdgeInsets.symmetric(horizontal: 16),
              itemCount: categories.length,
              separatorBuilder: (_, _) => const SizedBox(width: 8),
              itemBuilder: (context, index) {
                final category = categories[index];
                final isSelected = _selectedCategory == category;
                return FilterChip(
                  label: Text(category),
                  selected: isSelected,
                  onSelected: (selected) {
                    setState(() {
                      _selectedCategory = category;
                    });
                  },
                );
              },
            ),
          ),

        const SizedBox(height: 8),

        // Catalog List or empty filter result
        Expanded(
          child: filteredLevels.isEmpty
              ? Center(
                  child: Padding(
                    padding: const EdgeInsets.all(24.0),
                    child: Column(
                      mainAxisSize: MainAxisSize.min,
                      children: [
                        const Icon(
                          Icons.search_off_rounded,
                          size: 48,
                          color: Colors.grey,
                        ),
                        const SizedBox(height: 12),
                        Text(
                          'No matching puzzles',
                          style: Theme.of(context).textTheme.titleMedium,
                        ),
                        const SizedBox(height: 4),
                        const Text(
                          'Try adjusting your search or category filter.',
                          style: TextStyle(color: Colors.grey),
                        ),
                      ],
                    ),
                  ),
                )
              : RefreshIndicator(
                  onRefresh: _loadLevels,
                  child: ListView.builder(
                    padding: const EdgeInsets.only(bottom: 24, top: 4),
                    itemCount: filteredLevels.length,
                    itemBuilder: (context, index) {
                      final level = filteredLevels[index];
                      return LevelCard(level: level);
                    },
                  ),
                ),
        ),
      ],
    );
  }
}
