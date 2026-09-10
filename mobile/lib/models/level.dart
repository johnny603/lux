/// Model representing a puzzle level metadata in Lux.
class Level {
  final String id;
  final String title;
  final String description;
  final String? hint;
  final String validator;
  final String category;
  final String difficulty;
  final List<String> tags;

  const Level({
    required this.id,
    required this.title,
    required this.description,
    this.hint,
    this.validator = 'equals',
    required this.category,
    required this.difficulty,
    this.tags = const <String>[],
  });

  /// Factory constructor to parse a [Level] from a JSON map.
  factory Level.fromJson(Map<String, dynamic> json) {
    return Level(
      id: json['id']?.toString() ?? '',
      title: json['title']?.toString() ?? '',
      description: json['description']?.toString() ?? '',
      hint: json['hint']?.toString(),
      validator: json['validator']?.toString() ?? 'equals',
      category: json['category']?.toString() ?? 'General',
      difficulty: json['difficulty']?.toString() ?? 'medium',
      tags: (json['tags'] as List<dynamic>?)
              ?.map((tag) => tag.toString())
              .toList() ??
          const <String>[],
    );
  }

  /// Converts this [Level] instance to a JSON map.
  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'title': title,
      'description': description,
      'hint': hint,
      'validator': validator,
      'category': category,
      'difficulty': difficulty,
      'tags': tags,
    };
  }

  @override
  bool operator ==(Object other) =>
      identical(this, other) ||
      other is Level &&
          runtimeType == other.runtimeType &&
          id == other.id &&
          title == other.title &&
          description == other.description &&
          hint == other.hint &&
          validator == other.validator &&
          category == other.category &&
          difficulty == other.difficulty &&
          _listEquals(tags, other.tags);

  @override
  int get hashCode =>
      id.hashCode ^
      title.hashCode ^
      description.hashCode ^
      (hint?.hashCode ?? 0) ^
      validator.hashCode ^
      category.hashCode ^
      difficulty.hashCode ^
      tags.length.hashCode;

  static bool _listEquals(List<String> a, List<String> b) {
    if (identical(a, b)) return true;
    if (a.length != b.length) return false;
    for (var i = 0; i < a.length; i++) {
      if (a[i] != b[i]) return false;
    }
    return true;
  }
}
