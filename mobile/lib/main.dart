import 'package:flutter/material.dart';
import 'screens/catalog_screen.dart';
import 'services/lux_api_service.dart';

void main() {
  runApp(const LuxApp());
}

/// Root widget for the Lux Mobile Catalog application.
class LuxApp extends StatefulWidget {
  final LuxApiService? apiService;

  const LuxApp({
    super.key,
    this.apiService,
  });

  @override
  State<LuxApp> createState() => _LuxAppState();
}

class _LuxAppState extends State<LuxApp> {
  late final LuxApiService _apiService;

  @override
  void initState() {
    super.initState();
    _apiService = widget.apiService ?? LuxApiService();
  }

  @override
  void dispose() {
    if (widget.apiService == null) {
      _apiService.dispose();
    }
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'Lux Mobile Catalog',
      debugShowCheckedModeBanner: false,
      theme: ThemeData(
        colorScheme: ColorScheme.fromSeed(
          seedColor: const Color(0xFF3F51B5),
          brightness: Brightness.light,
        ),
        useMaterial3: true,
      ),
      darkTheme: ThemeData(
        colorScheme: ColorScheme.fromSeed(
          seedColor: const Color(0xFF7986CB),
          brightness: Brightness.dark,
        ),
        useMaterial3: true,
      ),
      themeMode: ThemeMode.system,
      home: CatalogScreen(apiService: _apiService),
    );
  }
}
