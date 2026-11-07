@echo off
setlocal

echo Setting up SoundTracker backend...

:: Set Python path
set PYTHON_PATH=C:\Users\phili\AppData\Local\Programs\Python\Python311\python.exe
set VENV_PATH=venv

:: Create virtual environment if it doesn't exist
if not exist "%VENV_PATH%" (
    echo Creating virtual environment...
    "%PYTHON_PATH%" -m venv %VENV_PATH%
    if %ERRORLEVEL% NEQ 0 (
        echo Failed to create virtual environment
        pause
        exit /b 1
    )
)

:: Activate virtual environment
call %VENV_PATH%\Scripts\activate.bat
if %ERRORLEVEL% NEQ 0 (
    echo Failed to activate virtual environment
    pause
    exit /b 1
)

echo Installing dependencies...
"%PYTHON_PATH%" -m pip install --upgrade pip
"%PYTHON_PATH%" -m pip install -r requirements.txt
if %ERRORLEVEL% NEQ 0 (
    echo Failed to install dependencies
    pause
    exit /b 1
)

echo Starting backend server...
set PYTHONPATH=%~dp0src
"%PYTHON_PATH%" -m uvicorn src.backend.main:app --host 0.0.0.0 --port 8000 --reload

pause
