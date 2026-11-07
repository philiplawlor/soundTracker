@echo off
REM Batch file to start backend (FastAPI) and frontend (Flutter)

REM Change to project directory
cd /d %~dp0

REM Create logs directory if it doesn't exist
if not exist "logs" mkdir logs

REM Check if Python is installed
python --version >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo Python is not installed or not in PATH. Please install Python 3.8 or later.
    echo.
    pause
    exit /b 1
)

REM Check if Flutter is installed
flutter --version >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo Flutter is not installed or not in PATH. Please install Flutter.
    echo.
    pause
    exit /b 1
)

REM Check if venv exists, if not create it
if not exist "venv\Scripts\activate.bat" (
    echo Creating Python virtual environment...
    python -m venv venv
    if %ERRORLEVEL% NEQ 0 (
        echo Failed to create virtual environment
        echo.
        pause
        exit /b 1
    )
    
    echo Installing backend dependencies...
    call venv\Scripts\activate.bat
    
    REM Ensure pip is up to date
    python -m pip install --upgrade pip
    
    REM Install requirements if exists
    if exist "requirements.txt" (
        pip install -r requirements.txt
        if %ERRORLEVEL% NEQ 0 (
            echo Failed to install backend dependencies
            echo.
            pause
            exit /b 1
        )
    )
    
    REM Install required packages
    echo Installing required Python packages...
    pip install uvicorn[standard] fastapi python-dotenv sounddevice numpy websockets
    if %ERRORLEVEL% NEQ 0 (
        echo Failed to install required packages
        echo.
        pause
        exit /b 1
    )
    
    deactivate
)

REM Start backend server with logging
echo.
echo ===================================================
echo Starting Backend Server...
echo ===================================================

REM Set PYTHONPATH to include the project root
set PYTHONPATH=%~dp0

REM Activate venv and start the backend with the correct module path
start "Backend" cmd /k "@echo off && title Backend && cd /d %~dp0 && call venv\Scripts\activate.bat && set PYTHONPATH=%~dp0 && echo Starting backend server... && python -m uvicorn src.backend.main:app --host 0.0.0.0 --port 8000 --reload && pause"

REM Wait a moment for the server to start
timeout /t 5 >nul

REM Check if the server is running
netstat -ano | findstr :8000 >nul
if %ERRORLEVEL% NEQ 0 (
    echo Error: Backend failed to start on port 8000.
    echo Please check the backend window for error messages.
    echo.
    pause
    exit /b 1
)

REM Start Flutter frontend
echo.
echo ===================================================
echo Starting Flutter Frontend...
echo ===================================================
echo.

start "Flutter Frontend" cmd /k "@echo off && title Flutter Frontend && cd /d %~dp0frontend && echo Installing Flutter dependencies... && flutter pub get && echo Starting Flutter dev server... && flutter run -d chrome --web-port 3030"

REM Create stop script
echo @echo off > stop_soundTracker.bat
echo echo Stopping SoundTracker... >> stop_soundTracker.bat
echo taskkill /F /FI "WINDOWTITLE eq Backend" /T >> stop_soundTracker.bat
echo taskkill /F /FI "WINDOWTITLE eq Flutter Frontend" /T >> stop_soundTracker.bat
echo del "%%~f0" >> stop_soundTracker.bat
echo echo Stopped SoundTracker >> stop_soundTracker.bat

echo.
echo ===================================================
echo SoundTracker is running!
echo.
echo Backend:      http://localhost:8000
echo API Docs:     http://localhost:8000/docs
echo Frontend:     http://localhost:3030
echo.
echo To stop the application, run: stop_soundTracker.bat
echo ===================================================
echo.

REM Keep the window open
pause

exit /b 0
