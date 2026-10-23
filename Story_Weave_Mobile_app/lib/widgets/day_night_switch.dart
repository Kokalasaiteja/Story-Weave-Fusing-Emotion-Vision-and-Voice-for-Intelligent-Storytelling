import 'package:flutter/material.dart';

/// A custom-coded, vector-animated Day / Night mode toggle switch
/// matching Mikhail Gribkov's iconic Day/Night mode switcher.
/// In Light/Day mode: Sky blue capsule, glowing Sun with concentric rings, and fluffy clouds.
/// In Dark/Night mode: Deep cosmic navy capsule, silvery cratered Moon, and twinkling stars.
class DayNightSwitch extends StatefulWidget {
  final bool isDarkMode;
  final ValueChanged<bool> onToggle;
  final double width;
  final double height;

  const DayNightSwitch({
    super.key,
    required this.isDarkMode,
    required this.onToggle,
    this.width = 68.0,
    this.height = 36.0,
  });

  @override
  State<DayNightSwitch> createState() => _DayNightSwitchState();
}

class _DayNightSwitchState extends State<DayNightSwitch>
    with SingleTickerProviderStateMixin {
  late AnimationController _controller;
  late Animation<double> _animation;

  @override
  void initState() {
    super.initState();
    _controller = AnimationController(
      vsync: this,
      duration: const Duration(milliseconds: 400),
      value: widget.isDarkMode ? 1.0 : 0.0,
    );
    _animation = CurvedAnimation(
      parent: _controller,
      curve: Curves.easeInOutCubic,
    );
  }

  @override
  void didUpdateWidget(DayNightSwitch oldWidget) {
    super.didUpdateWidget(oldWidget);
    if (widget.isDarkMode != oldWidget.isDarkMode) {
      if (widget.isDarkMode) {
        _controller.forward();
      } else {
        _controller.reverse();
      }
    }
  }

  @override
  void dispose() {
    _controller.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return GestureDetector(
      onTap: () => widget.onToggle(!widget.isDarkMode),
      child: AnimatedBuilder(
        animation: _animation,
        builder: (context, _) {
          return CustomPaint(
            size: Size(widget.width, widget.height),
            painter: _DayNightPainter(t: _animation.value),
          );
        },
      ),
    );
  }
}

class _DayNightPainter extends CustomPainter {
  final double t; // 0.0 = Day (Sun on right), 1.0 = Night (Moon on left)

  _DayNightPainter({required this.t});

