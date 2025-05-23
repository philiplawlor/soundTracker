from fastapi import FastAPI
from .database import create_db_and_tables
from .routers import sound_event
from .routers import ai

app = FastAPI(title="SoundTracker API")

@app.on_event("startup")
def on_startup():
    create_db_and_tables()

app.include_router(sound_event.router)
app.include_router(ai.router)
