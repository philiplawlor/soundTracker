#!/bin/bash
# Bash script to stop backend and frontend (by killing processes on ports)

# Kill backend (FastAPI on port 8000)
PID_BACKEND=$(lsof -ti:8000)
if [ ! -z "$PID_BACKEND" ]; then
  echo "Killing backend PID $PID_BACKEND"
  kill -9 $PID_BACKEND
fi

# Kill Flutter frontend (dart process, common for flutter run)
PID_FRONTEND=$(pgrep -f flutter_tools)
if [ ! -z "$PID_FRONTEND" ]; then
  echo "Killing frontend PID $PID_FRONTEND"
  kill -9 $PID_FRONTEND
fi

# Check ports are free
lsof -i :8000
lsof -i :50300
