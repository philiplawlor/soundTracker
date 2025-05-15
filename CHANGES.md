# CHANGES.md - SoundTracker

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
