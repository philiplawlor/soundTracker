# SoundTracker Backend

This is the backend service for the SoundTracker application, providing audio processing and API endpoints.

## Features

- Audio capture and processing
- WebSocket support for real-time audio streaming
- REST API for managing audio data
- SQLite database for persistent storage

## Setup

1. Create a virtual environment:
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

2. Install dependencies:
   ```bash
   pip install -e .
   ```

3. Configure environment variables:
   - Copy `.env.sample` to `.env`
   - Update the configuration as needed

4. Run the development server:
   ```bash
   ./run_backend.sh
   ```

## Development

- The main application is in `main.py`
- API routes are in the `routers/` directory
- Database models are in `models.py`
- Configuration is in `config.py`

## Testing

Run tests with:
```bash
pytest
```

## License

MIT
