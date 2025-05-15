# SoundTracker

![version](https://img.shields.io/badge/version-0.1.0-blue)

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

## Setup
- Always use a Python virtual environment for backend development
- Set up environment variables in `.env` (do not commit secrets)

## Contributing
- Keep files under 500 lines, split into modules as needed
- Write unit tests for all new features
- Follow PEP8 and use type hints
- Update documentation and PM files with every change
