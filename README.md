# SoundTracker

![version](https://img.shields.io/badge/version-0.4.0-blue)

SoundTracker is an application for tracking and analyzing sounds you make throughout the day. It runs in the background, records noise levels, uses AI for sound identification, and provides charts and filters for your data.

## Project Management
- See `PLANNING.md` for high-level vision and architecture
- See `TASK.md` for current tasks and backlog
- See `TODO.md` for feature requests and changes
- See `CHANGES.md` for version history

## Tech Stack
- Backend: Python (FastAPI, SQLAlchemy/SQLModel, pydantic, pytest)
- Frontend: Flutter
- Database: SQLite
- Deployment: GitHub Actions
- Platform: Linux, Raspberry Pi, WSL, Android, iOS

## Backend Setup

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

## API Documentation

### Audio Capture Endpoints

#### GET /audio/status
Get the current status of the audio capture.

**Response:**
```json
{
  "is_running": true,
  "sample_rate": 44100,
  "channels": 1,
  "active_connections": 1
}
```

#### GET /audio/level
Get the current noise level in dBFS.

**Response:**
```json
{
  "level_db": -12.34
}
```

### WebSocket Endpoint

#### /audio/ws
WebSocket endpoint for real-time audio level updates.

**Example Client (JavaScript):**
```javascript
const socket = new WebSocket('ws://localhost:8000/audio/ws');

socket.onmessage = (event) => {
  const data = JSON.parse(event.data);
  console.log('Noise level:', data.db, 'dBFS');
  console.log('RMS:', data.rms);
  console.log('Timestamp:', data.timestamp);
};
```

**WebSocket Message Format:**
```json
{
  "timestamp": "2023-01-01T12:00:00.000000",
  "rms": 0.123,
  "db": -18.23,
  "sample_rate": 44100
}
```

## Configuration

Edit the `.env` file to configure audio capture settings:

```ini
# Audio capture settings
AUDIO_SAMPLE_RATE=44100  # Sample rate in Hz
AUDIO_CHANNELS=1         # Number of audio channels (1=mono, 2=stereo)
AUDIO_BLOCK_SIZE=1024    # Samples per block

# WebSocket settings
WEBSOCKET_UPDATE_INTERVAL=0.1  # Update interval in seconds

# Database settings
DATABASE_URL=sqlite:///./soundtracker.db
```

## Running Tests

From the project root:
```
pytest backend/tests
```

All new features must have unit tests in `/backend/tests`.

## Contributing

- Keep files under 500 lines, split into modules as needed
- Write unit tests for all new features
- Follow PEP8 and use type hints
- Update documentation and PM files with every change
   