# CHANGES.md - SoundTracker

## [0.4.0] - 2025-06-11
- Fixed WebSocket endpoint for real-time audio device listing and monitoring
- Added detailed logging for WebSocket connections and message handling
- Implemented proper error handling and connection management for WebSockets
- Added test scripts for WebSocket communication
- Improved backend project structure and imports
- Added setup.py for proper package installation
- Updated documentation and version numbers

## [0.3.0] - 2025-05-15
- AI sound identification endpoint (`/ai/identify`) added
- Pluggable backend AI stub (random label, ready for ML model)
- Pydantic schema and router for AI
- Unit test for AI endpoint
- README updated with AI API usage
- Version bump to 0.3.0

## [0.2.0] - 2025-05-15
- Backend folder structure created with FastAPI, SQLModel, and SQLite
- REST API for sound events with CRUD and filtering
- Unit tests for API and models (pytest)
- Bash and Batch run scripts for backend
- Updated README.md with backend setup and test instructions
- Version bump to 0.2.0

## [0.1.0] - 2025-05-15
- Project management files (PLANNING.md, TASK.md, TODO.md, CHANGES.md, README.md) created
- Initial project planning and feature outline established
