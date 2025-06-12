from pydantic import BaseModel, Field, HttpUrl
from typing import Optional, List, Dict, Any, Union
from datetime import datetime
from enum import Enum

# Enums for sound classification
class SoundCategory(str, Enum):
    SPEECH = "speech"
    MUSIC = "music"
    NOISE = "noise"
    SILENCE = "silence"
    UNKNOWN = "unknown"
    OTHER = "other"

# Base models
class SoundEventBase(BaseModel):
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    noise_level: float = Field(..., ge=0.0, le=1.0, description="Normalized noise level (0.0 to 1.0)")
    sound_type: Optional[str] = Field(None, description="Type/category of the sound")
    description: Optional[str] = Field(None, description="Additional description or notes")
    confidence: Optional[float] = Field(None, ge=0.0, le=1.0, description="Confidence score of the prediction")

class SoundEventCreate(SoundEventBase):
    pass

class SoundEventRead(SoundEventBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

# AI Sound Classification Models
class AISoundIdentifyResponse(BaseModel):
    """Response model for basic sound identification"""
    label: str = Field(..., description="The predicted sound label")
    confidence: Optional[float] = Field(None, ge=0.0, le=1.0, description="Confidence score of the prediction")

class SoundPrediction(BaseModel):
    """Model representing a single sound prediction with confidence"""
    label: str = Field(..., description="The predicted sound class")
    score: float = Field(..., ge=0.0, le=1.0, description="Confidence score (0.0 to 1.0)")
    category: Optional[SoundCategory] = Field(None, description="Broad category of the sound")

class AISoundClassifyRequest(BaseModel):
    """Request model for sound classification"""
    audio_data: bytes = Field(..., description="Raw audio data in WAV format")
    top_k: Optional[int] = Field(5, ge=1, le=10, description="Number of top predictions to return (1-10)")
    min_confidence: Optional[float] = Field(0.1, ge=0.0, le=1.0, description="Minimum confidence threshold for predictions")

class AISoundClassifyResponse(BaseModel):
    """Response model for sound classification"""
    success: bool = Field(..., description="Whether the classification was successful")
    predictions: List[SoundPrediction] = Field(default_factory=list, description="List of predictions with confidence scores")
    message: Optional[str] = Field(None, description="Additional information or error message")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="When the classification was performed")
    model: str = Field("yamnet", description="Name/version of the model used for classification")

# WebSocket Models
class WebSocketMessageType(str, Enum):
    CLASSIFY = "classify"
    CLASSIFICATION_RESULT = "classification_result"
    ERROR = "error"
    STATUS = "status"

class WebSocketMessage(BaseModel):
    """Base WebSocket message model"""
    type: WebSocketMessageType = Field(..., description="Type of the WebSocket message")
    data: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Message payload")

class WebSocketClassifyRequest(WebSocketMessage):
    """WebSocket message for classification requests"""
    type: WebSocketMessageType = Field(WebSocketMessageType.CLASSIFY, const=True)
    audio_data: str = Field(..., description="Base64 encoded audio data")
    top_k: Optional[int] = Field(3, ge=1, le=10, description="Number of top predictions to return")
    request_id: Optional[str] = Field(None, description="Client-generated request ID for correlation")

class WebSocketClassificationResult(WebSocketMessage):
    """WebSocket message for classification results"""
    type: WebSocketMessageType = Field(WebSocketMessageType.CLASSIFICATION_RESULT, const=True)
    request_id: Optional[str] = Field(None, description="Client-generated request ID for correlation")
    predictions: List[Dict[str, Any]] = Field(default_factory=list, description="List of prediction objects")
    success: bool = Field(True, description="Whether the classification was successful")
    error: Optional[Dict[str, Any]] = Field(None, description="Error details if classification failed")

# Response models for API documentation
class HTTPErrorResponse(BaseModel):
    """Standard error response model"""
    detail: Union[str, Dict[str, Any]] = Field(..., description="Error details")
    status_code: int = Field(..., description="HTTP status code")
    error: str = Field(..., description="Error type/name")
