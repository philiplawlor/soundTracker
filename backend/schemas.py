from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from datetime import datetime
from enum import Enum

class SoundType(str, Enum):
    """Enum for sound type classification."""
    UNKNOWN = "unknown"
    SPEECH = "speech"
    MUSIC = "music"
    NOISE = "noise"
    SILENCE = "silence"

class SoundEventBase(BaseModel):
    """Base schema for sound event data."""
    audio_file_path: Optional[str] = Field(
        None, 
        description="Path to the stored audio file"
    )
    sound_type: SoundType = Field(
        default=SoundType.UNKNOWN,
        description="Type of sound detected"
    )
    confidence: float = Field(
        default=0.0, 
        ge=0.0, 
        le=1.0,
        description="Confidence score between 0 and 1"
    )
    noise_level_db: Optional[float] = Field(
        None,
        ge=0.0,
        description="Noise level in decibels"
    )
    duration_seconds: Optional[float] = Field(
        None,
        gt=0.0,
        description="Duration of the audio in seconds"
    )
    sample_rate: Optional[int] = Field(
        None,
        gt=0,
        description="Audio sample rate in Hz"
    )
    channels: Optional[int] = Field(
        1,
        gt=0,
        description="Number of audio channels"
    )
    event_metadata: Dict[str, Any] = Field(
        default_factory=dict,
        description="Additional metadata about the sound event"
    )

class SoundEventCreate(SoundEventBase):
    """Schema for creating a new sound event."""
    pass

class SoundEventRead(SoundEventBase):
    """Schema for reading sound event data (includes ID and timestamp)."""
    id: int
    timestamp: datetime

    class Config:
        orm_mode = True

class AISoundIdentifyResponse(BaseModel):
    """Response schema for AI sound identification."""
    label: str
    score: float
    metadata: Dict[str, Any] = {}
