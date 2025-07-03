import os
import sys 
from pathlib import Path
from typing import Dict, Any

from fastapi import FastAPI, HTTPException, WebSocket, APIRouter
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.docs import get_swagger_ui_html
from fastapi.openapi.utils import get_openapi
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles

# Add the backend directory to the Python path
BACKEND_DIR = Path(__file__).parent.absolute()
sys.path.append(str(BACKEND_DIR))

# Local imports
from database import create_db_and_tables
from routers.sound_event import router as sound_event_router
from routers.ai import router as ai_router
from config import settings

# Import audio_capture if it exists
try:
    from routers import audio_capture
except ImportError:
    audio_capture = None

# Get the base directory
BASE_DIR = Path(__file__).parent
STATIC_DIR = BASE_DIR / "static"

# Create necessary directories
STATIC_DIR.mkdir(parents=True, exist_ok=True)

# Initialize FastAPI app with metadata
app = FastAPI(
    title="SoundTracker API",
    description="Backend API for the SoundTracker application",
    version="1.0.0",
    docs_url=None,  # Disable default docs to use customized version
    redoc_url=None
)

# Mount static files
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS.split(",") if hasattr(settings, 'CORS_ORIGINS') and settings.CORS_ORIGINS != "*" else ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routers with v1 prefix
api_router = APIRouter(prefix="/api/v1")
api_router.include_router(sound_event_router, prefix="/sounds", tags=["Sound Events"])
# The AI router already has its own /ai prefix
api_router.include_router(ai_router, tags=["AI"])

# Include WebSocket router at the root level
if audio_capture and hasattr(audio_capture, 'ws_router'):
    app.include_router(audio_capture.ws_router)

# Include the API router
app.include_router(api_router)

# Root endpoint
@app.get("/", response_class=HTMLResponse, include_in_schema=False)
async def root():
    """Serve the main application page."""
    try:
        with open(os.path.join(STATIC_DIR, "audio_monitor.html"), "r") as f:
            return HTMLResponse(content=f.read(), media_type="text/html")
    except FileNotFoundError:
        return HTMLResponse(
            content="""<html><head><title>SoundTracker API</title></head><body><h1>SoundTracker Backend</h1><p>Welcome to the SoundTracker API.</p><p>API Documentation: <a href="/docs">Swagger UI</a></p><p>Health Check: <a href="/health">/health</a></p></body></html>""",
            media_type="text/html"
        )

# API Documentation endpoints
@app.get("/docs", include_in_schema=False)
async def custom_swagger_ui_html():
    """Serve custom Swagger UI with dark theme."""
    return get_swagger_ui_html(
        openapi_url="/openapi.json",
        title="SoundTracker API - Swagger UI",
        swagger_favicon_url="https://fastapi.tiangolo.com/img/favicon.png"
    )

@app.get("/openapi.json", include_in_schema=False)
async def get_custom_openapi():
    """Generate custom OpenAPI schema."""
    if app.openapi_schema:
        return app.openapi_schema
    
    openapi_schema = get_openapi(
        title="SoundTracker API",
        version="1.0.0",
        description="Backend API for the SoundTracker application",
        routes=app.routes,
    )
    
    # Add custom documentation
    openapi_schema["info"]["x-logo"] = {
        "url": "https://fastapi.tiangolo.com/img/logo-margin/logo-teal.png"
    }
    
    app.openapi_schema = openapi_schema
    return app.openapi_schema

# Health check endpoint
@app.get("/health", include_in_schema=False)
async def health_check() -> Dict[str, str]:
    """Health check endpoint for monitoring."""
    return {"status": "healthy"}

# Audio test page endpoint
@app.get("/audio-test", response_class=HTMLResponse, include_in_schema=False)
async def audio_test():
    """Serve the audio test page."""
    try:
        with open(os.path.join(STATIC_DIR, "audio_test.html"), "r") as f:
            return HTMLResponse(content=f.read(), media_type="text/html")
    except FileNotFoundError:
        return HTMLResponse(
            content="<h1>Audio Test Page Not Found</h1><p>The audio test page could not be found.</p>",
            status_code=404,
            media_type="text/html"
        )

# WebSocket test endpoint
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

# Database initialization
@app.on_event("startup")
async def on_startup():
    """Initialize database and other resources on startup."""
    try:
        create_db_and_tables()
        # Ensure static directory exists
        os.makedirs(STATIC_DIR, exist_ok=True)
        print("✅ Database tables created successfully")
    except Exception as e:
        print(f"❌ Error initializing database: {e}")
        raise

# Debug endpoint to list all routes
@app.get("/debug/routes", include_in_schema=False)
async def list_routes():
    """List all registered routes for debugging."""
    routes = []
    for route in app.routes:
        if hasattr(route, "path"):
            path = route.path
            methods = []
            if hasattr(route, "methods"):
                methods = list(route.methods or [])
            elif hasattr(route, "endpoint") and hasattr(route.endpoint, "methods"):
                methods = list(route.endpoint.methods or [])
            
            routes.append({
                "path": path,
                "methods": methods,
                "name": getattr(route, "name", str(route))
            })
    
    return {"routes": routes}

# For local development
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="debug"
    )
    # Static directory is already created at the top level
