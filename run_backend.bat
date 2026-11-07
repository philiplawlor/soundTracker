@echo off
setlocal

:: Set Python path to the system Python
set PYTHON_PATH=python

:: Create and activate a virtual environment
if not exist "venv" (
    echo Creating virtual environment...
    %PYTHON_PATH% -m venv venv
    if %ERRORLEVEL% NEQ 0 (
        echo Failed to create virtual environment
        pause
        exit /b 1
    )
)

:: Activate the virtual environment
call venv\Scripts\activate.bat
if %ERRORLEVEL% NEQ 0 (
    echo Failed to activate virtual environment
    pause
    exit /b 1
)

echo Installing dependencies...
%PYTHON_PATH% -m pip install --upgrade pip
%PYTHON_PATH% -m pip install fastapi uvicorn[standard] sqlmodel python-multipart python-jose[cryptography] passlib[bcrypt] python-dotenv tensorflow tensorflow-hub librosa numpy
if %ERRORLEVEL% NEQ 0 (
    echo Failed to install dependencies
    pause
    exit /b 1
)

:: Set the PYTHONPATH to include the src directory
set PYTHONPATH=%CD%\src

:: Change to the backend directory
cd src\backend

echo Starting backend server...
%PYTHON_PATH% -c "import uvicorn; uvicorn.run('main:app', host='0.0.0.0', port=8000, reload=True, log_level='debug')"

pause
