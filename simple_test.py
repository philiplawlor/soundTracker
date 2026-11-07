import sys
import os

def test_environment():
    print("=== Python Environment Test ===")
    print(f"Python version: {sys.version}")
    print(f"Current working directory: {os.getcwd()}")
    print("\nPython path:")
    for p in sys.path:
        print(f"  {p}")
    
    print("\nTesting FastAPI import...")
    try:
        from fastapi import FastAPI
        print("✅ FastAPI imported successfully!")
        
        app = FastAPI()
        print("✅ FastAPI app created successfully!")
        
        @app.get("/test")
        async def test_endpoint():
            return {"message": "Test successful!"}
            
        print("✅ Test endpoint created successfully!")
        print("\n✅ Environment test passed!")
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    test_environment()
