from sqlmodel import SQLModel, Field
from typing import Optional
from datetime import datetime

class SoundEvent(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    timestamp: datetime
    noise_level: float
    sound_type: Optional[str] = None
    description: Optional[str] = None
