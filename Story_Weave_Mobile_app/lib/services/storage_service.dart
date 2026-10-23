import 'dart:convert';
import 'package:shared_preferences/shared_preferences.dart';
import '../models/story_model.dart';

class StorageService {
  static const String _keyBaseUrl = 'story_weave_base_url';
  static const String _keyApiKey = 'story_weave_api_key';
  static const String _keySavedStories = 'story_weave_saved_stories';
  static const String _keyIsDarkMode = 'story_weave_is_dark_mode';

  // In-memory fallback if platform channel fails
  static String _memBaseUrl = 'http://10.0.2.2:8000';
  static String? _memApiKey;
  static bool _memIsDarkMode = true;
  static final List<StoryModel> _memStories = [];

  static Future<bool> isDarkMode() async {
    try {
      final prefs = await SharedPreferences.getInstance();
      return prefs.getBool(_keyIsDarkMode) ?? _memIsDarkMode;
    } catch (_) {
      return _memIsDarkMode;
    }
  }

  static Future<void> setDarkMode(bool isDark) async {
    _memIsDarkMode = isDark;
    try {
      final prefs = await SharedPreferences.getInstance();
      await prefs.setBool(_keyIsDarkMode, isDark);
    } catch (_) {}
  }

  static Future<String> getBaseUrl() async {
    try {
      final prefs = await SharedPreferences.getInstance();
      return prefs.getString(_keyBaseUrl) ?? _memBaseUrl;
    } catch (_) {
      return _memBaseUrl;
    }
  }

  static Future<void> setBaseUrl(String url) async {
    _memBaseUrl = url.trim();
    try {
      final prefs = await SharedPreferences.getInstance();
      await prefs.setString(_keyBaseUrl, url.trim());
    } catch (_) {}
  }

  static Future<String?> getApiKey() async {
    try {
      final prefs = await SharedPreferences.getInstance();
      return prefs.getString(_keyApiKey) ?? _memApiKey;
    } catch (_) {
      return _memApiKey;
    }
  }

  static Future<void> setApiKey(String key) async {
    _memApiKey = key.trim();
    try {
      final prefs = await SharedPreferences.getInstance();
      await prefs.setString(_keyApiKey, key.trim());
    } catch (_) {}
  }

  static final List<StoryModel> _defaultStories = [
    StoryModel(
      id: 'story_rbc_wbc',
      title: 'RBC and WBC: Defenders of the Pulse',
      genre: 'Science',
      concept: 'Explain how red and white blood cells protect the human body in an engaging story.',
      storyText: '''Title:
RBC and WBC: Defenders of the Pulse

Genre:
Science

Concept:
How red and white blood cells protect the human body with courage and harmony.

Characters:
1. Ruby: A swift crimson voyager transporting life-giving oxygen.
2. Warren: A brave immune sentinel shielding the bloodstream.

Introduction:
Deep within the warm rivers of the human bloodstream, billions of tiny sentinels journeyed without pause. Among them, Ruby spun gracefully through the glowing arteries.

Story:
With each heartbeat, Ruby carried her golden cargo of oxygen to thirsty tissue cells. Suddenly, an alarm echoed across the vascular banks—dust microbes had slipped through a surface scratch! Ruby paused in alarm, but Warren stepped forward with calm resolve, expanding his luminous white pseudopods. With steady courage, Warren engulfed the invaders, neutralizing the threat into harmless mist. Ruby smiled warmly, delivering healing oxygen to repair the boundary. Together, hand in hand, the red voyager and white defender kept the rhythm of life beating strong.

Conclusion:
United by duty and harmony, the microscopic heroes returned to their ceaseless patrol, proud protectors of the human pulse.''',
      visualPrompt: 'Cinematic digital painting of a glowing red blood cell and white blood cell defender floating in bioluminescent fluid, 8k resolution, volumetric lighting.',
      imageUrl: 'https://image.pollinations.ai/prompt/Cinematic%20digital%20painting%20of%20a%20glowing%20red%20blood%20cell%20and%20white%20blood%20cell%20defender%20bioluminescent%208k?width=512&height=512&seed=42',
      audioUrl: 'https://translate.google.com/translate_tts?ie=UTF-8&q=Deep+within+the+warm+rivers+of+the+human+bloodstream%2C+billions+of+tiny+sentinels+journeyed+without+pause.+Among+them%2C+Ruby+spun+gracefully+through+the+glowing+arteries.&tl=en&client=tw-ob',
      createdAt: DateTime.now().subtract(const Duration(minutes: 30)),
    ),
    StoryModel(
      id: 'story_clockwork',
      title: 'The Clockwork Forest',
      genre: 'Fantasy',
      concept: 'A young tinkerer discovers trees made of brass and amber that chime in the morning breeze.',
      storyText: '''Title:
The Clockwork Forest

Genre:
Fantasy

Concept:
A harmony between mechanical artistry and living ancient nature.

Characters:
1. Lyra: An inventive apprentice with a golden pocket wrench.
2. Gideon: A gentle amber-eyed brass owl who reads the winds.

Introduction:
At the edge of the Whispering Ridge, the leaves did not rustle; they chimed. Lyra held her breath as she stepped beneath the brass boughs of the Clockwork Forest.

Story:
Every branch was spun from polished bronze and warm copper, linked by smooth emerald gears that turned in rhythm with the subterranean waterfalls. High on a silver willow, Gideon the owl clicked his beak and fluttered down. 'The sunspring is overwound,' Gideon hooted with melodic resonance. Lyra stepped forward, spotting a trapped crystal pebble between the master gear teeth. Gently aligning her golden wrench, she eased the gear into free rotation. A luminous beam of sunlight struck the grove, setting thousands of brass leaves chiming in joyous symphony.

Conclusion:
With gears spinning in peaceful balance, Lyra knew that magic and machinery could live as one heart.''',
      visualPrompt: 'Enchanted forest with brass and copper mechanical trees, glowing amber leaves, clockwork owl, cinematic 8k render, soft ethereal lighting.',
      imageUrl: 'https://image.pollinations.ai/prompt/Enchanted%20forest%20with%20brass%20mechanical%20trees%20glowing%20amber%20leaves%20clockwork%20owl%20cinematic%208k?width=512&height=512&seed=88',
      audioUrl: 'https://translate.google.com/translate_tts?ie=UTF-8&q=At+the+edge+of+the+Whispering+Ridge%2C+the+leaves+did+not+rustle%3B+they+chimed.+Lyra+held+her+breath+as+she+stepped+beneath+the+brass+boughs+of+the+Clockwork+Forest.&tl=en&client=tw-ob',
      createdAt: DateTime.now().subtract(const Duration(minutes: 60)),
    ),
  ];

