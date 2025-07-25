# SoundTracker API Documentation

## Base URL
All API endpoints are prefixed with `/api/v1`.

## Authentication
Currently, the API does not require authentication for development. In production, consider adding JWT or OAuth2 authentication.

## Endpoints

### Health Check
- **URL**: `/health`
- **Method**: `GET`
- **Description**: Check if the API is running
- **Response**:
  ```json
  {
    "status": "healthy"
  }
  ```

### List All Sound Events
- **URL**: `/api/v1/sounds/`
- **Method**: `GET`
- **Description**: Retrieve a list of all sound events
- **Response**:
  ```json
  [
    {
      "id": 1,
      "audio_file_path": "/path/to/audio.wav",
      "sound_type": "speech",
      "confidence": 0.95,
      "noise_level_db": 42.5,
      "duration_seconds": 10.5,
      "sample_rate": 44100,
      "channels": 2,
      "event_metadata": {
        "speaker_id": "spk_123",
        "language": "en-US",
        "transcription": "This is a test transcription"
      },
      "created_at": "2023-01-01T00:00:00"
    }
  ]
  ```

### Create Sound Event
- **URL**: `/api/v1/sounds/`
- **Method**: `POST`
- **Description**: Create a new sound event
- **Request Body**:
  ```json
  {
    "audio_file_path": "/path/to/audio.wav",
    "sound_type": "speech",
    "confidence": 0.95,
    "noise_level_db": 42.5,
    "duration_seconds": 10.5,
    "sample_rate": 44100,
    "channels": 2,
    "event_metadata": {
      "speaker_id": "spk_123",
      "language": "en-US",
      "transcription": "This is a test transcription"
    }
  }
  ```
- **Response**:
  ```json
  {
    "id": 1,
    "audio_file_path": "/path/to/audio.wav",
    "sound_type": "speech",
    "confidence": 0.95,
    "noise_level_db": 42.5,
    "duration_seconds": 10.5,
    "sample_rate": 44100,
    "channels": 2,
    "event_metadata": {
      "speaker_id": "spk_123",
      "language": "en-US",
      "transcription": "This is a test transcription"
    },
    "created_at": "2023-01-01T00:00:00"
  }
  ```

### Get Sound Event by ID
- **URL**: `/api/v1/sounds/{event_id}`
- **Method**: `GET`
- **Description**: Get details of a specific sound event
- **URL Parameters**:
  - `event_id` (required): ID of the sound event to retrieve
- **Response**: Same as Create Sound Event response

### Delete Sound Event
- **URL**: `/api/v1/sounds/{event_id}`
- **Method**: `DELETE`
- **Description**: Delete a sound event
- **URL Parameters**:
  - `event_id` (required): ID of the sound event to delete
- **Response**:
  ```json
  {
    "status": "success",
    "message": "Sound event deleted successfully"
  }
  ```

### AI Status
- **URL**: `/api/v1/ai/status`
- **Method**: `GET`
- **Description**: Check if the AI model is loaded and ready
- **Response**:
  ```json
  {
    "status": "ready",
    "model_name": "YAMNet",
    "version": "1.0.0"
  }
  ```

### List Sound Classes
- **URL**: `/api/v1/ai/classes`
- **Method**: `GET`
- **Description**: List all sound classes that the model can recognize
- **Response**:
  ```json
  {
    "success": true,
    "classes": [
      {"id": 0, "name": "Speech"},
      {"id": 1, "name": "Music"},
      {"id": 2, "name": "Noise"}
    ]
  }
  ```

### Predict Sound from Audio
- **URL**: `/api/v1/ai/predict`
- **Method**: `POST`
- **Description**: Analyze an audio file and predict the sound class
- **Request**: `multipart/form-data` with a file field named `file`
- **Response**:
  ```json
  {
    "success": true,
    "predictions": [
      {
        "class_name": "Speech",
        "confidence": 0.95,
        "class_id": 0
      },
      {
        "class_name": "Music",
        "confidence": 0.03,
        "class_id": 1
      }
    ],
    "error": null
  }
  ```

### WebSocket Test
- **URL**: `/ws/test`
- **Protocol**: `WebSocket`
- **Description**: Test WebSocket connection
- **Messages**:
  - Send any message to receive an echo response

## Error Responses

### 400 Bad Request
```json
{
  "detail": "Invalid request data"
}
```

### 404 Not Found
```json
{
  "detail": "Sound event not found"
}
```

### 500 Internal Server Error
```json
{
  "detail": "Internal server error"
}
```

## Rate Limiting
Currently, there is no rate limiting in place. For production, consider implementing rate limiting to prevent abuse.
