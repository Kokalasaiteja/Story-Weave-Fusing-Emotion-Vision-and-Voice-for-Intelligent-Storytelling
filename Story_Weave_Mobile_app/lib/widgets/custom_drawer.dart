import 'package:flutter/material.dart';
import '../theme/app_theme.dart';
import 'day_night_switch.dart';

class CustomDrawer extends StatelessWidget {
  final String activeRoute;
  final Function(String route) onNavigate;
  final bool isDarkMode;
  final VoidCallback onToggleTheme;

  const CustomDrawer({
    super.key,
    required this.activeRoute,
    required this.onNavigate,
    required this.isDarkMode,
    required this.onToggleTheme,
  });

  Widget _buildNavItem({
    required BuildContext context,
    required IconData icon,
    required String title,
    required String route,
  }) {
    final isActive = activeRoute == route;
    final primaryColor = Theme.of(context).primaryColor;
    final isDark = Theme.of(context).brightness == Brightness.dark;

    return Container(
      margin: const EdgeInsets.symmetric(horizontal: 12, vertical: 4),
      decoration: BoxDecoration(
        color: isActive
            ? primaryColor.withValues(alpha: 0.12)
            : Colors.transparent,
        borderRadius: BorderRadius.circular(12),
        border: isActive
            ? Border.all(color: primaryColor.withValues(alpha: 0.4), width: 1)
            : null,
      ),
      child: ListTile(
        leading: Icon(
          icon,
          color: isActive
              ? primaryColor
              : (isDark ? AppTheme.darkTextSecondary : AppTheme.lightTextSecondary),
          size: 22,
        ),
        title: Text(
          title,
          style: TextStyle(
            color: isActive
                ? primaryColor
                : (isDark ? AppTheme.darkTextPrimary : AppTheme.lightTextPrimary),
            fontWeight: isActive ? FontWeight.w700 : FontWeight.w500,
            fontSize: 14,
          ),
        ),
        trailing: isActive
            ? Container(
                width: 6,
                height: 6,
                decoration: BoxDecoration(
                  color: primaryColor,
                  shape: BoxShape.circle,
                ),
              )
            : null,
        onTap: () => onNavigate(route),
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    final isDark = Theme.of(context).brightness == Brightness.dark;
    final primaryColor = Theme.of(context).primaryColor;

    return Drawer(
      backgroundColor: isDark ? const Color(0xFF0A0E1A) : Colors.white,
      child: Column(
        children: [
          // Header
          Container(
            padding: const EdgeInsets.fromLTRB(20, 50, 20, 24),
            decoration: BoxDecoration(
              gradient: LinearGradient(
                colors: isDark
                    ? [const Color(0xFF141C33), const Color(0xFF0A0E1A)]
                    : [const Color(0xFFF1F5F9), Colors.white],
                begin: Alignment.topCenter,
                end: Alignment.bottomCenter,
              ),
              border: Border(
                bottom: BorderSide(
                  color: isDark ? const Color(0x2200E5FF) : const Color(0x1A000000),
                ),
              ),
            ),
            child: Row(
              children: [
                Container(
                  width: 52,
                  height: 52,
                  decoration: BoxDecoration(
                    shape: BoxShape.circle,
                    boxShadow: [
                      BoxShadow(
                        color: primaryColor.withValues(alpha: 0.3),
                        blurRadius: 12,
                      ),
                    ],
                  ),
                  child: ClipOval(
                    child: Image.asset(
                      'assets/icon/app_icon.png',
                      fit: BoxFit.cover,
                      errorBuilder: (_, __, ___) => Icon(
                        Icons.auto_stories,
                        color: primaryColor,
                        size: 32,
                      ),
                    ),
                  ),
                ),
                const SizedBox(width: 14),
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      ShaderMask(
                        shaderCallback: (bounds) => (isDark
                                ? AppTheme.brandGradient
                                : AppTheme.lightBrandGradient)
                            .createShader(bounds),
                        child: const Text(
                          'Story Weave',
                          style: TextStyle(
                            color: Colors.white,
                            fontSize: 19,
                            fontWeight: FontWeight.w800,
                            letterSpacing: 0.5,
                          ),
                        ),
                      ),
                      const SizedBox(height: 2),
                      Text(
                        'Multimodal AI Companion',
                        style: TextStyle(
                          color: isDark
                              ? AppTheme.darkTextSecondary
                              : AppTheme.lightTextSecondary,
                          fontSize: 11,
                        ),
                      ),
                    ],
                  ),
                ),
              ],
            ),
          ),

          const SizedBox(height: 12),

          // Nav Items
          _buildNavItem(
            context: context,
            icon: Icons.auto_awesome,
            title: '✨ Story Creator',
            route: 'home',
          ),
          _buildNavItem(
            context: context,
            icon: Icons.menu_book_rounded,
            title: '📚 Story Library',
            route: 'history',
          ),
          _buildNavItem(
            context: context,
            icon: Icons.star_rounded,
            title: '🌟 Motive & Vision',
            route: 'about',
          ),

          const Divider(height: 24, thickness: 1),

          // Theme Mode Switcher Tile
          Container(
            margin: const EdgeInsets.symmetric(horizontal: 12),
            decoration: BoxDecoration(
              color: isDark ? const Color(0xFF141C33) : const Color(0xFFF1F5F9),
              borderRadius: BorderRadius.circular(12),
            ),
            child: ListTile(
              leading: Icon(
                isDark ? Icons.dark_mode_rounded : Icons.light_mode_rounded,
                color: isDark ? AppTheme.primaryNeon : AppTheme.lightPrimary,
              ),
              title: Text(
                isDark ? 'Dark Mode' : 'Light Mode',
                style: TextStyle(
                  fontSize: 14,
                  fontWeight: FontWeight.w600,
                  color: isDark ? AppTheme.darkTextPrimary : AppTheme.lightTextPrimary,
                ),
              ),
              trailing: DayNightSwitch(
                isDarkMode: isDark,
                onToggle: (_) => onToggleTheme(),
                width: 58,
                height: 30,
              ),
            ),
          ),

          const Spacer(),

          // Fixed 2-Line Footer with Zero Extra Space Below
          SafeArea(
            top: false,
            child: Container(
              width: double.infinity,
              padding: const EdgeInsets.fromLTRB(16, 12, 16, 4),
              decoration: BoxDecoration(
                border: Border(
                  top: BorderSide(
                    color: isDark ? const Color(0x1AFFFFFF) : const Color(0x1A000000),
                  ),
                ),
              ),
              child: Column(
                mainAxisSize: MainAxisSize.min,
                children: [
                  Text(
                    'Story Weave v1.0.0',
                    textAlign: TextAlign.center,
                    style: TextStyle(
                      color: isDark ? AppTheme.darkTextPrimary : AppTheme.lightTextPrimary,
                      fontWeight: FontWeight.w700,
                      fontSize: 12,
                      letterSpacing: 0.3,
                    ),
                  ),
                  const SizedBox(height: 2),
                  Text(
                    'Developed by Kokala Sai Teja',
                    textAlign: TextAlign.center,
                    style: TextStyle(
                      color: (isDark ? AppTheme.darkTextSecondary : AppTheme.lightTextSecondary)
                          .withValues(alpha: 0.8),
                      fontWeight: FontWeight.w500,
                      fontSize: 11,
                    ),
                  ),
                ],
              ),
            ),
          ),
        ],
      ),
    );
  }
}
