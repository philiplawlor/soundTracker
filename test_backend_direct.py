import sys
import os

# Add the src directory to the Python path
sys.path.insert(0, os.path.abspath('.'))

# Import the FastAPI app
try:
    from src.backend.main import app
    import uvicorn
    
    print("Successfully imported the FastAPI app!")
    print("Starting Uvicorn server...")
    
    # Run the server
    uvicorn.run(
        "src.backend.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="debug"
    )
    
except ImportError as e:
    print(f"Import error: {e}")
    print("Python path:", sys.path)
    print("Current working directory:", os.getcwd())
    raise

except Exception as e:
    print(f"Error: {e}")
    raise
