"""
Minimal test FastAPI application to verify server functionality.
"""
import logging
import sys
from fastapi import FastAPI, Request
import uvicorn

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

app = FastAPI()

# Add middleware to log all requests
@app.middleware("http")
async def log_requests(request: Request, call_next):
    logger.info(f"Request: {request.method} {request.url}")
    try:
        response = await call_next(request)
        return response
    except Exception as e:
        logger.error(f"Error processing request: {e}", exc_info=True)
        raise

@app.get("/")
async def read_root():
    logger.info("Root endpoint called")
    return {"message": "Hello, this is a test endpoint!"}

@app.get("/health")
async def health_check():
    logger.info("Health check endpoint called")
    return {"status": "healthy"}

if __name__ == "__main__":
    logger.info("Starting test server on http://0.0.0.0:8000")
    try:
        uvicorn.run(
            "test_app:app",
            host="0.0.0.0",
            port=8000,
            reload=True,
            log_level="info",
            access_log=True,
            workers=1
        )
    except Exception as e:
        logger.error(f"Failed to start server: {e}", exc_info=True)
