from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.docs import get_swagger_ui_html
from fastapi.openapi.utils import get_openapi
from typing import Dict, Any
import uvicorn
import os

from database import create_db_and_tables
from routers.sound_event import router as sound_event_router
from routers.ai import router as ai_router

# Initialize FastAPI app with metadata
app = FastAPI(
    title="SoundTracker API",
    description="Backend API for the SoundTracker application",
    version="1.0.0",
    docs_url=None,  # Disable default docs to use customized version
    redoc_url=None
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers with prefixes
app.include_router(sound_event_router, prefix="/api/v1/sounds", tags=["Sound Events"])
app.include_router(ai_router, prefix="/api/v1/ai", tags=["AI"])

# Root endpoint
@app.get("/", include_in_schema=False)
async def root() -> Dict[str, str]:
    """Root endpoint with welcome message and API information."""
    return {
        "message": "Welcome to SoundTracker API",
        "status": "running",
        "docs": "/docs",
        "redoc": "/redoc"
    }

# Custom docs endpoints
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

# Database initialization
@app.on_event("startup")
async def on_startup():
    """Initialize database and other resources on startup."""
    try:
        create_db_and_tables()
        print("✅ Database tables created successfully")
    except Exception as e:
        print(f"❌ Error initializing database: {e}")
        raise

# For local development
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
