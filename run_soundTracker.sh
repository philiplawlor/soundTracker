#!/bin/bash
# Bash script to start backend (FastAPI) and frontend (Flutter)

# Exit on error
set -e

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Function to display error messages
error_exit() {
    echo -e "${RED}Error: $1${NC}" >&2
    exit 1
}

# Function to check if a command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

echo -e "${YELLOW}Checking system requirements...${NC}"

# Check if Python is installed
if ! command_exists python3; then
    error_exit "Python 3.8 or later is required but not installed. Please install Python first."
fi

# Check if Flutter is installed
if ! command_exists flutter; then
    error_exit "Flutter is required but not installed. Please install Flutter first."
fi

# Get the directory of this script
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

# Create logs directory if it doesn't exist
mkdir -p logs

# Backend setup
echo -e "\n${YELLOW}Setting up backend...${NC}"

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "Creating Python virtual environment..."
    python3 -m venv venv || error_exit "Failed to create virtual environment"
    
    echo "Installing backend dependencies..."
    source venv/bin/activate
    pip install --upgrade pip
    
    # Install requirements if exists
    if [ -f "requirements.txt" ]; then
        pip install -r requirements.txt || error_exit "Failed to install requirements"
    fi
    
    # Install required packages
    pip install uvicorn[standard] fastapi python-dotenv sounddevice numpy websockets || \
        error_exit "Failed to install required packages"
    
    deactivate
fi

# Start backend server
echo -e "\n${YELLOW}Starting backend server...${NC}"
source venv/bin/activate
python -m uvicorn src.main:app --host 0.0.0.0 --port 8000 --reload > logs/backend.log 2>&1 &
BACKEND_PID=$!

# Wait a moment for the server to start
sleep 2

# Check if the server is running
if ! ps -p $BACKEND_PID > /dev/null; then
    echo -e "${RED}Error: Backend failed to start. Check logs/backend.log for details.${NC}"
    tail -n 20 logs/backend.log 2>/dev/null || echo "No log file found."
    exit 1
fi

# Frontend setup
echo -e "\n${YELLOW}Setting up frontend...${NC}"
cd frontend

# Install Flutter dependencies
echo "Installing Flutter dependencies..."
flutter pub get > ../logs/frontend.log 2>&1 || {
    echo -e "${RED}Error: Failed to install Flutter dependencies${NC}"
    exit 1
}

# Start Flutter frontend on port 3030
echo -e "\n${YELLOW}Starting Flutter frontend on port 3030...${NC}"
flutter run -d chrome --web-port=3030 >> ../logs/frontend.log 2>&1 &
FRONTEND_PID=$!
cd ..

# Create stop script
cat > stop_soundTracker.sh <<EOL
#!/bin/bash
echo "Stopping SoundTracker..."
kill $BACKEND_PID $FRONTEND_PID 2>/dev/null
rm -f "$PWD/stop_soundTracker.sh"
echo "Stopped SoundTracker"
EOL
chmod +x stop_soundTracker.sh

# Display status
echo -e "\n${GREEN}===================================================${NC}"
echo -e "${GREEN}SoundTracker is running!${NC}"
echo -e "${GREEN}Backend:${NC}  http://localhost:8000"
echo -e "${GREEN}API Docs:${NC} http://localhost:8000/docs"
echo -e "${GREEN}Frontend:${NC} http://localhost:3030"
echo -e "\n${YELLOW}Logs:${NC}"
echo -e "Backend:  $PWD/logs/backend.log"
echo -e "Frontend: $PWD/logs/frontend.log"
echo -e "\n${YELLOW}To stop the application, run:${NC} ./stop_soundTracker.sh"
echo -e "${GREEN}===================================================${NC}"

# Function to handle cleanup on exit
cleanup() {
    echo -e "\n${YELLOW}Shutting down SoundTracker...${NC}"
    kill $BACKEND_PID $FRONTEND_PID 2>/dev/null
    rm -f "$PWD/stop_soundTracker.sh"
    echo "Stopped SoundTracker"
    exit 0
}

# Set trap to call cleanup function on script exit
trap cleanup INT TERM EXIT

# Wait for all background processes to complete
wait $BACKEND_PID $FRONTEND_PID
