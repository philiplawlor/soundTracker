@echo off
REM Batch file to start backend (FastAPI) and frontend (Flutter)

REM Check if Python is installed
python --version >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo Python is not installed or not in PATH. Please install Python 3.8 or later.
    exit /b 1
)

REM Check if Flutter is installed
flutter --version >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo Flutter is not installed or not in PATH. Please install Flutter.
    exit /b 1
)

REM Change to project directory
cd /d %~dp0

REM Check if backend venv exists, if not create it
if not exist "backend\venv\Scripts\activate.bat" (
    echo Creating Python virtual environment...
    python -m venv backend\venv
    if %ERRORLEVEL% NEQ 0 (
        echo Failed to create virtual environment
        exit /b 1
    )
)

REM Install dependencies if requirements.txt exists
if exist "backend\requirements.txt" (
    echo Installing backend dependencies...
    call backend\venv\Scripts\activate.bat
    
    REM Ensure pip is up to date
    python -m pip install --upgrade pip
    
    REM Install requirements
    pip install -r backend\requirements.txt
    if %ERRORLEVEL% NEQ 0 (
        echo Failed to install backend dependencies
        exit /b 1
    )
    
    REM Install uvicorn explicitly if not already installed
    pip list | findstr "uvicorn" >nul
    if %ERRORLEVEL% NEQ 0 (
        echo Installing uvicorn...
        pip install uvicorn[standard]
        if %ERRORLEVEL% NEQ 0 (
            echo Failed to install uvicorn
            exit /b 1
        )
    )
    
    deactivate
)

REM Start backend server with logging
echo Starting backend server...

REM First, try to run the backend directly to see any errors
cd /d %~dp0backend
call venv\Scripts\activate.bat

REM Check if main.py exists
if not exist "main.py" (
    echo Error: main.py not found in the backend directory
    dir /b
    exit /b 1
)

REM Run the backend and log output
start "Backend" cmd /k "cd /d %~dp0backend && call venv\Scripts\activate.bat && echo Starting backend... && python -c "import uvicorn; uvicorn.run('main:app', host='0.0.0.0', port=8000, reload=True)" 2>&1 > backend.log"

REM Wait a moment for the server to start
timeout /t 2 >nul

REM Check if the server is running
tasklist /FI "WINDOWTITLE eq Backend" | findstr /i "cmd" >nul
if %ERRORLEVEL% NEQ 0 (
    echo Error: Backend failed to start. Check backend.log for details.
    type backend.log 2>nul || echo No log file found.
    exit /b 1
)

cd /d %~dp0

REM Start Flutter frontend (Web on port 3030)
start "Frontend" cmd /k "cd /d %~dp0frontend && flutter run -d chrome --web-port=3030"

echo SoundTracker is starting...
echo Backend: http://localhost:8000
echo Backend API Docs: http://localhost:8000/docs
echo Frontend: Check the Flutter application window

exit /b 0
