import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:intl/intl.dart';
import 'package:cached_network_image/cached_network_image.dart';
import '../models/story_model.dart';
import '../services/storage_service.dart';
import '../services/share_service.dart';
import '../theme/app_theme.dart';
import '../widgets/glass_container.dart';
import '../widgets/audio_player_widget.dart';
import '../services/api_service.dart';

class HistoryScreen extends StatefulWidget {
  const HistoryScreen({super.key});

  @override
  State<HistoryScreen> createState() => _HistoryScreenState();
}

class _HistoryScreenState extends State<HistoryScreen> {
  List<StoryModel> _stories = [];
  final Set<String> _selectedStoryIds = {};
  bool _isLoading = true;
  String _searchQuery = '';
  String _filterGenre = 'All';

  final List<String> _genres = [
    'All',
    'Science',
    'Fantasy',
    'Education',
    'Mythology',
    'Sci-Fi',
    'Drama'
  ];

  @override
  void initState() {
    super.initState();
    _loadStories();
  }

  Future<void> _loadStories() async {
    setState(() => _isLoading = true);
    final stories = await StorageService.getSavedStories();
    if (mounted) {
      setState(() {
        _stories = stories;
        _isLoading = false;
      });
    }
  }

  Future<void> _deleteStory(String id) async {
    await StorageService.deleteStory(id);
    _selectedStoryIds.remove(id);
    _loadStories();
    if (mounted) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Story deleted from library.')),
      );
    }
  }

  Future<void> _confirmDeleteSelected() async {
    if (_selectedStoryIds.isEmpty) return;
    final count = _selectedStoryIds.length;
    final confirmed = await showDialog<bool>(
      context: context,
      builder: (ctx) => AlertDialog(
        title: const Text('Delete Stories'),
        content: Text('Delete $count selected stories from library? This cannot be undone.'),
        actions: [
          TextButton(
            onPressed: () => Navigator.of(ctx).pop(false),
            child: const Text('Cancel'),
          ),
          ElevatedButton(
            style: ElevatedButton.styleFrom(backgroundColor: const Color(0xFFEF4444)),
            onPressed: () => Navigator.of(ctx).pop(true),
            child: const Text('Delete', style: TextStyle(color: Colors.white, fontWeight: FontWeight.bold)),
          ),
        ],
      ),
    );

    if (confirmed == true) {
      await StorageService.deleteStories(_selectedStoryIds.toList());
      setState(() {
        _selectedStoryIds.clear();
      });
      _loadStories();
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text('Deleted $count stories from library.'),
            backgroundColor: const Color(0xFFEF4444),
          ),
        );
      }
    }
  }

  void _showStoryDetails(StoryModel story) {
    final isDark = Theme.of(context).brightness == Brightness.dark;
    final primaryColor = Theme.of(context).primaryColor;
    var currentStory = story;
    bool isSynthesizing = false;

    showModalBottomSheet(
      context: context,
      isScrollControlled: true,
      backgroundColor: Colors.transparent,
      builder: (context) {
        return StatefulBuilder(
          builder: (context, setModalState) {
            return Container(
              height: MediaQuery.of(context).size.height * 0.88,
              decoration: BoxDecoration(
                color: isDark ? const Color(0xFF0D1222) : Colors.white,
                borderRadius: const BorderRadius.vertical(top: Radius.circular(24)),
                border: Border(
                  top: BorderSide(
                    color: isDark ? AppTheme.borderGlow : AppTheme.lightPrimary.withValues(alpha: 0.3),
                    width: 1.5,
                  ),
                ),
              ),
              child: Column(
                children: [
                  // Drag handle
                  Container(
                    margin: const EdgeInsets.only(top: 12),
                    width: 40,
                    height: 4,
                    decoration: BoxDecoration(
                      color: isDark ? Colors.white24 : Colors.black12,
                      borderRadius: BorderRadius.circular(2),
                    ),
                  ),
                  Expanded(
                    child: ListView(
                      padding: const EdgeInsets.all(20),
                      children: [
                        Row(
                          mainAxisAlignment: MainAxisAlignment.spaceBetween,
                          children: [
                            Container(
                              padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 4),
                              decoration: BoxDecoration(
                                color: primaryColor.withValues(alpha: 0.15),
                                borderRadius: BorderRadius.circular(12),
                                border: Border.all(color: primaryColor.withValues(alpha: 0.4)),
                              ),
                              child: Text(
                                currentStory.genre,
                                style: TextStyle(
                                  color: primaryColor,
                                  fontSize: 12,
                                  fontWeight: FontWeight.bold,
                                ),
                              ),
                            ),
                            Text(
                              DateFormat('MMM d, y • h:mm a').format(currentStory.createdAt),
                              style: TextStyle(
                                color: isDark ? AppTheme.darkTextSecondary : AppTheme.lightTextSecondary,
                                fontSize: 12,
                              ),
                            ),
                          ],
                        ),
                        const SizedBox(height: 12),
                        Text(
                          currentStory.title,
                          style: TextStyle(
                            color: isDark ? Colors.white : AppTheme.lightTextPrimary,
                            fontSize: 22,
                            fontWeight: FontWeight.bold,
                          ),
                        ),
                        const SizedBox(height: 16),
                        if (currentStory.imageUrl != null) ...[
                          ClipRRect(
                            borderRadius: BorderRadius.circular(16),
                            child: CachedNetworkImage(
                              imageUrl: currentStory.imageUrl!,
                              fit: BoxFit.cover,
                              height: 220,
                              width: double.infinity,
                            ),
                          ),
                          const SizedBox(height: 16),
                        ],
                        SelectableText(
                          currentStory.storyText,
                          style: TextStyle(
                            color: isDark ? AppTheme.darkTextPrimary : AppTheme.lightTextPrimary,
                            fontSize: 14,
                            height: 1.6,
                          ),
                        ),
                        const SizedBox(height: 16),
                        // Audio Narration Player in Saved Stories
                        Container(
                          padding: const EdgeInsets.all(14),
                          decoration: BoxDecoration(
                            color: isDark ? const Color(0xFF141C33) : const Color(0xFFF8FAFC),
                            borderRadius: BorderRadius.circular(16),
                            border: Border.all(
                              color: isDark ? AppTheme.borderGlow : AppTheme.lightPrimary.withValues(alpha: 0.25),
                            ),
                          ),
                          child: Column(
                            crossAxisAlignment: CrossAxisAlignment.start,
                            children: [
                              Row(
                                children: [
                                  Icon(Icons.graphic_eq, color: primaryColor, size: 20),
                                  const SizedBox(width: 8),
                                  Text(
                                    '🎙️ Voice Narration Audio',
                                    style: TextStyle(
                                      color: isDark ? Colors.white : AppTheme.lightTextPrimary,
                                      fontWeight: FontWeight.bold,
                                      fontSize: 14,
                                    ),
                                  ),
                                ],
                              ),
                              const SizedBox(height: 10),
                              AudioPlayerWidget(
                                audioUrl: currentStory.audioUrl,
                                isSynthesizing: isSynthesizing,
                                onSynthesizeRequested: () async {
                                  setModalState(() => isSynthesizing = true);
                                  try {
                                    final aud = await ApiService()
                                        .synthesizeAudio(currentStory.storyText);
                                    if (aud != null && aud.isNotEmpty) {
                                      final updated =
                                          currentStory.copyWith(audioUrl: aud);
                                      await StorageService.updateStory(updated);
                                      setModalState(() {
                                        currentStory = updated;
                                        isSynthesizing = false;
                                      });
                                      _loadStories();
                                    } else {
                                      setModalState(() => isSynthesizing = false);
                                    }
                                  } catch (_) {
                                    setModalState(() => isSynthesizing = false);
                                  }
                                },
                              ),
                            ],
                          ),
                        ),
                        const SizedBox(height: 20),
                        Row(
                          children: [
                            Expanded(
                              child: OutlinedButton.icon(
                                icon: const Icon(Icons.copy, size: 16),
                                label: const Text('Copy Text'),
                                style: OutlinedButton.styleFrom(
                                  foregroundColor: primaryColor,
                                  side: BorderSide(color: primaryColor),
                                  padding: const EdgeInsets.symmetric(vertical: 12),
                                  shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
                                ),
                                onPressed: () {
                                  Clipboard.setData(ClipboardData(text: currentStory.storyText));
                                  ScaffoldMessenger.of(context).showSnackBar(
                                    const SnackBar(content: Text('Copied to clipboard!')),
                                  );
                                },
                              ),
                            ),
                            const SizedBox(width: 12),
                            Expanded(
                              child: ElevatedButton.icon(
                                icon: const Icon(Icons.share, size: 16, color: Colors.white),
                                label: const Text('Share All', style: TextStyle(color: Colors.white, fontWeight: FontWeight.bold)),
                                style: ElevatedButton.styleFrom(
                                  backgroundColor: primaryColor,
                                  padding: const EdgeInsets.symmetric(vertical: 12),
                                  shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
                                ),
                                onPressed: () {
                                  ShareService.shareStory(context, currentStory);
                                },
                              ),
                            ),
                          ],
                        ),
                      ],
                    ),
                  ),
                ],
              ),
            );
          },
        );
      },
    );
  }

  @override
  Widget build(BuildContext context) {
    final isDark = Theme.of(context).brightness == Brightness.dark;
    final primaryColor = Theme.of(context).primaryColor;

    final filtered = _stories.where((s) {
      final matchesSearch = s.title.toLowerCase().contains(_searchQuery.toLowerCase()) ||
          s.concept.toLowerCase().contains(_searchQuery.toLowerCase());
      final matchesGenre = _filterGenre == 'All' || s.genre == _filterGenre;
      return matchesSearch && matchesGenre;
    }).toList();

    return Scaffold(
      appBar: AppBar(
        title: const Text('Saved Stories'),
      ),
      body: Column(
        children: [
          // Search & Filter header
          Padding(
            padding: const EdgeInsets.fromLTRB(16, 8, 16, 8),
            child: TextField(
              onChanged: (val) => setState(() => _searchQuery = val),
              decoration: InputDecoration(
                hintText: 'Search stories by title or concept...',
                prefixIcon: Icon(Icons.search, color: primaryColor),
              ),
            ),
          ),

          // Genre selector chips
          SizedBox(
            height: 44,
            child: ListView.builder(
              scrollDirection: Axis.horizontal,
              padding: const EdgeInsets.symmetric(horizontal: 16),
              itemCount: _genres.length,
              itemBuilder: (context, i) {
                final g = _genres[i];
                final isSelected = _filterGenre == g;
                return Padding(
                  padding: const EdgeInsets.only(right: 8),
                  child: FilterChip(
                    label: Text(g),
                    selected: isSelected,
                    onSelected: (val) {
                      if (val) setState(() => _filterGenre = g);
                    },
                    selectedColor: primaryColor,
                    backgroundColor: isDark ? const Color(0xFF141C33) : const Color(0xFFF1F5F9),
                    labelStyle: TextStyle(
                      color: isSelected
                          ? Colors.white
                          : (isDark ? Colors.white70 : AppTheme.lightTextSecondary),
                      fontWeight: isSelected ? FontWeight.bold : FontWeight.normal,
                      fontSize: 12,
                    ),
                    shape: RoundedRectangleBorder(
                      borderRadius: BorderRadius.circular(16),
                      side: BorderSide(
                        color: isSelected ? primaryColor : (isDark ? Colors.white12 : Colors.black12),
                      ),
                    ),
                  ),
                );
              },
            ),
          ),

          // Batch selection toolbar
          if (filtered.isNotEmpty)
            Padding(
              padding: const EdgeInsets.fromLTRB(16, 4, 16, 8),
              child: Row(
                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                children: [
                  InkWell(
                    borderRadius: BorderRadius.circular(8),
                    onTap: () {
                      setState(() {
                        final allIds = filtered.map((s) => s.id).toSet();
                        if (allIds.every(_selectedStoryIds.contains)) {
                          _selectedStoryIds.removeAll(allIds);
                        } else {
                          _selectedStoryIds.addAll(allIds);
                        }
                      });
                    },
                    child: Padding(
                      padding: const EdgeInsets.symmetric(horizontal: 4, vertical: 4),
                      child: Row(
                        children: [
                          Icon(
                            filtered.map((s) => s.id).every(_selectedStoryIds.contains)
                                ? Icons.check_box_rounded
                                : Icons.check_box_outline_blank_rounded,
                            size: 20,
                            color: primaryColor,
                          ),
                          const SizedBox(width: 6),
                          Text(
                            filtered.map((s) => s.id).every(_selectedStoryIds.contains)
                                ? 'Deselect All'
                                : 'Select All',
                            style: TextStyle(
                              color: primaryColor,
                              fontWeight: FontWeight.bold,
                              fontSize: 13,
                            ),
                          ),
                        ],
                      ),
                    ),
                  ),
                  if (_selectedStoryIds.isNotEmpty)
                    ElevatedButton.icon(
                      icon: const Icon(Icons.delete_sweep_rounded, size: 16, color: Colors.white),
                      label: Text(
                        'Delete (${_selectedStoryIds.length})',
                        style: const TextStyle(
                          color: Colors.white,
                          fontWeight: FontWeight.bold,
                          fontSize: 12,
                        ),
                      ),
                      style: ElevatedButton.styleFrom(
                        backgroundColor: const Color(0xFFEF4444),
                        padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 6),
                        minimumSize: Size.zero,
                        tapTargetSize: MaterialTapTargetSize.shrinkWrap,
                        shape: RoundedRectangleBorder(
                          borderRadius: BorderRadius.circular(10),
                        ),
                      ),
                      onPressed: _confirmDeleteSelected,
                    )
                  else
                    Text(
                      '${filtered.length} stories',
                      style: TextStyle(
                        color: isDark ? AppTheme.darkTextSecondary : AppTheme.lightTextSecondary,
                        fontSize: 12,
                      ),
                    ),
                ],
              ),
            ),

          // Story list
          Expanded(
            child: _isLoading
                ? Center(child: CircularProgressIndicator(color: primaryColor))
                : filtered.isEmpty
                    ? Center(
                        child: Column(
                          mainAxisAlignment: MainAxisAlignment.center,
                          children: [
                            Icon(Icons.auto_stories_outlined,
                                size: 64,
                                color: isDark ? Colors.white24 : Colors.black12),
                            const SizedBox(height: 16),
                            Text(
                              'No stories found in library.',
                              style: TextStyle(
                                color: isDark ? AppTheme.darkTextSecondary : AppTheme.lightTextSecondary,
                                fontSize: 16,
                              ),
                            ),
                            const SizedBox(height: 8),
                            TextButton.icon(
                              icon: Icon(Icons.add, color: primaryColor),
                              label: Text('Weave a Story Now', style: TextStyle(color: primaryColor)),
                              onPressed: () => Navigator.of(context).pop(),
                            ),
                          ],
                        ),
                      )
                    : ListView.builder(
                        padding: const EdgeInsets.all(16),
                        itemCount: filtered.length,
                        itemBuilder: (context, i) {
                          final story = filtered[i];
                          return GlassContainer(
                            margin: const EdgeInsets.only(bottom: 14),
                            padding: const EdgeInsets.all(14),
                            borderColor: isDark ? AppTheme.borderGlow : AppTheme.lightPrimary.withValues(alpha: 0.2),
                            child: InkWell(
                              onTap: () => _showStoryDetails(story),
                              child: Row(
                                crossAxisAlignment: CrossAxisAlignment.start,
                                children: [
                                  // Selection Checkbox
                                  Checkbox(
                                    value: _selectedStoryIds.contains(story.id),
                                    activeColor: primaryColor,
                                    checkColor: isDark ? Colors.black : Colors.white,
                                    visualDensity: VisualDensity.compact,
                                    materialTapTargetSize: MaterialTapTargetSize.shrinkWrap,
                                    shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(4)),
                                    onChanged: (val) {
                                      setState(() {
                                        if (val == true) {
                                          _selectedStoryIds.add(story.id);
                                        } else {
                                          _selectedStoryIds.remove(story.id);
                                        }
                                      });
                                    },
                                  ),
                                  const SizedBox(width: 4),
                                  // Thumbnail
                                  ClipRRect(
                                    borderRadius: BorderRadius.circular(12),
                                    child: story.imageUrl != null
                                        ? CachedNetworkImage(
                                            imageUrl: story.imageUrl!,
                                            width: 70,
                                            height: 70,
                                            fit: BoxFit.cover,
                                            placeholder: (_, __) => Container(
                                              width: 70,
                                              height: 70,
                                              color: isDark ? const Color(0xFF0F1524) : const Color(0xFFF1F5F9),
                                            ),
                                          )
                                        : Container(
                                            width: 70,
                                            height: 70,
                                            color: isDark ? const Color(0xFF161E33) : const Color(0xFFF1F5F9),
                                            child: Icon(Icons.book, color: primaryColor),
                                          ),
                                  ),
                                  const SizedBox(width: 14),
                                  Expanded(
                                    child: Column(
                                      crossAxisAlignment: CrossAxisAlignment.start,
                                      children: [
                                        Row(
                                          mainAxisAlignment: MainAxisAlignment.spaceBetween,
                                          children: [
                                            Container(
                                              padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 2),
                                              decoration: BoxDecoration(
                                                color: primaryColor.withValues(alpha: 0.12),
                                                borderRadius: BorderRadius.circular(8),
                                              ),
                                              child: Text(
                                                story.genre,
                                                style: TextStyle(
                                                  color: primaryColor,
                                                  fontSize: 10,
                                                  fontWeight: FontWeight.bold,
                                                ),
                                              ),
                                            ),
                                            IconButton(
                                              icon: Icon(
                                                Icons.delete_outline,
                                                size: 18,
                                                color: isDark ? Colors.white38 : Colors.black38,
                                              ),
                                              padding: EdgeInsets.zero,
                                              constraints: const BoxConstraints(),
                                              onPressed: () => _deleteStory(story.id),
                                            ),
                                          ],
                                        ),
                                        const SizedBox(height: 6),
                                        Text(
                                          story.title,
                                          maxLines: 1,
                                          overflow: TextOverflow.ellipsis,
                                          style: TextStyle(
                                            color: isDark ? Colors.white : AppTheme.lightTextPrimary,
                                            fontWeight: FontWeight.bold,
                                            fontSize: 15,
                                          ),
                                        ),
                                        const SizedBox(height: 4),
                                        Text(
                                          story.concept,
                                          maxLines: 2,
                                          overflow: TextOverflow.ellipsis,
                                          style: TextStyle(
                                            color: isDark ? AppTheme.darkTextSecondary : AppTheme.lightTextSecondary,
                                            fontSize: 12,
                                          ),
                                        ),
                                        const SizedBox(height: 8),
                                        Row(
                                          mainAxisAlignment: MainAxisAlignment.spaceBetween,
                                          children: [
                                            Row(
                                              children: [
                                                Icon(
                                                  story.audioUrl != null && story.audioUrl!.isNotEmpty
                                                      ? Icons.graphic_eq_rounded
                                                      : Icons.auto_stories_rounded,
                                                  size: 14,
                                                  color: primaryColor,
                                                ),
                                                const SizedBox(width: 4),
                                                Text(
                                                  story.audioUrl != null && story.audioUrl!.isNotEmpty
                                                      ? 'Audio Narration Ready'
                                                      : 'Tap to Read & Listen',
                                                  style: TextStyle(
                                                    color: primaryColor,
                                                    fontSize: 11,
                                                    fontWeight: FontWeight.w600,
                                                  ),
                                                ),
                                              ],
                                            ),
                                            InkWell(
                                              onTap: () => ShareService.shareStory(context, story),
                                              child: Padding(
                                                padding: const EdgeInsets.symmetric(horizontal: 4, vertical: 2),
                                                child: Row(
                                                  children: [
                                                    Icon(Icons.share_rounded, size: 13, color: primaryColor),
                                                    const SizedBox(width: 3),
                                                    Text(
                                                      'Share All',
                                                      style: TextStyle(
                                                        color: primaryColor,
                                                        fontSize: 11,
                                                        fontWeight: FontWeight.bold,
                                                      ),
                                                    ),
                                                  ],
                                                ),
                                              ),
                                            ),
                                          ],
                                        ),
                                      ],
                                    ),
                                  ),
                                ],
                              ),
                            ),
                          );
                        },
                      ),
          ),
        ],
      ),
    );
  }
}
