import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:cached_network_image/cached_network_image.dart';
import '../models/story_model.dart';
import '../services/api_service.dart';
import '../services/storage_service.dart';
import '../theme/app_theme.dart';
import '../widgets/glass_container.dart';
import '../widgets/audio_player_widget.dart';
import '../widgets/custom_drawer.dart';
import '../services/share_service.dart';
import '../widgets/day_night_switch.dart';
import 'history_screen.dart';
import 'about_screen.dart';

class HomeScreen extends StatefulWidget {
  final bool isDarkMode;
  final VoidCallback onToggleTheme;

  const HomeScreen({
    super.key,
    required this.isDarkMode,
    required this.onToggleTheme,
  });

  @override
  State<HomeScreen> createState() => _HomeScreenState();
}

class _HomeScreenState extends State<HomeScreen> {
  final TextEditingController _titleController = TextEditingController(
    text: 'RBC and WBC: Defenders of the Pulse',
  );
  final TextEditingController _descController = TextEditingController(
    text:
        'Explain how red and white blood cells protect the human body in an engaging story.',
  );

  String _selectedGenre = 'Science';
  final List<String> _genres = [
    'Science',
    'Fantasy',
    'Education',
    'Mythology',
    'Sci-Fi',
    'Drama'
  ];

  bool _isGenerating = false;
  String _generationProgress = '';
  StoryModel? _currentStory;
  bool _isAudioSynthesizing = false;

  @override
  void initState() {
    super.initState();
    // Silent background health check
    ApiService().checkHealth();
  }

