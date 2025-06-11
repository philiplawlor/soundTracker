import os
import sys
from pathlib import Path
from fastapi import FastAPI, Request, APIRouter, WebSocket
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse

# Import using absolute paths
from backend.database import create_db_and_tables
from backend.routers import sound_event, ai, audio_capture
from backend.config import settings

# Get the base directory
BASE_DIR = Path(__file__).parent
STATIC_DIR = BASE_DIR / "static"

# Create necessary directories
os.makedirs(STATIC_DIR, exist_ok=True)

app = FastAPI(title="SoundTracker API")

# Mount static files
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")


# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS.split(",") if settings.CORS_ORIGINS != "*" else ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routers with v1 prefix
api_router = APIRouter(prefix="/api/v1")
api_router.include_router(sound_event.router)
api_router.include_router(ai.router)
api_router.include_router(audio_capture.router)
app.include_router(api_router)

# Include WebSocket router at the root level
app.include_router(audio_capture.ws_router)

# Simple WebSocket test endpoint
@app.websocket("/ws/test")
async def websocket_test(websocket: WebSocket):
    """Simple WebSocket test endpoint"""
    await websocket.accept()
    try:
        while True:
            data = await websocket.receive_text()
            await websocket.send_text(f"Echo: {data}")
    except Exception as e:
        print(f"WebSocket error: {e}")
    finally:
        await websocket.close()

# Root endpoint
@app.get("/", response_class=HTMLResponse)
async def root():
    """Serve the main application page."""
    try:
        with open("backend/static/audio_monitor.html", "r") as f:
            return HTMLResponse(content=f.read(), media_type="text/html")
    except FileNotFoundError:
        return HTMLResponse(
            content="<h1>SoundTracker Backend</h1><p>Welcome to the SoundTracker API. Please use the API endpoints to interact with the system.</p>",
            media_type="text/html"
        )

# Audio test page endpoint
@app.get("/audio-test", response_class=HTMLResponse)
async def audio_test():
    """Serve the audio test page."""
    with open("static/audio_test.html", "r") as f:
        return HTMLResponse(content=f.read(), media_type="text/html")

@app.on_event("startup")
async def on_startup():
    """Initialize application services."""
    create_db_and_tables()
    
    # Ensure static directory exists
    os.makedirs("static", exist_ok=True)