  @override
  void paint(Canvas canvas, Size size) {
    final rect = Offset.zero & size;
    final rrect = RRect.fromRectAndRadius(
      rect,
      Radius.circular(size.height / 2),
    );

    canvas.save();
    canvas.clipRRect(rrect);

    // 1. Capsule Background Gradient (Sky Blue in Day -> Midnight Navy in Night)
    final dayTopColor = const Color(0xFF42B3F0);
    final dayBottomColor = const Color(0xFF76CEFB);
    final nightTopColor = const Color(0xFF1B2338);
    final nightBottomColor = const Color(0xFF0F1424);

    final bgPaint = Paint()
      ..shader = LinearGradient(
        begin: Alignment.topLeft,
        end: Alignment.bottomRight,
        colors: [
          Color.lerp(dayTopColor, nightTopColor, t)!,
          Color.lerp(dayBottomColor, nightBottomColor, t)!,
        ],
      ).createShader(rect);

    canvas.drawRRect(rrect, bgPaint);

    // 2. Stars (Visible in Night, t -> 1)
    if (t > 0.05) {
      final starOpacity = ((t - 0.2) / 0.8).clamp(0.0, 1.0);
      final starPaint = Paint()..color = Colors.white.withValues(alpha: starOpacity * 0.95);
      final smallStarPaint = Paint()..color = const Color(0xFFFFE599).withValues(alpha: starOpacity * 0.85);

      // Star positions on the right side of the switch
      final rightCenter = size.width * 0.65;
      _draw4PointStar(canvas, Offset(rightCenter + 4, size.height * 0.30), 3.2, starPaint);
      _draw4PointStar(canvas, Offset(rightCenter + 14, size.height * 0.65), 2.4, starPaint);
      _draw4PointStar(canvas, Offset(rightCenter - 8, size.height * 0.70), 2.0, smallStarPaint);

      // Tiny twinkle dots
      canvas.drawCircle(Offset(rightCenter + 12, size.height * 0.25), 1.0, starPaint);
      canvas.drawCircle(Offset(rightCenter - 4, size.height * 0.40), 1.1, starPaint);
      canvas.drawCircle(Offset(rightCenter + 3, size.height * 0.80), 0.9, starPaint);
    }

    // 3. Clouds (Visible in Day, t -> 0)
    if (t < 0.95) {
      final dayProgress = (1.0 - t).clamp(0.0, 1.0);
      final cloudOpacity = ((dayProgress - 0.15) / 0.85).clamp(0.0, 1.0);
      final cloudYOffset = t * 14.0; // Clouds sink down when night arrives

      // Back puffy cloud
      final backCloudPaint = Paint()..color = Colors.white.withValues(alpha: cloudOpacity * 0.4);
      canvas.drawCircle(Offset(size.width * 0.22, size.height * 0.72 + cloudYOffset), 12, backCloudPaint);
      canvas.drawCircle(Offset(size.width * 0.36, size.height * 0.78 + cloudYOffset), 10, backCloudPaint);

      // Front puffy cloud
      final frontCloudPaint = Paint()..color = Colors.white.withValues(alpha: cloudOpacity * 0.9);
      canvas.drawCircle(Offset(size.width * 0.14, size.height * 0.82 + cloudYOffset), 10, frontCloudPaint);
      canvas.drawCircle(Offset(size.width * 0.28, size.height * 0.76 + cloudYOffset), 13, frontCloudPaint);
      canvas.drawCircle(Offset(size.width * 0.42, size.height * 0.86 + cloudYOffset), 9, frontCloudPaint);
    }

    // 4. Knob Position
    // Night: Knob on left (t = 1)
    // Day: Knob on right (t = 0)
    final knobRadius = (size.height - 8) / 2;
    final minX = 4 + knobRadius;
    final maxX = size.width - 4 - knobRadius;
    final knobX = maxX - t * (maxX - minX);
    final knobCenter = Offset(knobX, size.height / 2);

    // 5. Sun Rays / Concentric Halo Rings (Day mode only)
    if (t < 0.9) {
      final sunDayFactor = (1.0 - t).clamp(0.0, 1.0);
      final haloPaint1 = Paint()
        ..color = const Color(0x24FFFFFF).withValues(alpha: sunDayFactor * 0.18)
        ..style = PaintingStyle.fill;
      final haloPaint2 = Paint()
        ..color = const Color(0x18FFFFFF).withValues(alpha: sunDayFactor * 0.12)
        ..style = PaintingStyle.fill;

      canvas.drawCircle(knobCenter, knobRadius * 1.55, haloPaint2);
      canvas.drawCircle(knobCenter, knobRadius * 1.25, haloPaint1);
    }

    // 6. Knob Drop Shadow
    final shadowPaint = Paint()
      ..color = Colors.black.withValues(alpha: 0.25)
      ..maskFilter = const MaskFilter.blur(BlurStyle.normal, 3.5);
    canvas.drawCircle(knobCenter.translate(0, 1.5), knobRadius, shadowPaint);

    // 7. Knob Sphere (Sun Golden Yellow -> Moon Silvery Lunar White)
    final sunColorTop = const Color(0xFFFFD56B);
    final sunColorBottom = const Color(0xFFFFA200);
    final moonColorTop = const Color(0xFFF1F5F9);
    final moonColorBottom = const Color(0xFFCBD5E1);

    final knobPaint = Paint()
      ..shader = LinearGradient(
        begin: Alignment.topLeft,
        end: Alignment.bottomRight,
        colors: [
          Color.lerp(sunColorTop, moonColorTop, t)!,
          Color.lerp(sunColorBottom, moonColorBottom, t)!,
        ],
      ).createShader(Rect.fromCircle(center: knobCenter, radius: knobRadius));

    canvas.drawCircle(knobCenter, knobRadius, knobPaint);

    // 8. Moon Craters (Fade in with t -> 1)
    if (t > 0.1) {
      final craterOpacity = ((t - 0.2) / 0.8).clamp(0.0, 1.0);
      final craterPaint = Paint()
        ..color = const Color(0xFF94A3B8).withValues(alpha: craterOpacity * 0.45)
        ..style = PaintingStyle.fill;

      // 3 subtle round craters
      canvas.drawCircle(knobCenter + const Offset(-3.5, -3.0), knobRadius * 0.22, craterPaint);
      canvas.drawCircle(knobCenter + const Offset(2.5, 2.5), knobRadius * 0.28, craterPaint);
      canvas.drawCircle(knobCenter + const Offset(-2.0, 4.0), knobRadius * 0.16, craterPaint);
    }

    // 9. Capsule Outer Border
    final borderDay = const Color(0x66FFFFFF);
    final borderNight = const Color(0x3300E5FF);
    final borderPaint = Paint()
      ..style = PaintingStyle.stroke
      ..strokeWidth = 1.4
      ..color = Color.lerp(borderDay, borderNight, t)!;

    canvas.drawRRect(rrect, borderPaint);

    canvas.restore();
  }

  void _draw4PointStar(Canvas canvas, Offset center, double radius, Paint paint) {
    final path = Path();
    path.moveTo(center.dx, center.dy - radius);
    path.quadraticBezierTo(center.dx, center.dy, center.dx + radius, center.dy);
    path.quadraticBezierTo(center.dx, center.dy, center.dx, center.dy + radius);
    path.quadraticBezierTo(center.dx, center.dy, center.dx - radius, center.dy);
    path.quadraticBezierTo(center.dx, center.dy, center.dx, center.dy - radius);
    path.close();
    canvas.drawPath(path, paint);
  }

  @override
  bool shouldRepaint(_DayNightPainter oldDelegate) => oldDelegate.t != t;
}