  Future<void> _generateStory() async {
    final title = _titleController.text.trim();
    final desc = _descController.text.trim();

    if (title.isEmpty || desc.isEmpty) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(
          content: Text('Please enter both a Story Title and Concept.'),
          backgroundColor: Color(0xFFE53935),
        ),
      );
      return;
    }

    FocusScope.of(context).unfocus();
    setState(() {
      _isGenerating = true;
      _generationProgress = 'Weaving your narrative...';
    });

    try {
      var story = await ApiService().generateStory(
        title: title,
        genre: _selectedGenre,
        description: desc,
        onProgress: (status) {
          if (mounted) setState(() => _generationProgress = status);
        },
      );

      // Auto-synthesize voice narration if not pre-generated
      if (story.audioUrl == null || story.audioUrl!.isEmpty) {
        if (mounted) setState(() => _generationProgress = 'Synthesizing voice narration...');
        final aud = await ApiService().synthesizeAudio(story.storyText);
        if (aud != null) {
          story = story.copyWith(audioUrl: aud);
        }
      }

      // Auto save to local history
      await StorageService.saveStory(story);

      if (mounted) {
        setState(() {
          _currentStory = story;
          _isGenerating = false;
        });
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(
            content: Text('✨ Story woven and saved to library!'),
            backgroundColor: Color(0xFF10B981),
          ),
        );
      }
    } catch (e) {
      if (mounted) {
        setState(() => _isGenerating = false);
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text('Generation issue: $e'),
            backgroundColor: const Color(0xFFE53935),
          ),
        );
      }
    }
  }

  void _handlePreset(String title, String genre, String desc) {
    setState(() {
      _titleController.text = title;
      _selectedGenre = genre;
      _descController.text = desc;
    });
  }

  void _handleDrawerNavigation(String route) {
    Navigator.of(context).pop(); // Close drawer
    if (route == 'history') {
      Navigator.of(context).push(
        MaterialPageRoute(builder: (_) => const HistoryScreen()),
      );
    } else if (route == 'about') {
      Navigator.of(context).push(
        MaterialPageRoute(builder: (_) => const AboutScreen()),
      );
    }
  }

  @override
  Widget build(BuildContext context) {
    final isDark = widget.isDarkMode;
    final primaryColor = Theme.of(context).primaryColor;

    return Scaffold(
      drawer: CustomDrawer(
        activeRoute: 'home',
        onNavigate: _handleDrawerNavigation,
        isDarkMode: widget.isDarkMode,
        onToggleTheme: widget.onToggleTheme,
      ),
      appBar: AppBar(
        title: Row(
          children: [
            Container(
              width: 32,
              height: 32,
              decoration: const BoxDecoration(shape: BoxShape.circle),
              child: ClipOval(
                child: Image.asset(
                  'assets/icon/app_icon.png',
                  fit: BoxFit.cover,
                  errorBuilder: (_, __, ___) => Icon(
                    Icons.auto_stories,
                    color: primaryColor,
                    size: 24,
                  ),
                ),
              ),
            ),
            const SizedBox(width: 10),
            ShaderMask(
              shaderCallback: (bounds) => (isDark
                      ? AppTheme.brandGradient
                      : AppTheme.lightBrandGradient)
                  .createShader(bounds),
              child: const Text(
                'Story Weave',
                style: TextStyle(
                  color: Colors.white,
                  fontWeight: FontWeight.w800,
                  fontSize: 20,
                ),
              ),
            ),
          ],
        ),
        actions: [
          Center(
            child: Padding(
              padding: const EdgeInsets.only(right: 14),
              child: DayNightSwitch(
                isDarkMode: widget.isDarkMode,
                onToggle: (_) => widget.onToggleTheme(),
                width: 66,
                height: 34,
              ),
            ),
          ),
        ],
      ),
      body: SingleChildScrollView(
        padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // Title and Tagline Header
            Container(
              margin: const EdgeInsets.only(top: 4, bottom: 16),
              padding: const EdgeInsets.symmetric(horizontal: 8),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    '📖 Story Weave',
                    style: Theme.of(context).textTheme.displayMedium?.copyWith(
                          fontWeight: FontWeight.w800,
                          letterSpacing: -0.5,
                          color: isDark ? Colors.white : AppTheme.lightTextPrimary,
                        ),
                  ),
                  const SizedBox(height: 4),
                  Text(
                    'Fusing Emotion, Vision & Voice for Intelligent Storytelling',
                    style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                          color: isDark
                              ? AppTheme.darkTextSecondary
                              : AppTheme.lightTextSecondary,
                        ),
                  ),
                ],
              ),
            ),

            // Concept Presets
            SizedBox(
              height: 38,
              child: ListView(
                scrollDirection: Axis.horizontal,
                children: [
                  ActionChip(
                    backgroundColor:
                        isDark ? const Color(0xFF141C33) : const Color(0xFFF1F5F9),
                    side: BorderSide(
                        color: isDark
                            ? const Color(0x3300E5FF)
                            : const Color(0x330284C7)),
                    avatar: const Icon(Icons.bloodtype_outlined,
                        size: 16, color: Color(0xFFFF5252)),
                    label: Text('RBC & WBC',
                        style: TextStyle(
                            fontSize: 12,
                            color: isDark
                                ? Colors.white
                                : AppTheme.lightTextPrimary)),
                    onPressed: () => _handlePreset(
                      'RBC and WBC: Defenders of the Pulse',
                      'Science',
                      'Explain how red and white blood cells protect the human body in an engaging story.',
                    ),
                  ),
                  const SizedBox(width: 8),
                  ActionChip(
                    backgroundColor:
                        isDark ? const Color(0xFF141C33) : const Color(0xFFF1F5F9),
                    side: BorderSide(
                        color: isDark
                            ? const Color(0x3300E5FF)
                            : const Color(0x330284C7)),
                    avatar: const Icon(Icons.forest_outlined,
                        size: 16, color: Color(0xFF10B981)),
                    label: Text('Clockwork Forest',
                        style: TextStyle(
                            fontSize: 12,
                            color: isDark
                                ? Colors.white
                                : AppTheme.lightTextPrimary)),
                    onPressed: () => _handlePreset(
                      'The Clockwork Forest',
                      'Fantasy',
                      'A young tinkerer discovers trees made of brass and amber that chime in the morning breeze.',
                    ),
                  ),
                  const SizedBox(width: 8),
                  ActionChip(
                    backgroundColor:
                        isDark ? const Color(0xFF141C33) : const Color(0xFFF1F5F9),
                    side: BorderSide(
                        color: isDark
                            ? const Color(0x3300E5FF)
                            : const Color(0x330284C7)),
                    avatar: Icon(Icons.rocket_launch_outlined,
                        size: 16,
                        color: isDark
                            ? AppTheme.secondaryNeon
                            : AppTheme.lightSecondary),
                    label: Text('Stellar Voyage',
                        style: TextStyle(
                            fontSize: 12,
                            color: isDark
                                ? Colors.white
                                : AppTheme.lightTextPrimary)),
                    onPressed: () => _handlePreset(
                      'The Starlit Odyssey',
                      'Sci-Fi',
                      'Two explorers discover a dormant crystalline satellite singing forgotten songs of peace.',
                    ),
                  ),
                ],
              ),
            ),

            const SizedBox(height: 16),

            // Main Input Glass Card
            GlassContainer(
              borderColor: isDark
                  ? AppTheme.borderGlow
                  : AppTheme.lightPrimary.withValues(alpha: 0.25),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  // Story Title
                  Text(
                    'Story Title',
                    style: TextStyle(
                      color: isDark ? AppTheme.darkTextPrimary : AppTheme.lightTextPrimary,
                      fontWeight: FontWeight.w600,
                      fontSize: 13,
                    ),
                  ),
                  const SizedBox(height: 8),
                  TextField(
                    controller: _titleController,
                    style: TextStyle(
                      color: isDark ? Colors.white : AppTheme.lightTextPrimary,
                      fontSize: 15,
                    ),
                    decoration: InputDecoration(
                      hintText: 'e.g. RBC and WBC',
                      prefixIcon: Icon(Icons.auto_stories_rounded,
                          color: primaryColor, size: 20),
                    ),
                  ),

                  const SizedBox(height: 16),

                  // Genre Selector
                  Text(
                    'Genre',
                    style: TextStyle(
                      color: isDark ? AppTheme.darkTextPrimary : AppTheme.lightTextPrimary,
                      fontWeight: FontWeight.w600,
                      fontSize: 13,
                    ),
                  ),
                  const SizedBox(height: 8),
                  Wrap(
                    spacing: 8,
                    runSpacing: 6,
                    children: _genres.map((g) {
                      final isSelected = _selectedGenre == g;
                      return ChoiceChip(
                        label: Text(g),
                        selected: isSelected,
                        onSelected: (val) {
                          if (val) setState(() => _selectedGenre = g);
                        },
                        selectedColor: primaryColor,
                        backgroundColor: isDark
                            ? const Color(0xFF0F1524)
                            : const Color(0xFFF1F5F9),
                        labelStyle: TextStyle(
                          color: isSelected
                              ? Colors.white
                              : (isDark ? Colors.white70 : AppTheme.lightTextSecondary),
                          fontWeight:
                              isSelected ? FontWeight.bold : FontWeight.normal,
                          fontSize: 12,
                        ),
                        shape: RoundedRectangleBorder(
                          borderRadius: BorderRadius.circular(20),
                          side: BorderSide(
                            color: isSelected
                                ? primaryColor
                                : (isDark ? Colors.white12 : Colors.black12),
                          ),
                        ),
                      );
                    }).toList(),
                  ),

                  const SizedBox(height: 16),

                  // Description / Concept
                  Text(
                    'Story Description / Concept',
                    style: TextStyle(
                      color: isDark ? AppTheme.darkTextPrimary : AppTheme.lightTextPrimary,
                      fontWeight: FontWeight.w600,
                      fontSize: 13,
                    ),
                  ),
                  const SizedBox(height: 8),
                  TextField(
                    controller: _descController,
                    maxLines: 3,
                    style: TextStyle(
                      color: isDark ? Colors.white : AppTheme.lightTextPrimary,
                      fontSize: 14,
                    ),
                    decoration: const InputDecoration(
                      hintText:
                          'Explain how red and white blood cells protect the human body...',
                    ),
                  ),

                  const SizedBox(height: 20),

                  // Generate Button
                  Container(
                    width: double.infinity,
                    height: 52,
                    decoration: BoxDecoration(
                      gradient: isDark
                          ? AppTheme.brandGradient
                          : AppTheme.lightBrandGradient,
                      borderRadius: BorderRadius.circular(14),
                      boxShadow: [
                        BoxShadow(
                          color: primaryColor.withValues(alpha: 0.35),
                          blurRadius: 15,
                          offset: const Offset(0, 4),
                        ),
                      ],
                    ),
                    child: Material(
                      color: Colors.transparent,
                      child: InkWell(
                        borderRadius: BorderRadius.circular(14),
                        onTap: _isGenerating ? null : _generateStory,
                        child: Center(
                          child: _isGenerating
                              ? Row(
                                  mainAxisAlignment: MainAxisAlignment.center,
                                  children: [
                                    const SizedBox(
                                      width: 20,
                                      height: 20,
                                      child: CircularProgressIndicator(
                                        strokeWidth: 2.5,
                                        color: Colors.white,
                                      ),
                                    ),
                                    const SizedBox(width: 12),
                                    Text(
                                      _generationProgress,
                                      style: const TextStyle(
                                        color: Colors.white,
                                        fontWeight: FontWeight.bold,
                                        fontSize: 14,
                                      ),
                                    ),
                                  ],
                                )
                              : const Row(
                                  mainAxisAlignment: MainAxisAlignment.center,
                                  children: [
                                    Text(
                                      '✨ Generate Story Weave',
                                      style: TextStyle(
                                        color: Colors.white,
                                        fontWeight: FontWeight.w800,
                                        fontSize: 16,
                                        letterSpacing: 0.3,
                                      ),
                                    ),
                                  ],
                                ),
                        ),
                      ),
                    ),
                  ),
                ],
              ),
            ),

            const SizedBox(height: 24),

            // Generated Output Section
            if (_currentStory != null) ...[
              // Narrative Section
              GlassContainer(
                borderColor: isDark
                    ? AppTheme.borderMagentaGlow
                    : AppTheme.lightSecondary.withValues(alpha: 0.25),
                gradient: isDark
                    ? AppTheme.darkAccentCardGradient
                    : AppTheme.lightAccentCardGradient,
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Row(
                      mainAxisAlignment: MainAxisAlignment.spaceBetween,
                      children: [
                        Row(
                          children: [
                            Icon(Icons.history_edu,
                                color: isDark
                                    ? AppTheme.secondaryNeon
                                    : AppTheme.lightSecondary,
                                size: 22),
                            const SizedBox(width: 8),
                            Text(
                              '📜 Generated Story',
                              style: Theme.of(context)
                                  .textTheme
                                  .titleLarge
                                  ?.copyWith(
                                    color: isDark ? Colors.white : AppTheme.lightTextPrimary,
                                    fontWeight: FontWeight.bold,
                                  ),
                            ),
                          ],
                        ),
                        Row(
                          children: [
                            IconButton(
                              icon: Icon(Icons.copy,
                                  size: 18,
                                  color: isDark
                                      ? AppTheme.darkTextSecondary
                                      : AppTheme.lightTextSecondary),
                              tooltip: 'Copy Story',
                              onPressed: () {
                                Clipboard.setData(ClipboardData(
                                    text: _currentStory!.storyText));
                                ScaffoldMessenger.of(context).showSnackBar(
                                  const SnackBar(
                                    content: Text('Story copied to clipboard!'),
                                  ),
                                );
                              },
                            ),
                            IconButton(
                              icon: Icon(Icons.share,
                                  size: 18,
                                  color: isDark
                                      ? AppTheme.darkTextSecondary
                                      : AppTheme.lightTextSecondary),
                              tooltip: 'Share',
                              onPressed: () {
                                ShareService.shareStory(context, _currentStory!);
                              },
                            ),
                          ],
                        ),
                      ],
                    ),
                    Divider(
                      color: isDark ? Colors.white12 : Colors.black12,
                      height: 20,
                    ),
                    SelectableText(
                      _currentStory!.storyText,
                      style: TextStyle(
                        color: isDark
                            ? AppTheme.darkTextPrimary
                            : AppTheme.lightTextPrimary,
                        fontSize: 14,
                        height: 1.6,
                      ),
                    ),
                  ],
                ),
              ),

              const SizedBox(height: 16),

              // Illustration Section
              if (_currentStory!.imageUrl != null)
                GlassContainer(
                  borderColor: isDark
                      ? AppTheme.borderGlow
                      : AppTheme.lightPrimary.withValues(alpha: 0.25),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Row(
                        children: [
                          Icon(Icons.image_outlined,
                              color: primaryColor, size: 22),
                          const SizedBox(width: 8),
                          Text(
                            '🖼 Generated Image',
                            style: Theme.of(context)
                                .textTheme
                                .titleLarge
                                ?.copyWith(
                                  color: isDark ? Colors.white : AppTheme.lightTextPrimary,
                                  fontWeight: FontWeight.bold,
                                ),
                          ),
                        ],
                      ),
                      const SizedBox(height: 14),
                      ClipRRect(
                        borderRadius: BorderRadius.circular(14),
                        child: CachedNetworkImage(
                          imageUrl: _currentStory!.imageUrl!,
                          fit: BoxFit.cover,
                          width: double.infinity,
                          placeholder: (_, __) => Container(
                            height: 240,
                            color: isDark
                                ? const Color(0xFF0F1524)
                                : const Color(0xFFF1F5F9),
                            child: Center(
                              child: CircularProgressIndicator(
                                  color: primaryColor),
                            ),
                          ),
                          errorWidget: (_, __, ___) => Container(
                            height: 200,
                            color: isDark
                                ? const Color(0xFF0F1524)
                                : const Color(0xFFF1F5F9),
                            child: const Center(
                              child: Icon(Icons.broken_image,
                                  color: Colors.black26, size: 48),
                            ),
                          ),
                        ),
                      ),
                      if (_currentStory!.visualPrompt != null) ...[
                        const SizedBox(height: 10),
                        Text(
                          _currentStory!.visualPrompt!,
                          style: TextStyle(
                            color: isDark
                                ? AppTheme.darkTextSecondary
                                : AppTheme.lightTextSecondary,
                            fontSize: 12,
                            fontStyle: FontStyle.italic,
                          ),
                        ),
                      ],
                    ],
                  ),
                ),

              const SizedBox(height: 16),

              // Audio Narration Section
              GlassContainer(
                borderColor: isDark
                    ? AppTheme.borderGlow
                    : AppTheme.lightPrimary.withValues(alpha: 0.25),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Row(
                      children: [
                        Icon(Icons.graphic_eq,
                            color: primaryColor, size: 22),
                        const SizedBox(width: 8),
                        Text(
                          '🔊 Read Aloud Story',
                          style: Theme.of(context)
                              .textTheme
                              .titleLarge
                              ?.copyWith(
                                color: isDark ? Colors.white : AppTheme.lightTextPrimary,
                                fontWeight: FontWeight.bold,
                              ),
                        ),
                      ],
                    ),
                    const SizedBox(height: 12),
                    AudioPlayerWidget(
                      audioUrl: _currentStory!.audioUrl,
                      isSynthesizing: _isAudioSynthesizing,
                      onSynthesizeRequested: () async {
                        setState(() => _isAudioSynthesizing = true);
                        try {
                          final aud = await ApiService()
                              .synthesizeAudio(_currentStory!.storyText);
                          if (!mounted) return;
                          if (aud != null && aud.isNotEmpty) {
                            final updated =
                                _currentStory!.copyWith(audioUrl: aud);
                            await StorageService.updateStory(updated);
                            setState(() {
                              _currentStory = updated;
                              _isAudioSynthesizing = false;
                            });
                            ScaffoldMessenger.of(context).showSnackBar(
                              const SnackBar(
                                content: Text(
                                    '✨ Audio ready! Press play to listen.'),
                                backgroundColor: Color(0xFF10B981),
                              ),
                            );
                          } else {
                            setState(() => _isAudioSynthesizing = false);
                            ScaffoldMessenger.of(context).showSnackBar(
                              const SnackBar(
                                content: Text(
                                    'Could not synthesize audio. Please try again.'),
                                backgroundColor: Color(0xFFE53935),
                              ),
                            );
                          }
                        } catch (e) {
                          if (mounted) {
                            setState(() => _isAudioSynthesizing = false);
                          }
                        }
                      },
                    ),
                  ],
                ),
              ),
            ],

            const SizedBox(height: 40),
          ],
        ),
      ),
    );
  }
}
