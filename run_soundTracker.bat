@echo off
REM Batch file to start backend (FastAPI) and frontend (Flutter)

REM Activate backend venv and start FastAPI
start "Backend" cmd /k "cd backend && call venv\Scripts\activate && uvicorn main:app --reload --port 8000"

REM Start Flutter frontend (Windows desktop)
start "Frontend" cmd /k "cd frontend && flutter run -d windows"

exit
