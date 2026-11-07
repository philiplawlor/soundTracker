from fastapi import FastAPI
import uvicorn
import sys
import os

app = FastAPI()

@app.get("/")
async def root():
    return {
        "message": "Hello, World!",
        "python_version": sys.version,
        "current_directory": os.getcwd(),
        "python_path": sys.path
    }

if __name__ == "__main__":
    print("Starting test FastAPI server...")
    print(f"Python version: {sys.version}")
    print(f"Current directory: {os.getcwd()}")
    print("Python path:")
    for p in sys.path:
        print(f"  {p}")
    
    uvicorn.run("test_fastapi:app", host="0.0.0.0", port=8000, reload=True)
