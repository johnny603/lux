import 'package:flutter/material.dart';
import '../models/level.dart';

/// Card widget to display a single level summary.
class LevelCard extends StatelessWidget {
  final Level level;
  final VoidCallback? onTap;

  const LevelCard({
    super.key,
    required this.level,
    this.onTap,
  });

  Color _getDifficultyColor(BuildContext context, String difficulty) {
    switch (difficulty.toLowerCase()) {
      case 'easy':
        return Colors.green.shade600;
      case 'medium':
        return Colors.amber.shade800;
      case 'hard':
        return Colors.red.shade600;
      case 'expert':
        return Colors.purple.shade600;
      default:
        return Theme.of(context).colorScheme.primary;
    }
  }

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final colorScheme = theme.colorScheme;
    final diffColor = _getDifficultyColor(context, level.difficulty);

    return Card(
      elevation: 0,
      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.circular(14),
        side: BorderSide(
          color: colorScheme.outlineVariant.withValues(alpha: 0.6),
        ),
      ),
      margin: const EdgeInsets.symmetric(horizontal: 16, vertical: 6),
      clipBehavior: Clip.antiAlias,
      child: InkWell(
        onTap: onTap ?? () => _showLevelDetails(context),
        child: Padding(
          padding: const EdgeInsets.all(16.0),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Row(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Container(
                    padding: const EdgeInsets.symmetric(
                      horizontal: 8,
                      vertical: 4,
                    ),
                    decoration: BoxDecoration(
                      color: colorScheme.primaryContainer,
                      borderRadius: BorderRadius.circular(6),
                    ),
                    child: Text(
                      '#${level.id}',
                      style: theme.textTheme.labelMedium?.copyWith(
                        color: colorScheme.onPrimaryContainer,
                        fontWeight: FontWeight.bold,
                      ),
                    ),
                  ),
                  const SizedBox(width: 10),
                  Expanded(
                    child: Text(
                      level.title,
                      style: theme.textTheme.titleMedium?.copyWith(
                        fontWeight: FontWeight.bold,
                      ),
                    ),
                  ),
                  Container(
                    padding: const EdgeInsets.symmetric(
                      horizontal: 8,
                      vertical: 3,
                    ),
                    decoration: BoxDecoration(
                      color: diffColor.withValues(alpha: 0.15),
                      borderRadius: BorderRadius.circular(12),
                      border: Border.all(
                        color: diffColor.withValues(alpha: 0.5),
                      ),
                    ),
                    child: Text(
                      level.difficulty.toUpperCase(),
                      style: theme.textTheme.labelSmall?.copyWith(
                        color: diffColor,
                        fontWeight: FontWeight.bold,
                        letterSpacing: 0.5,
                      ),
                    ),
                  ),
                ],
              ),
              const SizedBox(height: 8),
              Text(
                level.description,
                style: theme.textTheme.bodyMedium?.copyWith(
                  color: colorScheme.onSurfaceVariant,
                ),
                maxLines: 2,
                overflow: TextOverflow.ellipsis,
              ),
              const SizedBox(height: 12),
              Row(
                children: [
                  Icon(
                    Icons.folder_outlined,
                    size: 16,
                    color: colorScheme.outline,
                  ),
                  const SizedBox(width: 4),
                  Text(
                    level.category,
                    style: theme.textTheme.labelMedium?.copyWith(
                      color: colorScheme.outline,
                      fontWeight: FontWeight.w600,
                    ),
                  ),
                  const Spacer(),
                  if (level.tags.isNotEmpty)
                    Wrap(
                      spacing: 4,
                      children: level.tags.take(3).map((tag) {
                        return Container(
                          padding: const EdgeInsets.symmetric(
                            horizontal: 6,
                            vertical: 2,
                          ),
                          decoration: BoxDecoration(
                            color: colorScheme.surfaceContainerHighest,
                            borderRadius: BorderRadius.circular(4),
                          ),
                          child: Text(
                            tag,
                            style: theme.textTheme.labelSmall?.copyWith(
                              color: colorScheme.onSurfaceVariant,
                            ),
                          ),
                        );
                      }).toList(),
                    ),
                ],
              ),
            ],
          ),
        ),
      ),
    );
  }

  void _showLevelDetails(BuildContext context) {
    showModalBottomSheet(
      context: context,
      isScrollControlled: true,
      shape: const RoundedRectangleBorder(
        borderRadius: BorderRadius.vertical(top: Radius.circular(20)),
      ),
      builder: (ctx) {
        final theme = Theme.of(ctx);
        final colorScheme = theme.colorScheme;
        final diffColor = _getDifficultyColor(ctx, level.difficulty);

        return DraggableScrollableSheet(
          initialChildSize: 0.6,
          minChildSize: 0.4,
          maxChildSize: 0.9,
          expand: false,
          builder: (_, scrollController) {
            return SingleChildScrollView(
              controller: scrollController,
              padding: const EdgeInsets.all(24),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Center(
                    child: Container(
                      width: 40,
                      height: 4,
                      decoration: BoxDecoration(
                        color: colorScheme.outlineVariant,
                        borderRadius: BorderRadius.circular(2),
                      ),
                    ),
                  ),
                  const SizedBox(height: 16),
                  Row(
                    children: [
                      Container(
                        padding: const EdgeInsets.symmetric(
                          horizontal: 10,
                          vertical: 4,
                        ),
                        decoration: BoxDecoration(
                          color: colorScheme.primaryContainer,
                          borderRadius: BorderRadius.circular(8),
                        ),
                        child: Text(
                          'Puzzle #${level.id}',
                          style: theme.textTheme.labelLarge?.copyWith(
                            color: colorScheme.onPrimaryContainer,
                            fontWeight: FontWeight.bold,
                          ),
                        ),
                      ),
                      const SizedBox(width: 10),
                      Container(
                        padding: const EdgeInsets.symmetric(
                          horizontal: 10,
                          vertical: 4,
                        ),
                        decoration: BoxDecoration(
                          color: diffColor.withValues(alpha: 0.15),
                          borderRadius: BorderRadius.circular(8),
                        ),
                        child: Text(
                          level.difficulty.toUpperCase(),
                          style: theme.textTheme.labelMedium?.copyWith(
                            color: diffColor,
                            fontWeight: FontWeight.bold,
                          ),
                        ),
                      ),
                    ],
                  ),
                  const SizedBox(height: 12),
                  Text(
                    level.title,
                    style: theme.textTheme.headlineSmall?.copyWith(
                      fontWeight: FontWeight.bold,
                    ),
                  ),
                  const SizedBox(height: 16),
                  Text(
                    'Description',
                    style: theme.textTheme.titleSmall?.copyWith(
                      fontWeight: FontWeight.bold,
                      color: colorScheme.primary,
                    ),
                  ),
                  const SizedBox(height: 6),
                  Text(
                    level.description,
                    style: theme.textTheme.bodyLarge?.copyWith(height: 1.5),
                  ),
                  if (level.hint != null && level.hint!.isNotEmpty) ...[
                    const SizedBox(height: 16),
                    Text(
                      'Hint',
                      style: theme.textTheme.titleSmall?.copyWith(
                        fontWeight: FontWeight.bold,
                        color: colorScheme.primary,
                      ),
                    ),
                    const SizedBox(height: 6),
                    Container(
                      padding: const EdgeInsets.all(12),
                      decoration: BoxDecoration(
                        color: colorScheme.tertiaryContainer.withValues(alpha: 0.4),
                        borderRadius: BorderRadius.circular(8),
                      ),
                      child: Row(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Icon(
                            Icons.lightbulb_outline,
                            size: 20,
                            color: colorScheme.tertiary,
                          ),
                          const SizedBox(width: 8),
                          Expanded(
                            child: Text(
                              level.hint!,
                              style: theme.textTheme.bodyMedium,
                            ),
                          ),
                        ],
                      ),
                    ),
                  ],
                  const SizedBox(height: 16),
                  Row(
                    children: [
                      Expanded(
                        child: Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            Text(
                              'Category',
                              style: theme.textTheme.labelMedium?.copyWith(
                                color: colorScheme.outline,
                              ),
                            ),
                            const SizedBox(height: 4),
                            Text(
                              level.category,
                              style: theme.textTheme.bodyMedium?.copyWith(
                                fontWeight: FontWeight.w600,
                              ),
                            ),
                          ],
                        ),
                      ),
                      Expanded(
                        child: Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            Text(
                              'Validator',
                              style: theme.textTheme.labelMedium?.copyWith(
                                color: colorScheme.outline,
                              ),
                            ),
                            const SizedBox(height: 4),
                            Text(
                              level.validator,
                              style: theme.textTheme.bodyMedium?.copyWith(
                                fontWeight: FontWeight.w600,
                              ),
                            ),
                          ],
                        ),
                      ),
                    ],
                  ),
                  if (level.tags.isNotEmpty) ...[
                    const SizedBox(height: 16),
                    Text(
                      'Tags',
                      style: theme.textTheme.labelMedium?.copyWith(
                        color: colorScheme.outline,
                      ),
                    ),
                    const SizedBox(height: 6),
                    Wrap(
                      spacing: 6,
                      runSpacing: 6,
                      children: level.tags.map((tag) {
                        return Chip(
                          label: Text(tag),
                          padding: EdgeInsets.zero,
                          visualDensity: VisualDensity.compact,
                        );
                      }).toList(),
                    ),
                  ],
                  const SizedBox(height: 24),
                ],
              ),
            );
          },
        );
      },
    );
  }
}
