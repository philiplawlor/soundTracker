#!/bin/bash

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Function to check if a process is running
is_running() {
    pgrep -f "$1" > /dev/null
}

# Function to start the backend
start_backend() {
    echo -e "${YELLOW}Starting FastAPI backend...${NC}"
    if ! is_running "uvicorn backend.main:app"; then
        source venv/bin/activate
        nohup python -m uvicorn backend.main:app --reload --port 8001 > backend.log 2>&1 &
        echo $! > backend.pid
        echo -e "${GREEN}Backend started on http://localhost:8001${NC}"
    else
        echo -e "${YELLOW}Backend is already running${NC}"
    fi
}

# Function to start the frontend
start_frontend() {
    echo -e "${YELLOW}Starting Flutter frontend...${NC}"
    if ! is_running "flutter run -d chrome"; then
        cd frontend
        nohup flutter run -d chrome > ../frontend.log 2>&1 &
        echo $! > ../frontend.pid
        cd ..
        echo -e "${GREEN}Frontend started in Chrome${NC}"
    else
        echo -e "${YELLOW}Frontend is already running${NC}"
    fi
}

# Function to stop the backend
stop_backend() {
    echo -e "${YELLOW}Stopping FastAPI backend...${NC}"
    if [ -f "backend.pid" ]; then
        kill $(cat backend.pid) 2>/dev/null || true
        rm -f backend.pid
    fi
    pkill -f "uvicorn backend.main:app" 2>/dev/null || true
    echo -e "${GREEN}Backend stopped${NC}"
}

# Function to stop the frontend
stop_frontend() {
    echo -e "${YELLOW}Stopping Flutter frontend...${NC}"
    if [ -f "frontend.pid" ]; then
        kill $(cat frontend.pid) 2>/dev/null || true
        rm -f frontend.pid
    fi
    pkill -f "flutter run -d chrome" 2>/dev/null || true
    echo -e "${GREEN}Frontend stopped${NC}"
}

# Function to show status
status() {
    echo -e "\n${YELLOW}=== Application Status ===${NC}"
    
    if is_running "uvicorn backend.main:app"; then
        echo -e "Backend:  ${GREEN}Running${NC} (http://localhost:8001)"
    else
        echo -e "Backend:  ${RED}Stopped${NC}"
    fi
    
    if is_running "flutter run -d chrome"; then
        echo -e "Frontend: ${GREEN}Running${NC} (Chrome)"
    else
        echo -e "Frontend: ${RED}Stopped${NC}"
    fi
    echo -e "${YELLOW}========================${NC}"
}

# Main script logic
case "$1" in
    start)
        start_backend
        start_frontend
        status
        ;;
    stop)
        stop_frontend
        stop_backend
        status
        ;;
    restart)
        stop_frontend
        stop_backend
        start_backend
        start_frontend
        status
        ;;
    status)
        status
        ;;
    *)
        echo "Usage: $0 {start|stop|restart|status}"
        exit 1
        ;;
esac

exit 0
