import 'package:flutter/material.dart';
import 'package:url_launcher/url_launcher.dart';
import '../theme/app_theme.dart';
import '../widgets/glass_container.dart';

class AboutScreen extends StatelessWidget {
  const AboutScreen({super.key});

  Future<void> _launchUrl(BuildContext context, String url) async {
    final uri = Uri.parse(url);
    try {
      final launched = await launchUrl(uri, mode: LaunchMode.externalApplication);
      if (!launched) {
        await launchUrl(uri, mode: LaunchMode.platformDefault);
      }
    } catch (e) {
      if (context.mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('Could not open link: $url')),
        );
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    final isDark = Theme.of(context).brightness == Brightness.dark;
    final primaryColor = Theme.of(context).primaryColor;

    return Scaffold(
      appBar: AppBar(
        title: const Text('🌟 Motive & Vision'),
      ),
      body: SingleChildScrollView(
        padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
        child: Column(
          children: [
            const SizedBox(height: 8),
            // Logo & Title
            Center(
              child: Container(
                width: 86,
                height: 86,
                decoration: BoxDecoration(
                  shape: BoxShape.circle,
                  boxShadow: [
                    BoxShadow(
                      color: primaryColor.withValues(alpha: 0.35),
                      blurRadius: 18,
                      spreadRadius: 2,
                    ),
                  ],
                ),
                child: ClipOval(
                  child: Image.asset(
                    'assets/icon/app_icon.png',
                    fit: BoxFit.cover,
                  ),
                ),
              ),
            ),
            const SizedBox(height: 14),
            ShaderMask(
              shaderCallback: (bounds) => (isDark
                      ? AppTheme.brandGradient
                      : AppTheme.lightBrandGradient)
                  .createShader(bounds),
              child: const Text(
                'Story Weave',
                style: TextStyle(
                  color: Colors.white,
                  fontSize: 26,
                  fontWeight: FontWeight.w800,
                  letterSpacing: 0.5,
                ),
              ),
            ),
            const SizedBox(height: 4),
            Text(
              'Fusing Emotion, Vision & Voice for Intelligent Storytelling',
              textAlign: TextAlign.center,
              style: TextStyle(
                color: isDark ? AppTheme.darkTextSecondary : AppTheme.lightTextSecondary,
                fontSize: 13,
              ),
            ),
            const SizedBox(height: 8),
            Container(
              padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 4),
              decoration: BoxDecoration(
                color: primaryColor.withValues(alpha: 0.12),
                borderRadius: BorderRadius.circular(12),
                border: Border.all(color: primaryColor.withValues(alpha: 0.4)),
              ),
              child: Text(
                'v1.0.0 • Intelligent Storytelling Monorepo',
                style: TextStyle(
                  color: primaryColor,
                  fontSize: 11,
                  fontWeight: FontWeight.bold,
                ),
              ),
            ),

            const SizedBox(height: 20),

            // Why This Project Was Made (Our Motive)
            GlassContainer(
              borderColor: isDark ? AppTheme.borderGlow : AppTheme.lightPrimary.withValues(alpha: 0.25),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Row(
                    children: [
                      Icon(Icons.lightbulb_rounded, color: isDark ? AppTheme.primaryNeon : AppTheme.lightPrimary, size: 22),
                      const SizedBox(width: 8),
                      Text(
                        '💡 Why Story Weave Was Made',
                        style: TextStyle(
                          color: isDark ? Colors.white : AppTheme.lightTextPrimary,
                          fontSize: 16,
                          fontWeight: FontWeight.bold,
                        ),
                      ),
                    ],
                  ),
                  const SizedBox(height: 10),
                  Text(
                    'Story Weave was crafted with the vision of making imaginative storytelling deeply immersive, emotional, and accessible for everyone — from young curious minds and children to educators, parents, and authors.',
                    style: TextStyle(
                      color: isDark ? AppTheme.darkTextSecondary : AppTheme.lightTextSecondary,
                      fontSize: 13,
                      height: 1.5,
                    ),
                  ),
                  const SizedBox(height: 8),
                  Text(
                    'By fusing three sensory modalities — literary narrative, visual artwork, and voice narration — Story Weave transforms simple concepts (like how blood cells defend the human body or distant stellar voyages) into unforgettable, multisensory fairytales.',
                    style: TextStyle(
                      color: isDark ? AppTheme.darkTextSecondary : AppTheme.lightTextSecondary,
                      fontSize: 13,
                      height: 1.5,
                    ),
                  ),
                ],
              ),
            ),

            const SizedBox(height: 16),

            // Current Features (v1.0.0)
            GlassContainer(
              borderColor: isDark ? AppTheme.borderGlow : AppTheme.lightPrimary.withValues(alpha: 0.2),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    '✨ Current Features (v1.0.0)',
                    style: TextStyle(
                      color: isDark ? Colors.white : AppTheme.lightTextPrimary,
                      fontSize: 16,
                      fontWeight: FontWeight.bold,
                    ),
                  ),
                  const SizedBox(height: 14),
                  _buildFeatureRow(
                    context,
                    Icons.auto_stories,
                    'Intelligent Gemini Narrative Engine',
                    'Generates wholesome, emotionally resonant stories with structured character introductions, plots, and morals.',
                  ),
                  _buildFeatureRow(
                    context,
                    Icons.brush_outlined,
                    'Cinematic 8K Cover Artwork',
                    'Automatically crafts visual prompt descriptions and renders breathtaking art matching the story atmosphere.',
                  ),
                  _buildFeatureRow(
                    context,
                    Icons.record_voice_over_outlined,
                    'Voice Narration (Read Aloud)',
                    'Integrated text-to-speech audio synthesis with real-time waveform controls and seek bars on web and mobile.',
                  ),
                  _buildFeatureRow(
                    context,
                    Icons.bookmark_added_outlined,
                    'Story Library & Audio Playback',
                    'Persistent local library allowing users to revisit saved tales and listen to full voice narrations anytime.',
                  ),
                ],
              ),
            ),

            const SizedBox(height: 16),

            // Newly Updated & Roadmap Features
            GlassContainer(
              borderColor: isDark ? AppTheme.borderMagentaGlow : AppTheme.lightSecondary.withValues(alpha: 0.25),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    '🚀 Newly Updated & Roadmap Features',
                    style: TextStyle(
                      color: isDark ? Colors.white : AppTheme.lightTextPrimary,
                      fontSize: 16,
                      fontWeight: FontWeight.bold,
                    ),
                  ),
                  const SizedBox(height: 14),
                  _buildFeatureRow(
                    context,
                    Icons.share_outlined,
                    'Multimodal Sharing Sheet',
                    'Now shares the complete story: narrative text, cover illustration image, and audio narration file simultaneously.',
                  ),
                  _buildFeatureRow(
                    context,
                    Icons.audiotrack_outlined,
                    'Saved Stories Voice Narration',
                    'Saved stories now include full audio playback and MP3 download options inside the Library tab.',
                  ),
                  _buildFeatureRow(
                    context,
                    Icons.nightlight_round,
                    'Animated Day / Night Capsule',
                    'Sleek celestial toggle with glowing celestial bodies and stars matching interactive child-friendly aesthetics.',
                  ),
                  _buildFeatureRow(
                    context,
                    Icons.android,
                    'Direct APK Installation',
                    'One-tap downloads for modern ARM64-v8a, ARMv7a, x86_64, and Universal APKs straight from the web portal.',
                  ),
                ],
              ),
            ),

            const SizedBox(height: 16),

            // Developer Card
            GlassContainer(
              borderColor: isDark ? AppTheme.borderGlow : AppTheme.lightPrimary.withValues(alpha: 0.25),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    '🧑‍💻 Developer',
                    style: TextStyle(
                      color: isDark ? Colors.white : AppTheme.lightTextPrimary,
                      fontSize: 16,
                      fontWeight: FontWeight.bold,
                    ),
                  ),
                  const SizedBox(height: 10),
                  Text(
                    'Kokala Sai Teja',
                    style: TextStyle(
                      color: isDark ? Colors.white : AppTheme.lightTextPrimary,
                      fontSize: 18,
                      fontWeight: FontWeight.bold,
                    ),
                  ),
                  const SizedBox(height: 4),
                  Text(
                    'Full-Stack & Mobile AI Developer',
                    style: TextStyle(
                      color: isDark ? AppTheme.darkTextSecondary : AppTheme.lightTextSecondary,
                      fontSize: 13,
                    ),
                  ),
                  const SizedBox(height: 18),
                  Row(
                    children: [
                      // LinkedIn Button
                      Expanded(
                        child: ElevatedButton.icon(
                          icon: const Icon(Icons.link, size: 16, color: Colors.white),
                          label: const Text(
                            'LinkedIn Profile',
                            style: TextStyle(color: Colors.white, fontWeight: FontWeight.bold, fontSize: 13),
                          ),
                          style: ElevatedButton.styleFrom(
                            backgroundColor: const Color(0xFF0077B5),
                            padding: const EdgeInsets.symmetric(vertical: 12),
                            shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
                          ),
                          onPressed: () => _launchUrl(
                            context,
                            'https://www.linkedin.com/in/sai-teja-kokala-245a12299?utm_source=share_via&utm_content=profile&utm_medium=member_android',
                          ),
                        ),
                      ),
                      const SizedBox(width: 12),
                      // Email Button
                      Expanded(
                        child: ElevatedButton.icon(
                          icon: const Icon(Icons.email_outlined, size: 16, color: Colors.white),
                          label: const Text(
                            'Email Me',
                            style: TextStyle(color: Colors.white, fontWeight: FontWeight.bold, fontSize: 13),
                          ),
                          style: ElevatedButton.styleFrom(
                            backgroundColor: const Color(0xFFEA4335),
                            padding: const EdgeInsets.symmetric(vertical: 12),
                            shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
                          ),
                          onPressed: () => _launchUrl(
                            context,
                            'mailto:kokalasaiteja@gmail.com?subject=Story%20Weave%20Inquiry',
                          ),
                        ),
                      ),
                    ],
                  ),
                ],
              ),
            ),
            const SizedBox(height: 30),
          ],
        ),
      ),
    );
  }

  Widget _buildFeatureRow(
      BuildContext context, IconData icon, String title, String subtitle) {
    final isDark = Theme.of(context).brightness == Brightness.dark;
    final primaryColor = Theme.of(context).primaryColor;

    return Padding(
      padding: const EdgeInsets.only(bottom: 12),
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Container(
            padding: const EdgeInsets.all(8),
            decoration: BoxDecoration(
              color: primaryColor.withValues(alpha: 0.12),
              borderRadius: BorderRadius.circular(8),
            ),
            child: Icon(icon, color: primaryColor, size: 18),
          ),
          const SizedBox(width: 12),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  title,
                  style: TextStyle(
                    color: isDark ? Colors.white : AppTheme.lightTextPrimary,
                    fontWeight: FontWeight.w600,
                    fontSize: 13,
                  ),
                ),
                Text(
                  subtitle,
                  style: TextStyle(
                    color: isDark ? AppTheme.darkTextSecondary : AppTheme.lightTextSecondary,
                    fontSize: 11,
                    height: 1.3,
                  ),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }
}
