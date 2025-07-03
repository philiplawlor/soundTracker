from sqlmodel import SQLModel, Field, Column, JSON
from typing import Optional, Dict, Any, List
from datetime import datetime
from enum import Enum
from pydantic import BaseModel, Field as PydanticField
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.types import TypeDecorator, VARCHAR
import json

# Custom JSON type for better compatibility
class JSONEncodedDict(TypeDecorator):
    """Represents an immutable structure as a json-encoded string."""
    
    impl = VARCHAR
    
    def process_bind_param(self, value, dialect):
        if value is not None:
            value = json.dumps(value)
        return value
    
    def process_result_value(self, value, dialect):
        if value is not None:
            value = json.loads(value)
        return value

class SoundType(str, Enum):
    UNKNOWN = "unknown"
    SPEECH = "speech"
    MUSIC = "music"
    NOISE = "noise"
    SILENCE = "silence"
    # Add more sound types as needed

class SoundEventBase(SQLModel):
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    audio_file_path: Optional[str] = Field(default=None, nullable=True)  # Path to stored audio file
    sound_type: SoundType = Field(default=SoundType.UNKNOWN)
    confidence: float = Field(default=0.0, ge=0.0, le=1.0)  # Confidence score 0-1
    noise_level_db: Optional[float] = Field(default=None, nullable=True)  # In decibels
    duration_seconds: Optional[float] = Field(default=None, nullable=True)  # Duration in seconds
    sample_rate: Optional[int] = Field(default=None, nullable=True)  # Sample rate in Hz
    channels: Optional[int] = Field(default=1, ge=1, nullable=True)  # Number of audio channels
    
    # Using sa_column to properly define the column type and avoid SQLModel warnings
    event_metadata: Dict[str, Any] = Field(
        default_factory=dict,
        sa_column=Column(
            JSONB().with_variant(JSONEncodedDict, "sqlite"),
            nullable=True,
            info={"primary_key": False}  # Explicitly mark as non-primary key
        )
    )

class SoundEvent(SoundEventBase, table=True):
    """Database model for sound events."""
    __tablename__ = "sound_events"
    
    id: Optional[int] = Field(default=None, primary_key=True)

# Pydantic model for creating events (without id)
class SoundEventCreate(SQLModel):
    """Schema for creating a new sound event."""
    audio_file_path: Optional[str] = None
    sound_type: SoundType = SoundType.UNKNOWN
    confidence: float = 0.0
    noise_level_db: Optional[float] = None
    duration_seconds: Optional[float] = None
    sample_rate: Optional[int] = None
    channels: Optional[int] = 1
    event_metadata: Dict[str, Any] = {}

# Pydantic model for API responses (includes id)
class SoundEventRead(SoundEventBase):
    """Schema for reading sound event data (includes ID)."""
    id: int
