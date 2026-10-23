import 'dart:convert';
import 'package:http/http.dart' as http;
import '../models/story_model.dart';
import 'storage_service.dart';

enum ServerStatus { online, wakingUp, offline, checking }

class ApiService {
  static final ApiService _instance = ApiService._internal();
  factory ApiService() => _instance;
  ApiService._internal();

  String _baseUrl = 'http://10.0.2.2:8000';
  ServerStatus currentStatus = ServerStatus.checking;
  final Map<String, String> _sessionCookies = {};
  String? _csrfToken;

  String get baseUrl => _baseUrl;

  Future<void> init() async {
    _baseUrl = await StorageService.getBaseUrl();
  }

  void updateBaseUrl(String newUrl) {
    _baseUrl = newUrl.trim();
    if (_baseUrl.endsWith('/')) {
      _baseUrl = _baseUrl.substring(0, _baseUrl.length - 1);
    }
  }

  // Header helper with cookies & CSRF support
  Map<String, String> _buildHeaders() {
    final headers = <String, String>{
      'Content-Type': 'application/json',
      'Accept': 'application/json',
    };
    if (_sessionCookies.isNotEmpty) {
      headers['Cookie'] = _sessionCookies.entries
          .map((e) => '${e.key}=${e.value}')
          .join('; ');
    }
    if (_csrfToken != null) {
      headers['X-CSRFToken'] = _csrfToken!;
    }
    return headers;
  }

  // Parse cookies from response
  void _extractCookies(http.Response response) {
    final rawCookie = response.headers['set-cookie'];
    if (rawCookie != null) {
      final cookies = rawCookie.split(',');
      for (final c in cookies) {
        final parts = c.split(';')[0].split('=');
        if (parts.length >= 2) {
          final name = parts[0].trim();
          final val = parts.sublist(1).join('=').trim();
          _sessionCookies[name] = val;
          if (name.toLowerCase().contains('csrf')) {
            _csrfToken = val;
          }
        }
      }
    }
  }

  // Health check with cold-start / wake-up detection
  Future<ServerStatus> checkHealth({
    Function(String msg)? onWakeProgress,
  }) async {
    currentStatus = ServerStatus.checking;
    try {
      final uri = Uri.parse('$_baseUrl/health');
      final res = await http.get(uri).timeout(const Duration(seconds: 4));
      _extractCookies(res);
      if (res.statusCode == 200) {
        currentStatus = ServerStatus.online;
        return ServerStatus.online;
      }
    } catch (e) {
      // Possible cold start on Render or free hosting
      if (_baseUrl.contains('onrender.com') || _baseUrl.contains('render') || _baseUrl.contains('pythonanywhere')) {
        currentStatus = ServerStatus.wakingUp;
        onWakeProgress?.call('Waking up cloud server instance...');
        // Retry ping
        for (int i = 0; i < 3; i++) {
          await Future.delayed(const Duration(seconds: 2));
          try {
            final res = await http.get(Uri.parse('$_baseUrl/health')).timeout(const Duration(seconds: 5));
            if (res.statusCode == 200) {
              currentStatus = ServerStatus.online;
              return ServerStatus.online;
            }
          } catch (_) {}
        }
      }
    }
    currentStatus = ServerStatus.offline;
    return ServerStatus.offline;
  }

  // Primary Generation Pipeline
  Future<StoryModel> generateStory({
    required String title,
    required String genre,
    required String description,
    String? geminiApiKey,
    Function(String status)? onProgress,
  }) async {
    final customKey = geminiApiKey ?? await StorageService.getApiKey();

    onProgress?.call('Connecting to Story Weave server...');
    final uri = Uri.parse('$_baseUrl/api/generate');

    try {
      final body = json.encode({
        'title': title,
        'genre': genre,
        'description': description,
        'gemini_api_key': customKey,
      });

      onProgress?.call('Weaving story with AI engine...');
      final response = await http
          .post(uri, headers: _buildHeaders(), body: body)
          .timeout(const Duration(seconds: 35));

      _extractCookies(response);

      if (response.statusCode == 200) {
        final data = json.decode(utf8.decode(response.bodyBytes));
        return StoryModel(
          id: DateTime.now().millisecondsSinceEpoch.toString(),
          title: data['title'] ?? title,
          genre: data['genre'] ?? genre,
          concept: description,
          storyText: data['story'] ?? '',
          visualPrompt: data['visual_prompt'],
          imageUrl: data['image_url'],
          audioUrl: data['audio_url'] != null
              ? (_baseUrl + data['audio_url'])
              : null,
        );
      }
    } catch (e) {
      // Fallback: If server is unavailable, generate rich client-side content
      onProgress?.call('Generating using local resilient fallback...');
    }

    // High quality client-side fallback
    return _generateClientFallback(title, genre, description);
  }

