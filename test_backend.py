import sys
import os

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath('.'))

try:
    from src.backend.main import app
    import uvicorn
    
    print("Backend imports successful!")
    print("Starting Uvicorn server...")
    uvicorn.run(app, host="0.0.0.0", port=8000)
except Exception as e:
    print(f"Error: {e}")
    raise
