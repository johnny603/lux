import 'package:flutter/material.dart';

/// Dialog allowing the user to view and configure the Lux Server Base URL.
class ServerConfigDialog extends StatefulWidget {
  final String currentBaseUrl;
  final ValueChanged<String> onSave;

  const ServerConfigDialog({
    super.key,
    required this.currentBaseUrl,
    required this.onSave,
  });

  @override
  State<ServerConfigDialog> createState() => _ServerConfigDialogState();
}

class _ServerConfigDialogState extends State<ServerConfigDialog> {
  late final TextEditingController _controller;
  String? _errorText;

  static const List<Map<String, String>> presets = [
    {
      'label': 'Local (Desktop / Web)',
      'url': 'http://127.0.0.1:5050',
    },
    {
      'label': 'Android Emulator',
      'url': 'http://10.0.2.2:5050',
    },
    {
      'label': 'Localhost',
      'url': 'http://localhost:5050',
    },
  ];

  @override
  void initState() {
    super.initState();
    _controller = TextEditingController(text: widget.currentBaseUrl);
  }

  @override
  void dispose() {
    _controller.dispose();
    super.dispose();
  }

  void _validateAndSave() {
    final text = _controller.text.trim();
    if (text.isEmpty) {
      setState(() {
        _errorText = 'Base URL cannot be empty';
      });
      return;
    }

    final uri = Uri.tryParse(text);
    if (uri == null || !uri.hasScheme || (!uri.isScheme('http') && !uri.isScheme('https'))) {
      setState(() {
        _errorText = 'Enter a valid URL (e.g. http://127.0.0.1:5050)';
      });
      return;
    }

    widget.onSave(text);
    Navigator.of(context).pop();
  }

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);

    return AlertDialog(
      title: const Row(
        children: [
          Icon(Icons.dns_rounded),
          SizedBox(width: 10),
          Text('Server Configuration'),
        ],
      ),
      content: SingleChildScrollView(
        child: Column(
          mainAxisSize: MainAxisSize.min,
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              'Specify the base URL where the Lux server is running:',
              style: theme.textTheme.bodyMedium,
            ),
            const SizedBox(height: 16),
            TextField(
              controller: _controller,
              decoration: InputDecoration(
                labelText: 'Base URL',
                hintText: 'http://127.0.0.1:5050',
                border: const OutlineInputBorder(),
                errorText: _errorText,
                prefixIcon: const Icon(Icons.link),
              ),
              keyboardType: TextInputType.url,
              onChanged: (_) {
                if (_errorText != null) {
                  setState(() {
                    _errorText = null;
                  });
                }
              },
            ),
            const SizedBox(height: 16),
            Text(
              'Quick Presets:',
              style: theme.textTheme.labelMedium?.copyWith(
                fontWeight: FontWeight.bold,
              ),
            ),
            const SizedBox(height: 8),
            Wrap(
              spacing: 8,
              runSpacing: 8,
              children: presets.map((p) {
                final isSelected = _controller.text == p['url'];
                return ActionChip(
                  avatar: isSelected ? const Icon(Icons.check, size: 16) : null,
                  label: Text('${p['label']} (${p['url']})'),
                  onPressed: () {
                    setState(() {
                      _controller.text = p['url']!;
                      _errorText = null;
                    });
                  },
                );
              }).toList(),
            ),
          ],
        ),
      ),
      actions: [
        TextButton(
          onPressed: () => Navigator.of(context).pop(),
          child: const Text('Cancel'),
        ),
        FilledButton(
          onPressed: _validateAndSave,
          child: const Text('Save & Reconnect'),
        ),
      ],
    );
  }
}
