@echo off
setlocal

echo Setting up SoundTracker backend...

:: Set Python path
set PYTHONPATH=%~dp0src

:: Activate virtual environment
call venv\Scripts\activate.bat
if %ERRORLEVEL% NEQ 0 (
    echo Failed to activate virtual environment
    pause
    exit /b 1
)

echo Installing dependencies...
pip install -r requirements.txt
if %ERRORLEVEL% NEQ 0 (
    echo Failed to install dependencies
    pause
    exit /b 1
)

echo Starting backend server...
python -m uvicorn src.backend.main:app --host 0.0.0.0 --port 8000 --reload

pause
