import 'dart:convert';

class StoryModel {
  final String id;
  final String title;
  final String genre;
  final String concept;
  final String storyText;
  final String? visualPrompt;
  final String? imageUrl;
  final String? audioUrl;
  final DateTime createdAt;

  StoryModel({
    required this.id,
    required this.title,
    required this.genre,
    required this.concept,
    required this.storyText,
    this.visualPrompt,
    this.imageUrl,
    this.audioUrl,
    DateTime? createdAt,
  }) : createdAt = createdAt ?? DateTime.now();

  Map<String, dynamic> toMap() {
    return {
      'id': id,
      'title': title,
      'genre': genre,
      'concept': concept,
      'storyText': storyText,
      'visualPrompt': visualPrompt,
      'imageUrl': imageUrl,
      'audioUrl': audioUrl,
      'createdAt': createdAt.toIso8601String(),
    };
  }

  factory StoryModel.fromMap(Map<String, dynamic> map) {
    return StoryModel(
      id: map['id'] ?? DateTime.now().millisecondsSinceEpoch.toString(),
      title: map['title'] ?? 'Untitled Story',
      genre: map['genre'] ?? 'Science',
      concept: map['concept'] ?? '',
      storyText: map['story'] ?? map['storyText'] ?? '',
      visualPrompt: map['visual_prompt'] ?? map['visualPrompt'],
      imageUrl: map['image_url'] ?? map['imageUrl'],
      audioUrl: map['audio_url'] ?? map['audioUrl'],
      createdAt: map['createdAt'] != null
          ? DateTime.tryParse(map['createdAt']) ?? DateTime.now()
          : DateTime.now(),
    );
  }

  String toJson() => json.encode(toMap());

  factory StoryModel.fromJson(String source) =>
      StoryModel.fromMap(json.decode(source));

  StoryModel copyWith({
    String? id,
    String? title,
    String? genre,
    String? concept,
    String? storyText,
    String? visualPrompt,
    String? imageUrl,
    String? audioUrl,
    DateTime? createdAt,
  }) {
    return StoryModel(
      id: id ?? this.id,
      title: title ?? this.title,
      genre: genre ?? this.genre,
      concept: concept ?? this.concept,
      storyText: storyText ?? this.storyText,
      visualPrompt: visualPrompt ?? this.visualPrompt,
      imageUrl: imageUrl ?? this.imageUrl,
      audioUrl: audioUrl ?? this.audioUrl,
      createdAt: createdAt ?? this.createdAt,
    );
  }
}
