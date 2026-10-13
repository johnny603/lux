import 'package:flutter_test/flutter_test.dart';
import 'package:lux_mobile/models/level.dart';

void main() {
  group('Level Model', () {
    test('parses complete JSON correctly', () {
      final json = {
        'id': '1',
        'title': 'Hello World in C',
        'description': 'Write a program that outputs Hello, World!',
        'hint': 'Use printf',
        'validator': 'equals',
        'category': 'Basics',
        'difficulty': 'easy',
        'tags': ['c', 'intro', 'stdio'],
      };

      final level = Level.fromJson(json);

      expect(level.id, '1');
      expect(level.title, 'Hello World in C');
      expect(level.description, 'Write a program that outputs Hello, World!');
      expect(level.hint, 'Use printf');
      expect(level.validator, 'equals');
      expect(level.category, 'Basics');
      expect(level.difficulty, 'easy');
      expect(level.tags, ['c', 'intro', 'stdio']);
    });

    test('handles missing or null optional fields with sensible defaults', () {
      final json = {
        'id': 42,
        'title': 'Minimal Puzzle',
        'description': 'Description here',
      };

      final level = Level.fromJson(json);

      expect(level.id, '42');
      expect(level.title, 'Minimal Puzzle');
      expect(level.description, 'Description here');
      expect(level.hint, isNull);
      expect(level.validator, 'equals');
      expect(level.category, 'General');
      expect(level.difficulty, 'medium');
      expect(level.tags, isEmpty);
    });

    test('converts to JSON map correctly', () {
      const level = Level(
        id: '2',
        title: 'Network Packet Sniffer',
        description: 'Analyze raw pcap packets',
        hint: 'Use libpcap',
        validator: 'regex',
        category: 'Security',
        difficulty: 'hard',
        tags: ['networking', 'security'],
      );

      final json = level.toJson();

      expect(json['id'], '2');
      expect(json['title'], 'Network Packet Sniffer');
      expect(json['description'], 'Analyze raw pcap packets');
      expect(json['hint'], 'Use libpcap');
      expect(json['validator'], 'regex');
      expect(json['category'], 'Security');
      expect(json['difficulty'], 'hard');
      expect(json['tags'], ['networking', 'security']);
    });

    test('supports equality comparison and hash codes', () {
      const level1 = Level(
        id: '1',
        title: 'Title',
        description: 'Desc',
        category: 'DevOps',
        difficulty: 'easy',
        tags: ['tag1'],
      );

      const level2 = Level(
        id: '1',
        title: 'Title',
        description: 'Desc',
        category: 'DevOps',
        difficulty: 'easy',
        tags: ['tag1'],
      );

      const level3 = Level(
        id: '2',
        title: 'Title 2',
        description: 'Desc 2',
        category: 'DevOps',
        difficulty: 'hard',
        tags: ['tag2'],
      );

      expect(level1, equals(level2));
      expect(level1.hashCode, equals(level2.hashCode));
      expect(level1, isNot(equals(level3)));
    });
  });
}
