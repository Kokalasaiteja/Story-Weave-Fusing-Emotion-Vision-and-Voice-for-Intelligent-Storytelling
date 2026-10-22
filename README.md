# 📖 Story Weave — Fusing Emotion, Vision & Voice for Intelligent Storytelling

[![Live Demo](https://img.shields.io/badge/Live_Demo-Story_Weave_Streamlit-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white)](https://ai-story-generator-with-image.streamlit.app/)
[![Flutter](https://img.shields.io/badge/Flutter-3.44.8-02569B?style=for-the-badge&logo=flutter&logoColor=white)](https://flutter.dev)
[![Python](https://img.shields.io/badge/Python-3.13-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![Android](https://img.shields.io/badge/Android-API_24+-3DDC84?style=for-the-badge&logo=android&logoColor=white)](https://developer.android.com)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg?style=for-the-badge)](https://github.com/Kokalasaiteja/Story-Weave-Fusing-Emotion-Vision-and-Voice-for-Intelligent-Storytelling/blob/main/LICENSE)

**Story Weave** is an AI-powered multimodal storytelling application that fuses text, visuals, and voice to create engaging stories in a few clicks. Users can provide a story title, genre, and concept, and the app generates a structured narrative, a cinematic illustration, and an immersive voice narration.

Story Weave is architected as an **enterprise monorepo** featuring both a responsive **Streamlit Web Application** and a high-performance **Flutter Android Native Mobile Application**.

---

## 🚀 Live Demo & APK Downloads

- 🌐 **Web Live App**: Try the app live here: [Story Weave Live](https://ai-story-weave.streamlit.app/)
- 📱 **Mobile Android APKs**: Download pre-compiled standalone release APKs directly from the repository:

| Build Target | Architecture | File Size | Recommended Device | Direct File Link |
|:---|:---|:---:|:---|:---|
| **ARM64 (Modern)** | `arm64-v8a` | **35.6 MB** | Modern 64-bit Android smartphones & tablets | [Download ARM64 APK](Story_Weave_Web/media/app-arm64-v8a-release.apk) |
| **ARMv7a (32-bit)** | `armeabi-v7a` | **33.1 MB** | Legacy & budget 32-bit Android devices | [Download ARMv7a APK](Story_Weave_Web/media/app-armeabi-v7a-release.apk) |
| **x86_64 (Emulators)** | `x86_64` | **37.1 MB** | Android Studio Emulators & ChromeOS | [Download x86_64 APK](Story_Weave_Web/media/app-x86_64-release.apk) |
| **Universal Fat APK** | All ABIs | **70.5 MB** | Universal all-in-one distribution installer | [Download Universal APK](Story_Weave_Web/media/app-release.apk) |

---

## 🌟 Features

### 🧠 Core Multimodal Storytelling
- **Story Generation**: AI-generated stories structured in three distinct sections: **Introduction**, **Story**, and **Conclusion** (kept under 500 words for optimal pacing).
- **Image Generation**: High-fidelity cinematic illustrations extracted dynamically from the story's visual prompt using Pollinations AI.
- **Audio Narration**: Natural text-to-speech (TTS) conversion using gTTS for immersive listening, with instant playback and `.mp3` download.
- **Multi-Genre Support**: Science, Fantasy, Education, Mythology, Sci-Fi, and Drama with contextual storytelling styles.

### 💻 Web Platform (`Story_Weave_Web`)
- **Interactive UI**: Clean Streamlit interface with session state management for a seamless single-page application experience.
- **Custom Vector Day/Night Switch**: Vector-coded theme toggle switch (Golden Sun + Clouds in Day mode, Cratered Moon + Stars in Night mode) with 60fps micro-animations.
- **Persistent JSON Story Library**: All generated stories are saved in `data/saved_stories.json`, persisting across page reloads and browser sessions.
- **Batch Story Management**: Select All / Deselect All controls, multi-item batch deletion, keyword search, and genre filtering.
- **Direct APK Distribution Portal**: Integrated download buttons for all Android release APK architectures.

### 📱 Companion Mobile App (`Story_Weave_Mobile_app`)
- **Native Flutter 3.44+ Performance**: Fluid 60fps Material 3 experience with liquid-glass aesthetic and responsive touch controls.
- **Vector-Animated `DayNightSwitch`**: Custom-painted physics toggle switch matching Mikhail Gribkov's iconic Day/Night switch.
- **Embedded Audio Player**: Scrubbable audio progress bar, playback timer, play/pause controls, and background streaming.
- **Interactive Visual Gallery**: Full-screen image preview with pinch-to-zoom, pan, and system share sheet integration.
- **Adaptive Launcher Icons**: Safe-zone optimized adaptive launcher icons (`108dp` safe-zone geometry) that render clearly on all Android launchers.

---

## 🏛️ Monorepo Architecture

The repository is organized into a clean dual-directory structure separating web and mobile codebases:

```
Story-Weave-Fusing-Emotion-Vision-and-Voice-for-Intelligent-Storytelling-main/
├── README.md                          # Master project documentation
├── .gitignore                         # Universal ignore for Python, Flutter & Gradle
├── Story_Weave_Web/                   # 🌐 Production Web Application
│   ├── app.py                         # Streamlit web interface with multimodal engine
│   ├── requirements.txt               # Web Python dependencies
│   ├── data/                          # Persistent JSON storage
│   │   └── saved_stories.json         # Saved stories database
│   ├── media/                         # Compiled standalone release APKs
│   │   ├── app-arm64-v8a-release.apk
│   │   ├── app-armeabi-v7a-release.apk
│   │   ├── app-x86_64-release.apk
│   │   └── app-release.apk
│   ├── static/                        # Icons, logos, and vector assets
│   └── screenshots/                   # Web walkthrough screenshots
└── Story_Weave_Mobile_app/            # 📱 Production Native Flutter Mobile App
    ├── pubspec.yaml                   # Flutter dependencies & launcher icon config
    ├── android/                       # Native Android configuration (Manifest, Gradle, Mipmaps)
    ├── assets/                        # App icons, splash artwork, and presets
    ├── lib/                           # Flutter Dart source code
    │   ├── main.dart                  # Application entry point
    │   ├── models/                    # StoryModel & data contracts
    │   ├── screens/                   # HomeScreen, HistoryScreen, MotiveScreen
    │   ├── services/                  # StorageService, ApiService, AudioService
    │   ├── theme/                     # AppTheme & color palettes
    │   └── widgets/                   # DayNightSwitch, AudioPlayerWidget, CustomDrawer
    └── build/                         # Gradle build outputs & APK releases
```

---

## 🛠️ Technology Stack

| Component | Technology | Description |
|:---|:---|:---|
| **Web Frontend & UI** | [Streamlit](https://streamlit.io) 1.35+ | Dynamic web dashboard with custom CSS glassmorphism |
| **Mobile Frontend** | [Flutter](https://flutter.dev) 3.44+ / [Dart](https://dart.dev) 3.12+ | Cross-platform native Android client with Material 3 |
| **Story Generation** | [Google Gemini 2.5 Generative AI](https://ai.google.dev/) | Multimodal LLM for creative, emotionally resonant stories |
| **Image Generation** | [Pollinations AI](https://pollinations.ai) | Stable Diffusion-based cinematic 8k illustration engine |
| **Audio Generation** | [gTTS (Google Text-to-Speech)](https://pypi.org/project/gTTS/) | Natural voice narration synthesis |
| **Image Processing** | [PIL (Pillow)](https://python-pillow.org/) | Python Imaging Library for visual asset processing |
| **HTTP Requests** | [Requests](https://requests.readthedocs.io/) / [http](https://pub.dev/packages/http) | Network communication and API calls |
| **Local Persistence** | JSON Storage / [shared_preferences](https://pub.dev/packages/shared_preferences) | Client-side persistent story library across sessions |

---

## 📦 Installation & Usage

### 1. Clone the Repository

```bash
git clone https://github.com/Kokalasaiteja/Story-Weave-Fusing-Emotion-Vision-and-Voice-for-Intelligent-Storytelling.git
cd Story-Weave-Fusing-Emotion-Vision-and-Voice-for-Intelligent-Storytelling-main
```

---

### 2. Run the Web Application (`Story_Weave_Web`)

#### A. Install Dependencies
```bash
cd Story_Weave_Web

# Optional: Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

pip install -r requirements.txt
```

#### B. Set Your Secrets (Optional Gemini API Key)
Add your Gemini API key in `.streamlit/secrets.toml` or Streamlit Cloud Secrets:

```toml
[general]
GEMINI_API_KEY = "your_gemini_api_key_here"
HF_API_KEY = "your_huggingface_api_key_here"
```

> [!NOTE]
> *Never hardcode API keys in your code. Use Streamlit secrets or environment variables.*  
> If no API key is provided, Story Weave runs in a built-in **Creative Fallback Mode** so you can test all features immediately without any setup.

#### C. Run the Web App Locally
```bash
streamlit run app.py
```

Open your browser at **`http://localhost:8501`** and enjoy storytelling!

---

### 3. Run the Mobile Companion App (`Story_Weave_Mobile_app`)

#### A. Install Flutter Dependencies
```bash
cd Story_Weave_Mobile_app
flutter pub get
```

#### B. Run on Emulator or Connected Device
```bash
flutter run
```

#### C. Build Android Release APKs
```bash
# Build architecture-specific APKs:
flutter build apk --split-per-abi

# Build universal all-in-one APK:
flutter build apk
```

Compiled APKs will be output to `Story_Weave_Mobile_app/build/app/outputs/flutter-apk/`.

---

## 📝 Usage Guide

1. **Enter Story Title**: Type your title or click a Quick Preset (e.g., *RBC & WBC* or *Clockwork Forest*).
2. **Select Genre**: Choose a genre from the dropdown (*Science, Fantasy, Education, Mythology, Sci-Fi, Drama*).
3. **Write Story Description / Concept**: Provide a brief concept or learning prompt.
4. **Click ✨ Generate Story Weave**: The AI will craft the story, extract a visual prompt, generate a cinematic illustration, and synthesize voice narration.
5. **View Narrative & Art**: Read through the structured Introduction, Story, and Conclusion with accompanying artwork.
6. **Listen & Download**: Click **🔊 Read Aloud Story** or use the integrated audio player to listen or download the `.mp3` narration.
7. **Browse 📚 Story Library**: View saved stories, search by keyword, filter by genre, and batch-delete stories with a single click.

---

## ⚡ Future Enhancements

- 🎙️ **Customizable Voice Options**: Multiple voice personas, accents, pitch, and speed adjustments for voice narration.
- 🎨 **Multiple Illustration Styles**: Art style presets including cartoon, watercolor, comic book, anime, and cinematic 3D.
- 🌐 **Multi-Language Support**: Narrative generation and voice synthesis across Spanish, French, German, Hindi, Telugu, and Japanese.
- ☁️ **Cloud Gallery Sync**: Personal user accounts and cloud synchronization for stories, bookmarks, and illustrations.

---

## 🧑‍💻 Developer

**Developed by Kokala Sai Teja**  
- 📧 **Email**: [kokalasaiteja@gmail.com](mailto:kokalasaiteja@gmail.com?subject=Story%20Weave%20Inquiry)  
- 💼 **LinkedIn**: [linkedin.com/in/sai-teja-kokala-245a12299](https://www.linkedin.com/in/sai-teja-kokala-245a12299?utm_source=share_via&utm_content=profile&utm_medium=member_android)  
- 🐙 **GitHub**: [github.com/Kokalasaiteja](https://github.com/Kokalasaiteja)

---

## 📜 License

This project is licensed under the MIT License. See the [LICENSE](https://github.com/Kokalasaiteja/Story-Weave-Fusing-Emotion-Vision-and-Voice-for-Intelligent-Storytelling/blob/main/LICENSE) file for details.
