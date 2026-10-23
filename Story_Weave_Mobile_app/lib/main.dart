import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'services/api_service.dart';
import 'services/storage_service.dart';
import 'theme/app_theme.dart';
import 'screens/home_screen.dart';

void main() async {
  WidgetsFlutterBinding.ensureInitialized();

  // Initialize API service settings
  await ApiService().init();

  // Load saved theme preference
  final isDark = await StorageService.isDarkMode();

  runApp(StoryWeaveApp(initialIsDarkMode: isDark));
}

class StoryWeaveApp extends StatefulWidget {
  final bool initialIsDarkMode;
  const StoryWeaveApp({super.key, this.initialIsDarkMode = true});

  @override
  State<StoryWeaveApp> createState() => _StoryWeaveAppState();
}

class _StoryWeaveAppState extends State<StoryWeaveApp> {
  late bool _isDarkMode;

  @override
  void initState() {
    super.initState();
    _isDarkMode = widget.initialIsDarkMode;
    _updateSystemUI();
  }

  void _updateSystemUI() {
    SystemChrome.setSystemUIOverlayStyle(
      SystemUiOverlayStyle(
        statusBarColor: Colors.transparent,
        statusBarIconBrightness:
            _isDarkMode ? Brightness.light : Brightness.dark,
        systemNavigationBarColor:
            _isDarkMode ? const Color(0xFF080B12) : const Color(0xFFF8FAFC),
        systemNavigationBarIconBrightness:
            _isDarkMode ? Brightness.light : Brightness.dark,
      ),
    );
  }

  void _toggleTheme() {
    setState(() {
      _isDarkMode = !_isDarkMode;
    });
    _updateSystemUI();
    StorageService.setDarkMode(_isDarkMode);
  }

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'Story Weave',
      debugShowCheckedModeBanner: false,
      theme: AppTheme.lightTheme,
      darkTheme: AppTheme.darkTheme,
      themeMode: _isDarkMode ? ThemeMode.dark : ThemeMode.light,
      home: HomeScreen(
        isDarkMode: _isDarkMode,
        onToggleTheme: _toggleTheme,
      ),
    );
  }
}
