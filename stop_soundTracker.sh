#!/bin/bash
# Bash script to stop SoundTracker backend and frontend processes

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${YELLOW}[*] Stopping SoundTracker...${NC}"

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Check for required commands
for cmd in lsof pgrep pkill; do
    if ! command_exists "$cmd"; then
        echo -e "${RED}[ERROR] Required command '$cmd' not found. Please install it first.${NC}"
        exit 1
    fi
done

# Stop backend processes
echo -e "\n${YELLOW}[*] Stopping backend processes...${NC}"

# Kill processes on port 8000 (FastAPI)
if PIDS=$(lsof -ti:8000 2>/dev/null); then
    echo -e "${GREEN}[+] Stopping FastAPI server (PIDs: ${PIDS//$'\n'/, })${NC}"
    kill -9 $PIDS 2>/dev/null
fi

# Kill any Python processes running the FastAPI app
PYTHON_PIDS=$(pgrep -f "python.*main:app")
if [ ! -z "$PYTHON_PIDS" ]; then
    echo -e "${GREEN}[+] Stopping Python processes (PIDs: ${PYTHON_PIDS//$'\n'/, })${NC}"
    kill -9 $PYTHON_PIDS 2>/dev/null
fi

# Stop frontend processes
echo -e "\n${YELLOW}[*] Stopping frontend processes...${NC}"

# Kill Flutter/Dart processes
FLUTTER_PIDS=$(pgrep -f 'flutter|dart')
if [ ! -z "$FLUTTER_PIDS" ]; then
    echo -e "${GREEN}[+] Stopping Flutter/Dart processes (PIDs: ${FLUTTER_PIDS//$'\n'/, })${NC}"
    kill -9 $FLUTTER_PIDS 2>/dev/null
fi

# Kill any processes on common Flutter ports (50300-50399)
for port in $(seq 50300 50399); do
    if PIDS=$(lsof -ti:$port 2>/dev/null); then
        echo -e "${GREEN}[+] Stopping process on port $port (PIDs: ${PIDS//$'\n'/, })${NC}"
        kill -9 $PIDS 2>/dev/null
    fi
done

# Verify processes are stopped
echo -e "\n${YELLOW}[*] Verifying processes are stopped...${NC}"

# Check for remaining Python processes
if pgrep -f "python.*main:app" >/dev/null; then
    echo -e "${RED}[WARNING] Some Python processes are still running${NC}"
else
    echo -e "${GREEN}[✓] All backend processes have been stopped${NC}"
fi

# Check for remaining Flutter/Dart processes
if pgrep -f 'flutter|dart' >/dev/null; then
    echo -e "${RED}[WARNING] Some Flutter/Dart processes are still running${NC}"
else
    echo -e "${GREEN}[✓] All frontend processes have been stopped${NC}"
fi

# Check ports
echo -e "\n${YELLOW}[*] Checking ports...${NC}"
for port in 8000 50300 50301 50302; do
    if lsof -i :$port >/dev/null 2>&1; then
        echo -e "${RED}[!] Port $port is still in use:${NC}"
        lsof -i :$port
    else
        echo -e "${GREEN}[✓] Port $port is free${NC}"
    fi
done

echo -e "\n${GREEN}[✓] SoundTracker has been stopped${NC}"
exit 0
