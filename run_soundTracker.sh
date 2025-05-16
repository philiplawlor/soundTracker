#!/bin/bash
# Bash script to start backend (FastAPI) and frontend (Flutter)

# Start backend (assumes venv is in backend/venv)
cd backend
source venv/bin/activate
uvicorn main:app --reload --port 8000 &
BACKEND_PID=$!
cd ..

# Start frontend (desktop)
cd frontend
flutter run -d windows &
FRONTEND_PID=$!
cd ..

echo "Backend PID: $BACKEND_PID"
echo "Frontend PID: $FRONTEND_PID"

echo "To stop, run ./stop_backend_frontend.sh"
