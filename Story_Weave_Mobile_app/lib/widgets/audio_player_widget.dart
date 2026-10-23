import 'package:flutter/material.dart';
import 'package:audioplayers/audioplayers.dart';
import '../theme/app_theme.dart';

class AudioPlayerWidget extends StatefulWidget {
  final String? audioUrl;
  final VoidCallback? onSynthesizeRequested;
  final bool isSynthesizing;

  const AudioPlayerWidget({
    super.key,
    this.audioUrl,
    this.onSynthesizeRequested,
    this.isSynthesizing = false,
  });

  @override
  State<AudioPlayerWidget> createState() => _AudioPlayerWidgetState();
}

class _AudioPlayerWidgetState extends State<AudioPlayerWidget> {
  late AudioPlayer _player;
  PlayerState _state = PlayerState.stopped;
  Duration _duration = Duration.zero;
  Duration _position = Duration.zero;

  @override
  void initState() {
    super.initState();
    _player = AudioPlayer();

    _player.onPlayerStateChanged.listen((state) {
      if (mounted) setState(() => _state = state);
    });

    _player.onDurationChanged.listen((d) {
      if (mounted) setState(() => _duration = d);
    });

    _player.onPositionChanged.listen((p) {
      if (mounted) setState(() => _position = p);
    });

    _player.onPlayerComplete.listen((_) {
      if (mounted) {
        setState(() {
          _state = PlayerState.stopped;
          _position = Duration.zero;
        });
      }
    });
  }

  @override
  void didUpdateWidget(covariant AudioPlayerWidget oldWidget) {
    super.didUpdateWidget(oldWidget);
    if (widget.audioUrl != oldWidget.audioUrl) {
      _player.stop();
      setState(() {
        _state = PlayerState.stopped;
        _position = Duration.zero;
        _duration = Duration.zero;
      });
    }
  }

  @override
  void dispose() {
    _player.dispose();
    super.dispose();
  }

  Future<void> _togglePlay() async {
    if (widget.audioUrl == null || widget.audioUrl!.isEmpty) return;
    try {
      if (_state == PlayerState.playing) {
        await _player.pause();
      } else if (_state == PlayerState.paused) {
        await _player.resume();
      } else {
        await _player.play(UrlSource(widget.audioUrl!));
      }
    } catch (e) {
      debugPrint('Audio playback error: $e');
    }
  }

  String _formatDuration(Duration d) {
    final m = d.inMinutes.remainder(60).toString().padLeft(2, '0');
    final s = d.inSeconds.remainder(60).toString().padLeft(2, '0');
    return '$m:$s';
  }

  @override
  Widget build(BuildContext context) {
    final hasAudio = widget.audioUrl != null && widget.audioUrl!.isNotEmpty;

    if (!hasAudio) {
      return Container(
        padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
        decoration: BoxDecoration(
          color: const Color(0xFF0F1526),
          borderRadius: BorderRadius.circular(14),
          border: Border.all(color: AppTheme.borderGlow),
        ),
        child: Row(
          children: [
            const Icon(Icons.volume_up_outlined, color: AppTheme.primaryNeon, size: 22),
            const SizedBox(width: 12),
            const Expanded(
              child: Text(
                'Narration audio ready for synthesis',
                style: TextStyle(color: AppTheme.textSecondary, fontSize: 13),
              ),
            ),
            ElevatedButton.icon(
              onPressed: widget.isSynthesizing ? null : widget.onSynthesizeRequested,
              icon: widget.isSynthesizing
                  ? const SizedBox(
                      width: 14,
                      height: 14,
                      child: CircularProgressIndicator(strokeWidth: 2, color: Colors.black),
                    )
                  : const Icon(Icons.graphic_eq, size: 16, color: Colors.black),
              label: Text(
                widget.isSynthesizing ? 'Voicing...' : 'Read Aloud',
                style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 12, color: Colors.black),
              ),
              style: ElevatedButton.styleFrom(
                backgroundColor: AppTheme.primaryNeon,
                padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 8),
                shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(20)),
              ),
            ),
          ],
        ),
      );
    }

    final isPlaying = _state == PlayerState.playing;

    return Container(
      padding: const EdgeInsets.all(14),
      decoration: BoxDecoration(
        color: const Color(0xFF0F1526),
        borderRadius: BorderRadius.circular(16),
        border: Border.all(color: AppTheme.borderGlow),
      ),
      child: Column(
        children: [
          Row(
            children: [
              IconButton(
                onPressed: _togglePlay,
                icon: Icon(
                  isPlaying ? Icons.pause_circle_filled : Icons.play_circle_filled,
                  color: AppTheme.primaryNeon,
                  size: 40,
                ),
              ),
              const SizedBox(width: 8),
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    const Text(
                      'AI Voice Narration',
                      style: TextStyle(
                        color: AppTheme.textPrimary,
                        fontWeight: FontWeight.w600,
                        fontSize: 14,
                      ),
                    ),
                    const SizedBox(height: 2),
                    Text(
                      '${_formatDuration(_position)} / ${_formatDuration(_duration)}',
                      style: const TextStyle(
                        color: AppTheme.textSecondary,
                        fontSize: 12,
                      ),
                    ),
                  ],
                ),
              ),
              IconButton(
                onPressed: () => _player.stop(),
                icon: const Icon(Icons.stop_rounded, color: AppTheme.textSecondary, size: 24),
              ),
            ],
          ),
          SliderTheme(
            data: SliderTheme.of(context).copyWith(
              thumbShape: const RoundSliderThumbShape(enabledThumbRadius: 6),
              trackHeight: 3,
              activeTrackColor: AppTheme.primaryNeon,
              inactiveTrackColor: Colors.white12,
              thumbColor: AppTheme.primaryNeon,
            ),
            child: Slider(
              value: (_position.inMilliseconds /
                      (_duration.inMilliseconds > 0 ? _duration.inMilliseconds : 1))
                  .clamp(0.0, 1.0),
              onChanged: (val) {
                final targetMs = (_duration.inMilliseconds * val).round();
                _player.seek(Duration(milliseconds: targetMs));
              },
            ),
          ),
        ],
      ),
    );
  }
}
