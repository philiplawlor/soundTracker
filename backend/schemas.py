from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class SoundEventCreate(BaseModel):
    timestamp: datetime
    noise_level: float
    sound_type: Optional[str] = None
    description: Optional[str] = None

class SoundEventRead(SoundEventCreate):
    id: int
