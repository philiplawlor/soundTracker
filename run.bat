@echo off
setlocal enabledelayedexpansion

:: Check if Python is installed
where python >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo Python is not installed or not in PATH
    exit /b 1
)

:: Check if Flutter is installed
where flutter >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo Flutter is not installed or not in PATH
    exit /b 1
)

:: Function to check if a process is running
:is_running
setlocal
set "command=%~1"
set "pid_file=%~2"
set "is_running=0"

if exist "!pid_file!" (
    for /f "tokens=1" %%i in (!pid_file!) do (
        tasklist /FI "PID eq %%i" 2>nul | findstr /i "%%i" >nul
        if !ERRORLEVEL! EQU 0 set is_running=1
    )
)

if !is_running! EQU 0 (
    tasklist 2>nul | findstr /i "%~1" >nul
    if !ERRORLEVEL! EQU 0 set is_running=1
)

exit /b !is_running!

:: Function to start the backend
:start_backend
call :is_running "python -m uvicorn" backend.pid
if !errorlevel! EQU 1 (
    echo Starting FastAPI backend...
    if not exist "venv\Scripts\activate" (
        echo Virtual environment not found. Creating...
        python -m venv venv
        call venv\Scripts\activate
        pip install -r requirements.txt
    ) else (
        call venv\Scripts\activate
    )
    start "FastAPI Backend" /B cmd /c "python -m uvicorn backend.main:app --reload --port 8001 > backend.log 2>&1 & echo !^! > backend.pid"
    echo Backend started on http://localhost:8001
) else (
    echo Backend is already running
)
exit /b 0

:: Function to start the frontend
:start_frontend
call :is_running "flutter run -d chrome" frontend.pid
if !errorlevel! EQU 1 (
    echo Starting Flutter frontend...
    cd frontend
    start "Flutter Frontend" /B cmd /c "flutter run -d chrome > ..\frontend.log 2>&1 & echo !^! > ..\frontend.pid"
    cd ..
    echo Frontend started in Chrome
) else (
    echo Frontend is already running
)
exit /b 0

:: Function to stop the backend
:stop_backend
echo Stopping FastAPI backend...
if exist backend.pid (
    for /f "tokens=*" %%i in (backend.pid) do (
        taskkill /F /PID %%i >nul 2>&1
    )
    del backend.pid >nul 2>&1
)
taskkill /F /IM python.exe /FI "WINDOWTITLE eq FastAPI Backend" >nul 2>&1
echo Backend stopped
exit /b 0

:: Function to stop the frontend
:stop_frontend
echo Stopping Flutter frontend...
if exist frontend.pid (
    for /f "tokens=*" %%i in (frontend.pid) do (
        taskkill /F /PID %%i >nul 2>&1
    )
    del frontend.pid >nul 2>&1
)
taskkill /F /IM chrome.exe /FI "WINDOWTITLE eq Flutter Frontend" >nul 2>&1
taskkill /F /IM dart.exe >nul 2>&1
echo Frontend stopped
exit /b 0

:: Function to show status
:status
echo.
echo === Application Status ===

call :is_running "python -m uvicorn" backend.pid
if !errorlevel! EQU 1 (
    echo Backend:  Running (http://localhost:8001)
) else (
    echo Backend:  Stopped
)

call :is_running "flutter run -d chrome" frontend.pid
if !errorlevel! EQU 1 (
    echo Frontend: Running (Chrome)
) else (
    echo Frontend: Stopped
)

echo ========================
echo.
exit /b 0

:: Main script logic
if "%~1"=="" (
    echo Usage: %~n0 {start^|stop^|restart^|status}
    exit /b 1
)

if "%~1"=="start" (
    call :start_backend
    call :start_frontend
    call :status
) else if "%~1"=="stop" (
    call :stop_frontend
    call :stop_backend
    call :status
) else if "%~1"=="restart" (
    call :stop_frontend
    call :stop_backend
    call :start_backend
    call :start_frontend
    call :status
) else if "%~1"=="status" (
    call :status
) else (
    echo Invalid command: %~1
    echo Usage: %~n0 {start^|stop^|restart^|status}
    exit /b 1
)

exit /b 0