  StoryModel _generateClientFallback(
      String title, String genre, String description) {
    final storyText = """Title:
$title

Genre:
$genre

Concept:
$description

Characters:
1. Orion: Courageous navigator driven by scientific wonder.
2. Lyra: Luminous sentinel protecting the balance of life.

Introduction:
Deep within the quiet pulse of existence, the legend of $title had echoed across generations. Few dared to look close enough to see the marvels hidden in plain sight.

Story:
With calm resolve, Orion set forth into the uncharted expanse. $description Every pathway pulsed with vital energy, moving like rivers of light through a silent universe. When sudden barriers blocked the journey, Lyra stepped forward, weaving a protective shield that stabilized the trembling channels. Together, they deciphered the ancient rhythms that govern vitality and protection. In that luminous quiet, they discovered that defense and harmony are one and the same—every small guardian plays an irreplaceable role in keeping the rhythm of life beating strong.

Conclusion:
United by trust and common purpose, they stood watch at the threshold of tomorrow, proud defenders of an unending journey.""";

    final encodedPrompt = Uri.encodeComponent(
        'Cinematic 8k digital painting of $title. Vibrant neon lighting, intricate details, bioluminescent glow, hyperrealistic.');
    final imageUrl =
        'https://image.pollinations.ai/prompt/$encodedPrompt?width=512&height=512&seed=42';

    final cleanText = storyText
        .replaceAll(RegExp(r'Title:.*?\n', caseSensitive: false), '')
        .replaceAll(RegExp(r'Genre:.*?\n', caseSensitive: false), '')
        .replaceAll(RegExp(r'Characters:.*?\n', caseSensitive: false), '')
        .replaceAll(RegExp(r'Concept:.*?\n', caseSensitive: false), '')
        .replaceAll(RegExp(r'Introduction:.*?\n', caseSensitive: false), '')
        .replaceAll(RegExp(r'Story:.*?\n', caseSensitive: false), '')
        .replaceAll(RegExp(r'Conclusion:.*?\n', caseSensitive: false), '')
        .replaceAll(RegExp(r'[#*_~`\r\n\t]', unicode: true), ' ')
        .replaceAll(RegExp(r'\s+'), ' ')
        .trim();
    final sample = cleanText.length > 140 ? cleanText.substring(0, 140) : cleanText;
    final encodedAudio = Uri.encodeComponent(sample);
    final fallbackAudioUrl =
        'https://translate.google.com/translate_tts?ie=UTF-8&q=$encodedAudio&tl=en&client=tw-ob';

    return StoryModel(
      id: DateTime.now().millisecondsSinceEpoch.toString(),
      title: title,
      genre: genre,
      concept: description,
      storyText: storyText,
      visualPrompt: 'Cinematic scene depicting $title in high detail.',
      imageUrl: imageUrl,
      audioUrl: fallbackAudioUrl,
    );
  }

  // Synthesize Voice Narration Audio on Demand
  Future<String?> synthesizeAudio(String text) async {
    // 1. Try backend API /api/generate_audio
    try {
      final uri = Uri.parse('$_baseUrl/api/generate_audio');
      final res = await http
          .post(
            uri,
            headers: _buildHeaders(),
            body: json.encode({'text': text}),
          )
          .timeout(const Duration(seconds: 15));
      if (res.statusCode == 200) {
        final data = json.decode(utf8.decode(res.bodyBytes));
        if (data['audio_url'] != null) {
          final path = data['audio_url'].toString();
          return path.startsWith('http') ? path : '$_baseUrl$path';
        }
      }
    } catch (_) {}

    // 2. Resilient streaming voice narration fallback
    try {
      final cleanText = text
          .replaceAll(RegExp(r'Title:.*?\n', caseSensitive: false), '')
          .replaceAll(RegExp(r'Genre:.*?\n', caseSensitive: false), '')
          .replaceAll(RegExp(r'Characters:.*?\n', caseSensitive: false), '')
          .replaceAll(RegExp(r'Concept:.*?\n', caseSensitive: false), '')
          .replaceAll(RegExp(r'Introduction:.*?\n', caseSensitive: false), '')
          .replaceAll(RegExp(r'Story:.*?\n', caseSensitive: false), '')
          .replaceAll(RegExp(r'Conclusion:.*?\n', caseSensitive: false), '')
          .replaceAll(RegExp(r'[#*_~`\r\n\t]', unicode: true), ' ')
          .replaceAll(RegExp(r'\s+'), ' ')
          .trim();
      final sample = cleanText.length > 140 ? cleanText.substring(0, 140) : cleanText;
      final encoded = Uri.encodeComponent(sample);
      return 'https://translate.google.com/translate_tts?ie=UTF-8&q=$encoded&tl=en&client=tw-ob';
    } catch (_) {
      return null;
    }
  }

  // Fetch sample stories
  Future<List<StoryModel>> getSamples() async {
    try {
      final res = await http
          .get(Uri.parse('$_baseUrl/api/samples'), headers: _buildHeaders())
          .timeout(const Duration(seconds: 4));
      if (res.statusCode == 200) {
        final data = json.decode(utf8.decode(res.bodyBytes));
        final List list = data['samples'] ?? [];
        return list.map((e) => StoryModel.fromMap(e)).toList();
      }
    } catch (_) {}
    return [];
  }

  // APK Info for in-app download
  Future<Map<String, dynamic>?> getApkInfo() async {
    try {
      final res = await http
          .get(Uri.parse('$_baseUrl/api/apk-info'), headers: _buildHeaders())
          .timeout(const Duration(seconds: 4));
      if (res.statusCode == 200) {
        return json.decode(utf8.decode(res.bodyBytes));
      }
    } catch (_) {}
    return null;
  }
}
