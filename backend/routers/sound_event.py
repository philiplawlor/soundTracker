from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from ..database import get_session
from ..models import SoundEvent
from ..schemas import SoundEventCreate, SoundEventRead
from typing import List

router = APIRouter(prefix="/sound-events", tags=["Sound Events"])

@router.post("/", response_model=SoundEventRead)
def create_sound_event(event: SoundEventCreate, session: Session = Depends(get_session)):
    db_event = SoundEvent(**event.dict())
    session.add(db_event)
    session.commit()
    session.refresh(db_event)
    return db_event

@router.get("/", response_model=List[SoundEventRead])
def read_sound_events(skip: int = 0, limit: int = 100, session: Session = Depends(get_session)):
    events = session.exec(select(SoundEvent).offset(skip).limit(limit)).all()
    return events

@router.get("/{event_id}", response_model=SoundEventRead)
def read_sound_event(event_id: int, session: Session = Depends(get_session)):
    event = session.get(SoundEvent, event_id)
    if not event:
        raise HTTPException(status_code=404, detail="Sound event not found")
    return event
