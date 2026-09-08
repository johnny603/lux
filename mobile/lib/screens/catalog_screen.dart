import 'package:flutter/material.dart';
import '../models/level.dart';
import '../services/lux_api_service.dart';
import '../viewmodels/catalog_viewmodel.dart';
import '../widgets/level_card.dart';
import '../widgets/server_config_dialog.dart';
import '../widgets/state_views.dart';

/// Main screen displaying the Lux puzzle catalog, representing the View layer in MVVM.
///
/// Binds reactively to [CatalogViewModel] for state management and presentation logic.
class CatalogScreen extends StatefulWidget {
  final LuxApiService? apiService;
  final CatalogViewModel? viewModel;

  const CatalogScreen({
    super.key,
    this.apiService,
    this.viewModel,
  }) : assert(apiService != null || viewModel != null,
            'Either apiService or viewModel must be provided');

  @override
  State<CatalogScreen> createState() => _CatalogScreenState();
}

class _CatalogScreenState extends State<CatalogScreen> {
  late final CatalogViewModel _viewModel;
  late final bool _ownsViewModel;
  final TextEditingController _searchController = TextEditingController();

  @override
  void initState() {
    super.initState();
    if (widget.viewModel != null) {
      _viewModel = widget.viewModel!;
      _ownsViewModel = false;
    } else {
      _viewModel = CatalogViewModel(apiService: widget.apiService!);
      _ownsViewModel = true;
    }

    _searchController.text = _viewModel.searchQuery;

    // Trigger initial fetch if view model is still in initial state.
    if (_viewModel.state == CatalogViewState.initial) {
      _viewModel.loadLevels();
    }
  }

  @override
  void dispose() {
    _searchController.dispose();
    if (_ownsViewModel) {
      _viewModel.dispose();
    }
    super.dispose();
  }

  void _openServerConfigDialog() {
    showDialog(
      context: context,
      builder: (ctx) => ServerConfigDialog(
        currentBaseUrl: _viewModel.baseUrl,
        onSave: (newUrl) {
          _viewModel.updateBaseUrl(newUrl);
        },
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final colorScheme = theme.colorScheme;

    return ListenableBuilder(
      listenable: _viewModel,
      builder: (context, _) {
        final filteredLevels = _viewModel.filteredLevels;
        final categories = _viewModel.categories;

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
                  _viewModel.baseUrl,
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
                onPressed: _viewModel.isLoading ? null : _viewModel.refresh,
              ),
            ],
          ),
          body: _buildBody(context, filteredLevels, categories),
        );
      },
    );
  }

  Widget _buildBody(
    BuildContext context,
    List<Level> filteredLevels,
    List<String> categories,
  ) {
    if (_viewModel.isLoading) {
      return const LoadingView();
    }

    if (_viewModel.hasError) {
      return ErrorView(
        message: _viewModel.errorMessage ?? 'An error occurred',
        onRetry: _viewModel.loadLevels,
        onConfigureServer: _openServerConfigDialog,
      );
    }

    if (_viewModel.isEmpty) {
      return EmptyView(
        title: 'Catalog is Empty',
        message: 'The Lux server returned no puzzles.',
        onRefresh: _viewModel.loadLevels,
      );
    }

    return Column(
      children: [
        // Search bar
        Padding(
          padding: const EdgeInsets.fromLTRB(16, 8, 16, 8),
          child: TextField(
            controller: _searchController,
            decoration: InputDecoration(
              hintText: 'Search puzzles, tags, id...',
              prefixIcon: const Icon(Icons.search),
              suffixIcon: _viewModel.searchQuery.isNotEmpty
                  ? IconButton(
                      icon: const Icon(Icons.clear),
                      onPressed: () {
                        _searchController.clear();
                        _viewModel.setSearchQuery('');
                      },
                    )
                  : null,
              contentPadding: const EdgeInsets.symmetric(vertical: 0),
              border: OutlineInputBorder(
                borderRadius: BorderRadius.circular(12),
              ),
            ),
            onChanged: (val) {
              _viewModel.setSearchQuery(val);
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
                final isSelected = _viewModel.selectedCategory == category;
                return FilterChip(
                  label: Text(category),
                  selected: isSelected,
                  onSelected: (selected) {
                    _viewModel.setSelectedCategory(category);
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
                  onRefresh: _viewModel.refresh,
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
