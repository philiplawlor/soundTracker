# SoundTracker

![version](https://img.shields.io/badge/version-0.5.0-blue)

SoundTracker is an application for tracking and analyzing sounds in your environment. It captures audio, identifies sounds using AI, and provides visualization and analysis tools.

## Project Management
- See `PLANNING.md` for high-level vision and architecture
- See `TASK.md` for current tasks and backlog
- See `TODO.md` for feature requests and changes
- See `CHANGES.md` for version history

## Features

- Real-time audio capture and analysis
- AI-powered sound classification using YAMNet
- Web-based interface for monitoring and control
- RESTful API for integration
- Cross-platform support (Windows, Linux, macOS)

## Quick Start

### Prerequisites

- Python 3.10 or 3.11
- Flutter SDK (for frontend development)
- Git

### Running the Application

#### Windows
```bash
# Start both backend and frontend
.\run_soundTracker.bat

# Stop the application
.\stop_soundTracker.bat
```

#### Linux/macOS
```bash
# Make scripts executable
chmod +x *.sh

# Start both backend and frontend
./run_soundTracker.sh

# Stop the application
./stop_soundTracker.sh
```

## Backend Setup

1. Navigate to the backend directory:
   ```bash
   cd backend
   ```

2. Create and activate a Python virtual environment:
   - **Windows**:
     ```bash
     python -m venv venv
     .\venv\Scripts\Activate
     ```
   - **Linux/macOS**:
     ```bash
     python3 -m venv venv
     source venv/bin/activate
     ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Set up environment variables:
   ```bash
   copy .env.sample .env
   ```
   Edit the `.env` file as needed.

5. Start the backend server:
   ```bash
   python -m uvicorn main:app --reload
   ```

## Frontend Setup

1. Navigate to the frontend directory:
   ```bash
   cd frontend
   ```

2. Install dependencies:
   ```bash
   flutter pub get
   ```

3. Run the Flutter web app:
   ```bash
   flutter run -d chrome --web-port 3030
   ```

## API Documentation

For detailed API documentation, see [API_DOCUMENTATION.md](backend/API_DOCUMENTATION.md).

### Key Endpoints

- `GET /health` - Check API status
- `GET /api/v1/sounds/` - List all sound events
- `POST /api/v1/sounds/` - Create a new sound event
- `GET /api/v1/ai/classes` - List available sound classes
- `POST /api/v1/ai/predict` - Analyze audio and predict sound class

## Development

### Backend
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
   