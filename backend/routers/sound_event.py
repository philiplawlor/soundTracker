from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlmodel import Session, select, or_

from database import get_session
from models import SoundEvent, SoundType
from schemas import SoundEventCreate, SoundEventRead

router = APIRouter(prefix="/sounds", tags=["Sound Events"])

def get_sound_event_or_404(event_id: int, session: Session) -> SoundEvent:
    """Helper function to get a sound event by ID or raise 404."""
    event = session.get(SoundEvent, event_id)
    if not event:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Sound event with ID {event_id} not found"
        )
    return event

@router.post(
    "/", 
    response_model=SoundEventRead,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new sound event",
    response_description="The created sound event"
)
async def create_sound_event(
    event: SoundEventCreate, 
    session: Session = Depends(get_session)
) -> SoundEvent:
    """
    Create a new sound event with the given data.
    
    - **audio_file_path**: Path to the audio file (optional)
    - **sound_type**: Type of sound (unknown, speech, music, noise, silence)
    - **confidence**: Confidence score between 0 and 1
    - **noise_level_db**: Noise level in decibels (optional)
    - **duration_seconds**: Duration of the audio in seconds (optional)
    - **sample_rate**: Audio sample rate in Hz (optional)
    - **channels**: Number of audio channels (default: 1)
    - **event_metadata**: Additional metadata as key-value pairs (optional)
    """
    db_event = SoundEvent.model_validate(event)
    session.add(db_event)
    session.commit()
    session.refresh(db_event)
    return db_event

@router.get(
    "/", 
    response_model=List[SoundEventRead],
    summary="List all sound events",
    response_description="List of sound events"
)
async def list_sound_events(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of records to return"),
    sound_type: Optional[SoundType] = Query(None, description="Filter by sound type"),
    min_confidence: Optional[float] = Query(None, ge=0.0, le=1.0, description="Minimum confidence score"),
    start_date: Optional[datetime] = Query(None, description="Filter by start date"),
    end_date: Optional[datetime] = Query(None, description="Filter by end date"),
    session: Session = Depends(get_session)
) -> List[SoundEvent]:
    """
    Retrieve a list of sound events with optional filtering.
    
    - **skip**: Number of records to skip (for pagination)
    - **limit**: Maximum number of records to return (max 1000)
    - **sound_type**: Filter by type of sound
    - **min_confidence**: Filter by minimum confidence score (0.0 to 1.0)
    - **start_date**: Filter events after this datetime
    - **end_date**: Filter events before this datetime
    """
    query = select(SoundEvent)
    
    # Apply filters
    if sound_type:
        query = query.where(SoundEvent.sound_type == sound_type)
    if min_confidence is not None:
        query = query.where(SoundEvent.confidence >= min_confidence)
    if start_date:
        query = query.where(SoundEvent.timestamp >= start_date)
    if end_date:
        # Include the entire end date
        end_date = end_date + timedelta(days=1)
        query = query.where(SoundEvent.timestamp < end_date)
    
    # Apply pagination and order by most recent first
    query = query.offset(skip).limit(limit).order_by(SoundEvent.timestamp.desc())
    
    return session.exec(query).all()

@router.get(
    "/{event_id}", 
    response_model=SoundEventRead,
    summary="Get a sound event by ID",
    responses={
        404: {"description": "Sound event not found"}
    }
)
async def get_sound_event(
    event_id: int, 
    session: Session = Depends(get_session)
) -> SoundEvent:
    """
    Retrieve a specific sound event by its ID.
    
    - **event_id**: The ID of the sound event to retrieve
    """
    return get_sound_event_or_404(event_id, session)

@router.delete(
    "/{event_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a sound event",
    responses={
        204: {"description": "Sound event deleted successfully"},
        404: {"description": "Sound event not found"}
    }
)
async def delete_sound_event(
    event_id: int,
    session: Session = Depends(get_session)
) -> None:
    """
    Delete a sound event by ID.
    
    - **event_id**: The ID of the sound event to delete
    """
    event = get_sound_event_or_404(event_id, session)
    session.delete(event)
    session.commit()
    return None
