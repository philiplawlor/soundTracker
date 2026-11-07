# Task Management for SoundTracker (v0.5.0)

This file tracks active tasks, backlog, and sub-tasks for the project. Update this list as you work.

## Current Focus Areas
- [ ] Complete WebSocket integration for real-time audio streaming
- [ ] Implement audio device management in Flutter
- [ ] Enhance audio visualization
- [ ] Add error handling and recovery

## Active Tasks
### Backend
- [x] Set up Python backend project structure with FastAPI
- [x] Implement audio capture and noise level analysis
- [x] Create WebSocket endpoint for real-time audio streaming
- [x] Implement device enumeration API
- [ ] Add audio format conversion utilities
- [ ] Implement audio data persistence
- [ ] Add API endpoints for historical data

### Frontend
- [x] Set up Flutter project structure
- [x] Implement basic audio recording
- [ ] Complete WebSocket integration
  - [x] Basic WebSocket connection
  - [ ] Handle reconnection logic
  - [ ] Buffer management for smooth visualization
- [ ] Audio device management
  - [x] List available devices
  - [ ] Implement device selection
  - [ ] Handle device changes during runtime
- [ ] Audio visualization
  - [x] Basic waveform display
  - [ ] Real-time dBFS meter
  - [ ] Historical data charts
- [ ] User interface
  - [ ] Recording controls
  - [ ] Device selection panel
  - [ ] Settings page

### Database
- [ ] Design SQLite schema
- [ ] Implement data access layer
- [ ] Add data migration support

## Backlog
### High Priority
- [ ] Implement sound classification
- [ ] Add data export functionality
- [ ] Create dashboard with analytics
- [ ] Implement user preferences

### Medium Priority
- [ ] Add unit and integration tests
- [ ] Implement error boundaries
- [ ] Add logging and monitoring
- [ ] Create build and deployment pipelines

### Future Features
- [ ] User authentication
- [ ] Cloud sync
- [ ] Mobile background processing
- [ ] Wearable device integration
- [ ] Advanced sound analysis
- [ ] Customizable alerts and notifications

## Discovered During Work
- Need to handle sample rate conversion between devices
- Consider adding audio normalization
- Potential memory optimization needed for long recordings
- Add audio session management for mobile platforms
- Consider adding audio effects processing

## Notes
- Web audio APIs have different constraints than native
- Need to handle permissions gracefully on all platforms
- Consider adding audio format conversion for compatibility
- Add proper error handling for device access issues
