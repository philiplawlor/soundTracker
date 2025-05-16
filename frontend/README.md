# SoundTracker Frontend

![version](https://img.shields.io/badge/version-0.1.0-blue)

A cross-platform Flutter app for sound classification using your FastAPI backend AI.

## Features
- Pick and play WAV audio files
- Send audio to backend `/ai/identify` endpoint
- Displays predicted sound label (YAMNet)
- Runs on Windows, macOS, Linux, Android, iOS, and web

## Requirements
- Flutter 3.x (with desktop, web, and mobile enabled)
- Backend running at `http://localhost:8000` (see project root README)

## Getting Started

1. Install dependencies:
   ```sh
   flutter pub get
   ```
2. Run the app:
   - **Desktop:**
     ```sh
     flutter run -d windows   # or -d macos, -d linux
     ```
   - **Web:**
     ```sh
     flutter run -d chrome
     ```
   - **Android/iOS:**
     ```sh
     flutter run -d android  # or -d ios (on macOS)
     ```

## Usage
1. Pick a WAV file from your device.
2. Play the audio to verify.
3. Press "Identify Sound" to send to backend and display the AI label.

## Dependencies
- `http`, `file_picker`, `audioplayers`, `flutter_launcher_icons`

---

For more info, see the main project README.
