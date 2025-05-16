@echo off
REM Batch file to stop backend and frontend (by killing processes on ports)

REM Stop FastAPI backend (port 8000)
for /f "tokens=5" %%a in ('netstat -ano ^| findstr :8000 ^| findstr LISTENING') do (
    echo Killing backend process PID %%a
    taskkill /PID %%a /F
)

REM Stop Flutter frontend (port 50300+ or search for flutter_tools)
taskkill /IM dart.exe /F
REM Optionally, kill flutter console
REM taskkill /IM flutter_console.exe /F

REM Check ports are free
netstat -ano | findstr :8000
netstat -ano | findstr :50300

pause
