# SoundTracker

![version](https://img.shields.io/badge/version-0.3.2-blue)

SoundTracker is an application for tracking and analyzing sounds you make throughout the day. It runs in the background, records noise levels, uses AI for sound identification, and provides charts and filters for your data.

## Project Management
- See `PLANNING.md` for high-level vision and architecture
- See `TASK.md` for current tasks and backlog
- See `TODO.md` for feature requests and changes
- See `CHANGES.md` for version history

## Getting Started

### Quick Start Scripts

> **Added in v0.3.2**

You can use the following scripts to start and stop the backend (FastAPI) and frontend (Flutter) together:

#### Windows
- **Start:** `run_soundTracker.bat`
- **Stop:** `stop_soundTracker.bat`

#### Linux/macOS (Bash)
- **Start:** `./run_soundTracker.sh`
- **Stop:** `./stop_soundTracker.sh`

> Make sure to `chmod +x *.sh` on Unix systems before running.

**What these scripts do:**
- Start: Launches the backend (with venv) and frontend (Flutter desktop) in separate terminals/processes.
- Stop: Kills backend and frontend processes (by port or process name), then checks that ports are freed up (8000 for backend, 50300+ for Flutter).

**Troubleshooting:**
- If a port is still in use after stopping, you may need to manually kill the process or restart your system.
- On Windows, ensure you have the necessary permissions to kill processes.
- On Linux/macOS, `lsof` is required for port checks.

## Tech Stack
- Backend: Python (FastAPI, SQLAlchemy/SQLModel, pydantic, pytest)
- Frontend: Flutter
- Database: SQLite
- Deployment: GitHub Actions
- Platform: Linux, Raspberry Pi, WSL, Android, iOS

## Backend Setup

### AI Sound Identification Endpoint

- **POST /ai/identify**
  - Accepts: WAV file upload (form field: `file`)
  - Returns: `{ "label": "Speech" }` (real label from YAMNet model)
  - Example (with curl):
    ```sh
    curl -F "file=@path/to/audio.wav" http://localhost:8000/ai/identify
    ```
  - Only WAV files are supported for now.

#### How it works
- Uses Google’s [YAMNet](https://tfhub.dev/google/yamnet/1) model via TensorFlow Hub for real sound classification (521 classes).
- Audio is preprocessed (mono, 16kHz) and passed to the model.
- The top predicted class label is returned.

#### Dependencies
- `tensorflow`, `tensorflow-hub`, `librosa`, `soundfile`, `python-multipart` (see requirements.txt)


1. Open a terminal in the `backend` directory.
2. Create a Python virtual environment:
   - Windows: `python -m venv venv`
   - Linux/Mac/WSL: `python3 -m venv venv`
3. Activate the virtual environment:
   - Windows: `./venv/Scripts/Activate`
   - Linux/Mac/WSL: `source venv/bin/activate`
4. Install dependencies:
   - `pip install -r requirements.txt`
5. Copy `.env.sample` to `.env` and adjust as needed (never commit secrets).
6. Run the backend:
   - Windows: `run_backend.bat`
   - Linux/Mac/WSL: `bash run_backend.sh`

## Running Tests

From the project root:
```
pytest backend/tests
```

All new features must have unit tests in `/backend/tests`.

## Project Management
- See `PLANNING.md` for high-level vision and architecture
- See `TASK.md` for current tasks and backlog
- See `TODO.md` for feature requests and changes
- See `CHANGES.md` for version history

## Contributing
- Keep files under 500 lines, split into modules as needed
- Write unit tests for all new features
- Follow PEP8 and use type hints
- Update documentation and PM files with every change
