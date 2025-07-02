#!/bin/bash
# Bash script to start backend (FastAPI) and frontend (Flutter)

# Exit on error
set -e

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${YELLOW}Checking system requirements...${NC}"

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "Python 3.8 or later is required but not installed. Please install Python first."
    exit 1
fi

# Check if Flutter is installed
if ! command -v flutter &> /dev/null; then
    echo "Flutter is required but not installed. Please install Flutter first."
    exit 1
fi

# Get the directory of this script
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

# Backend setup
echo -e "\n${YELLOW}Setting up backend...${NC}"
cd backend

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "Creating Python virtual environment..."
    python3 -m venv venv
    
    echo "Activating virtual environment and installing dependencies..."
    source venv/bin/activate
    pip install --upgrade pip
    pip install -r requirements.txt
    deactivate
fi

# Start backend server
echo -e "\n${YELLOW}Starting backend server...${NC}"
source venv/bin/activate
uvicorn main:app --reload --port 8000 > ../backend.log 2>&1 &
BACKEND_PID=$!
cd ..

# Frontend setup
echo -e "\n${YELLOW}Setting up frontend...${NC}"
cd frontend

# Install Flutter dependencies if needed
if [ ! -d ".dart_tool" ]; then
    echo "Installing Flutter dependencies..."
    flutter pub get
fi

# Start Flutter frontend on port 3030
echo -e "\n${YELLOW}Starting Flutter frontend on port 3030...${NC}"
flutter run -d chrome --web-port=3030 > ../frontend.log 2>&1 &
FRONTEND_PID=$!
cd ..

# Create stop script
echo -e "\n${YELLOW}Creating stop script...${NC}"
cat > stop_soundTracker.sh <<EOL
#!/bin/bash
echo "Stopping SoundTracker..."
kill $BACKEND_PID $FRONTEND_PID 2>/dev/null
rm -f stop_soundTracker.sh
echo "Stopped SoundTracker"
EOL
chmod +x stop_soundTracker.sh

echo -e "\n${GREEN}SoundTracker is running!${NC}"
echo -e "${GREEN}Backend:${NC} http://localhost:8000"
echo -e "${GREEN}API Docs:${NC} http://localhost:8000/docs"
echo -e "${GREEN}Frontend:${NC} http://localhost:3030"
echo -e "\nTo stop the application, run: ./stop_soundTracker.sh"

# Wait for all background processes to complete
wait $BACKEND_PID $FRONTEND_PID
