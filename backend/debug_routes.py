"""Debug script to inspect FastAPI application and routes."""
import sys
import inspect
from pathlib import Path

# Add the backend directory to the Python path
BACKEND_DIR = Path(__file__).parent.absolute()
sys.path.append(str(BACKEND_DIR))

print(f"Python path: {sys.path}\n")

# Import the FastAPI app
try:
    from main import app
    print("✅ Successfully imported FastAPI app from main.py")
except Exception as e:
    print(f"❌ Failed to import FastAPI app: {e}")
    sys.exit(1)

def get_route_info(route):
    """Extract route information."""
    info = {
        "path": getattr(route, "path", "N/A"),
        "name": getattr(route, "name", "N/A"),
        "methods": ", ".join(sorted(route.methods)) if hasattr(route, "methods") else "N/A",
        "endpoint": "N/A",
        "type": type(route).__name__
    }
    
    if hasattr(route, "endpoint"):
        if hasattr(route.endpoint, "__name__"):
            info["endpoint"] = route.endpoint.__name__
        else:
            info["endpoint"] = str(route.endpoint)
    
    return info

def list_routes():
    """List all registered routes in the FastAPI application."""
    if not hasattr(app, "routes"):
        print("❌ No 'routes' attribute found on the app")
        return
    
    print(f"\n=== Registered API Routes ({len(app.routes)} total) ===\n")
    
    for i, route in enumerate(app.routes, 1):
        info = get_route_info(route)
        print(f"{i}. {info['methods']: <15} {info['path']}")
        print(f"   ├─ Type: {info['type']}")
        print(f"   ├─ Name: {info['name']}")
        print(f"   └─ Endpoint: {info['endpoint']}\n")

def inspect_app():
    """Inspect the FastAPI app object."""
    print("\n=== FastAPI App Inspection ===\n")
    
    # Basic app info
    print(f"App title: {app.title}")
    print(f"Description: {app.description}")
    print(f"Version: {app.version}")
    print(f"Debug: {app.debug}")
    
    # Check for routers
    if hasattr(app, "router"):
        print("\nRouters:")
        for route in app.router.routes:
            print(f"- {route.path} ({', '.join(route.methods) if hasattr(route, 'methods') else 'No methods'})")
    
    # Check for mounted apps
    if hasattr(app, "mounts"):
        print("\nMounted apps:")
        for path, mounted_app in app.mounts.items():
            print(f"- {path} -> {mounted_app}")

if __name__ == "__main__":
    print("\n" + "="*80)
    print("DEBUGGING FASTAPI APP")
    print("="*80)
    
    # Inspect the app
    inspect_app()
    
    # List all routes
    list_routes()
    
    print("\nDebugging complete!")
    print("="*80)
