@echo off
setlocal

echo Testing Python environment...
set PYTHON_PATH=C:\Users\phili\AppData\Local\Programs\Python\Python311\python.exe

if not exist "%PYTHON_PATH%" (
    echo Python not found at %PYTHON_PATH%
    pause
    exit /b 1
)

echo Python found at %PYTHON_PATH%
echo Python version:
"%PYTHON_PATH%" --version

echo.
echo Installing dependencies...
"%PYTHON_PATH%" -m pip install fastapi uvicorn
if %ERRORLEVEL% NEQ 0 (
    echo Failed to install dependencies
    pause
    exit /b 1
)

echo.
echo Starting test server...
"%PYTHON_PATH%" test_fastapi.py

pause
