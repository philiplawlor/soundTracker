# CHANGES.md - SoundTracker

## [0.7.0] - 2025-07-25
- **Major Project Restructure**: Migrated the backend application to a standard `src`-layout to resolve persistent `ModuleNotFoundError` issues and improve package structure.
- **Fixed All Import Errors**: Corrected all local application imports to use relative paths (e.g., `from ..database import ...`), making the package structure robust.
- **Dependency and Environment Stabilization**:
    - Rebuilt the virtual environment and generated a complete, accurate `requirements.txt` using `pip freeze`.
    - Resolved missing dependencies (`pydantic-settings`, `websockets`) that were causing startup crashes.
    - Fixed Pydantic `orm_mode` deprecation warning by updating it to `from_attributes`.
- **Packaging and Installation**: Correctly configured `pyproject.toml` to support the `src`-layout and allow for a stable installation in editable mode (`pip install -e .`).
- **Server Stability**: The backend server now launches reliably without import errors or dependency warnings.

## [0.6.0] - 2025-07-25
- Stabilized the AI backend by resolving persistent test collection failures.
- Rewrote AI tests to use a fully isolated FastAPI app instance, improving test reliability.
- Fixed Pydantic validation and data type errors in the `/ai/identify` endpoint.
- Ensured AI model is loaded correctly via dependency injection, preventing startup conflicts.
- Confirmed that AI sound classification results are now correctly saved to the database.

## [0.5.2] - 2025-07-03
- Fixed audio recording on web platform
- Resolved stream subscription errors in audio recorder
- Improved error handling and user feedback
- Made error messages selectable for easier debugging
- Fixed UI layout and widget tree structure
- Updated dependencies for better compatibility
- Fixed MediaRecorder JS interop issues
- Improved audio playback and recording reliability
- Added proper error handling for web audio API
- Updated run scripts to use port 3030 by default

## [0.5.1] - 2025-07-03
- Fixed double `/ai/ai` router prefix in API endpoints
- Added comprehensive API documentation in `API_DOCUMENTATION.md`
- Updated README.md with detailed setup and usage instructions
- Resolved Pydantic/SQLModel warning about `metadata` shadowing
- Improved database model configuration for better compatibility
- Added proper type hints and documentation throughout the codebase
- Enhanced test coverage with additional edge cases
- Fixed virtual environment activation in run scripts

## [0.5.0] - 2025-07-03
- Fixed audio playback and identification in the web interface
- Implemented web-compatible audio playback using Web Audio API
- Resolved 404 errors in the identify sound endpoint
- Added debug endpoints for troubleshooting
- Improved error handling and logging
- Updated documentation and dependencies

## [0.4.0] - 2025-06-11
- Fixed WebSocket endpoint for real-time audio device listing and monitoring
- Added detailed logging for WebSocket connections and message handling
- Implemented proper error handling and connection management for WebSockets
- Added test scripts for WebSocket communication
- Improved backend project structure and imports
- Added setup.py for proper package installation
- Updated documentation and version numbers

## [0.3.2] - 2025-05-16
- Added run/stop scripts for backend and frontend (`run_soundTracker`/`stop_soundTracker`) for Windows and Bash
- Documented usage in README
- Improved developer experience for all platforms

## [0.3.1] - 2025-05-15
- Integrated real YAMNet model (TensorFlow Hub) for sound classification
- Fixed class map download to use official repo
- Patched tests to use valid WAV files and close SQLite properly
- All tests passing

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
