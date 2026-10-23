import 'dart:io';
import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;
import 'package:path_provider/path_provider.dart';
import 'package:share_plus/share_plus.dart';
import '../models/story_model.dart';
import 'api_service.dart';

class ShareService {
  static Future<void> shareStory(BuildContext context, StoryModel story) async {
    final scaffold = ScaffoldMessenger.of(context);
    
    scaffold.showSnackBar(
      const SnackBar(
        content: Text('📦 Preparing narrative text, illustration & audio to share...'),
        duration: Duration(seconds: 2),
      ),
    );

    final List<XFile> files = [];
    final tempDir = await getTemporaryDirectory();

    // 1. Download & attach illustration image if available
    if (story.imageUrl != null && story.imageUrl!.isNotEmpty) {
      try {
        final imgUrl = story.imageUrl!;
        if (imgUrl.startsWith('http://') || imgUrl.startsWith('https://')) {
          final res = await http.get(
            Uri.parse(imgUrl),
            headers: {'User-Agent': 'Mozilla/5.0 (Linux; Android 10; Mobile)'},
          ).timeout(const Duration(seconds: 10));
          if (res.statusCode == 200 && res.bodyBytes.isNotEmpty) {
            final imgFile = File('${tempDir.path}/story_${story.id}_illustration.png');
            await imgFile.writeAsBytes(res.bodyBytes);
            files.add(XFile(imgFile.path, mimeType: 'image/png', name: '${story.title}_illustration.png'));
          }
        } else if (File(imgUrl).existsSync()) {
          files.add(XFile(imgUrl, mimeType: 'image/png'));
        }
      } catch (e) {
        debugPrint('Image share fetch error: $e');
      }
    }

    // 2. Download & attach narration audio (synthesize if not present yet or if fetch fails)
    String? audUrl = story.audioUrl;
    if (audUrl == null || audUrl.isEmpty) {
      try {
        audUrl = await ApiService().synthesizeAudio(story.storyText);
      } catch (e) {
        debugPrint('Audio synthesis for share error: $e');
      }
    }

    bool audioAdded = false;
    if (audUrl != null && audUrl.isNotEmpty) {
      try {
        if (audUrl.startsWith('http://') || audUrl.startsWith('https://')) {
          final res = await http.get(
            Uri.parse(audUrl),
            headers: {'User-Agent': 'Mozilla/5.0 (Linux; Android 10; Mobile) AppleWebKit/537.36'},
          ).timeout(const Duration(seconds: 12));
          if (res.statusCode == 200 && res.bodyBytes.isNotEmpty) {
            final audFile = File('${tempDir.path}/story_${story.id}_narration.mp3');
            await audFile.writeAsBytes(res.bodyBytes);
            files.add(XFile(audFile.path, mimeType: 'audio/mpeg', name: 'narration.mp3'));
            audioAdded = true;
          }
        } else if (File(audUrl).existsSync()) {
          files.add(XFile(audUrl, mimeType: 'audio/mpeg'));
          audioAdded = true;
        }
      } catch (e) {
        debugPrint('Audio share fetch error: $e');
      }
    }

    // If initial fetch failed (e.g. stale URL), re-synthesize fresh audio and retry download
    if (!audioAdded) {
      try {
        final freshUrl = await ApiService().synthesizeAudio(story.storyText);
        if (freshUrl != null && (freshUrl.startsWith('http://') || freshUrl.startsWith('https://'))) {
          final res = await http.get(
            Uri.parse(freshUrl),
            headers: {'User-Agent': 'Mozilla/5.0 (Linux; Android 10; Mobile) AppleWebKit/537.36'},
          ).timeout(const Duration(seconds: 12));
          if (res.statusCode == 200 && res.bodyBytes.isNotEmpty) {
            final audFile = File('${tempDir.path}/story_${story.id}_narration.mp3');
            await audFile.writeAsBytes(res.bodyBytes);
            files.add(XFile(audFile.path, mimeType: 'audio/mpeg', name: 'narration.mp3'));
          }
        }
      } catch (e) {
        debugPrint('Fresh audio synthesis retry failed: $e');
      }
    }

    final shareText = '''📖 ${story.title}
Genre: ${story.genre}

${story.storyText}

✨ Fusing Emotion, Vision & Voice — Woven with Story Weave AI
Developed by Kokala Sai Teja''';

    try {
      if (files.isNotEmpty) {
        await Share.shareXFiles(
          files,
          text: shareText,
          subject: 'Story Weave: ${story.title}',
        );
      } else {
        await Share.share(
          shareText,
          subject: 'Story Weave: ${story.title}',
        );
      }
    } catch (e) {
      debugPrint('Share sheet invocation error: $e');
      await Share.share(shareText);
    }
  }
}