  static Future<List<StoryModel>> getSavedStories() async {
    try {
      final prefs = await SharedPreferences.getInstance();
      final raw = prefs.getString(_keySavedStories);
      if (raw == null) {
        await saveStories(_defaultStories);
        return List.from(_defaultStories);
      }
      if (raw.isEmpty) return [];
      final List decoded = json.decode(raw);
      final list = decoded.map((e) => StoryModel.fromMap(e)).toList();
      // Ensure all stories have playable audio URLs
      bool changed = false;
      for (int i = 0; i < list.length; i++) {
        if (list[i].audioUrl == null || list[i].audioUrl!.isEmpty) {
          final cleanText = list[i].storyText
              .replaceAll(RegExp(r'Title:.*?\n', caseSensitive: false), '')
              .replaceAll(RegExp(r'Genre:.*?\n', caseSensitive: false), '')
              .replaceAll(RegExp(r'Characters:.*?\n', caseSensitive: false), '')
              .replaceAll(RegExp(r'[#*_~`]', unicode: true), '')
              .trim();
          final sample = cleanText.length > 500 ? cleanText.substring(0, 500) : cleanText;
          final encoded = Uri.encodeComponent(sample);
          list[i] = list[i].copyWith(
            audioUrl: 'https://translate.google.com/translate_tts?ie=UTF-8&q=$encoded&tl=en&client=tw-ob',
          );
          changed = true;
        }
      }
      if (changed) {
        await saveStories(list);
      }
      return list;
    } catch (_) {
      return _memStories.isNotEmpty ? _memStories : List.from(_defaultStories);
    }
  }

  static Future<void> saveStories(List<StoryModel> stories) async {
    _memStories.clear();
    _memStories.addAll(stories);
    try {
      final prefs = await SharedPreferences.getInstance();
      final encoded = json.encode(stories.map((e) => e.toMap()).toList());
      await prefs.setString(_keySavedStories, encoded);
    } catch (_) {}
  }

  static Future<void> saveStory(StoryModel story) async {
    _memStories.removeWhere((item) => item.id == story.id);
    _memStories.insert(0, story);
    try {
      final prefs = await SharedPreferences.getInstance();
      final list = await getSavedStories();
      list.removeWhere((item) => item.id == story.id);
      list.insert(0, story);
      final encoded = json.encode(list.map((e) => e.toMap()).toList());
      await prefs.setString(_keySavedStories, encoded);
    } catch (_) {}
  }

  static Future<void> updateStory(StoryModel story) async {
    await saveStory(story);
  }

  static Future<void> deleteStory(String id) async {
    _memStories.removeWhere((item) => item.id == id);
    try {
      final prefs = await SharedPreferences.getInstance();
      final list = await getSavedStories();
      list.removeWhere((item) => item.id == id);
      final encoded = json.encode(list.map((e) => e.toMap()).toList());
      await prefs.setString(_keySavedStories, encoded);
    } catch (_) {}
  }

  static Future<void> deleteStories(List<String> ids) async {
    final idSet = ids.toSet();
    _memStories.removeWhere((item) => idSet.contains(item.id));
    try {
      final prefs = await SharedPreferences.getInstance();
      final list = await getSavedStories();
      list.removeWhere((item) => idSet.contains(item.id));
      final encoded = json.encode(list.map((e) => e.toMap()).toList());
      await prefs.setString(_keySavedStories, encoded);
    } catch (_) {}
  }
}
