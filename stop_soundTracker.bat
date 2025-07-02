@echo off
REM ===========================================================================
REM SoundTracker Stop Script for Windows
REM This script stops all backend and frontend processes for the SoundTracker app
REM ===========================================================================

setlocal enabledelayedexpansion

:: Colors for output
set "RED=31"
set "GREEN=32"
set "YELLOW=33"
set "NC=0"

:: Function to print colored text
:color_echo
    set "color=%~1"
    set "message=%~2"
    echo [%time%] %message%
    echo.
exit /b 0

:: Main script
call :color_echo %YELLOW% "[*] Stopping SoundTracker..."

:: Stop backend processes
call :color_echo %YELLOW% "[*] Stopping backend processes..."

:: Kill processes on port 8000 (FastAPI)
for /f "tokens=5" %%a in ('netstat -ano ^| findstr ":8000 " ^| findstr "LISTENING"') do (
    call :color_echo %GREEN% "[+] Stopping FastAPI server (PID: %%a)"
    taskkill /F /PID %%a >nul 2>&1
)

:: Kill any Python processes running the FastAPI app
for /f "tokens=2 delims=:" %%a in ('tasklist /FI "IMAGENAME eq python.exe" /FO LIST ^| findstr "PID:"') do (
    for /f "tokens=*" %%b in ('wmic process where "(ProcessId=%%~a)" get CommandLine 2^>nul ^| findstr /i "main:app"') do (
        call :color_echo %GREEN% "[+] Stopping Python process (PID: %%~a)"
        taskkill /F /PID %%~a >nul 2>&1
    )
)

:: Stop frontend processes
call :color_echo %YELLOW% "[*] Stopping frontend processes..."

:: Kill Flutter/Dart processes
for /f "tokens=2 delims=:" %%a in ('tasklist /FI "IMAGENAME eq dart.exe" /FO LIST ^| findstr "PID:"') do (
    call :color_echo %GREEN% "[+] Stopping Dart process (PID: %%~a)"
    taskkill /F /PID %%~a >nul 2>&1
)

for /f "tokens=2 delims=:" %%a in ('tasklist /FI "IMAGENAME eq flutter_console.exe" /FO LIST ^| findstr "PID:"') do (
    call :color_echo %GREEN% "[+] Stopping Flutter process (PID: %%~a)"
    taskkill /F /PID %%~a >nul 2>&1
)

:: Kill any remaining processes on common Flutter/Node ports
for %%i in (3000 3001 3002 3003 3004 3005 5000 5001 5002 5003 5004 5005 8000 8001 8002 8003 8004 8005 8080 8081 8082 8083 8084 8085 8888 9000 9001 9002 9003 9004 9005 50300 50301 50302 50303 50304 50305) do (
    for /f "tokens=5" %%a in ('netstat -ano ^| findstr ":%%i " ^| findstr "LISTENING"') do (
        call :color_echo %GREEN% "[+] Killing process on port %%i (PID: %%a)"
        taskkill /F /PID %%a >nul 2>&1
    )
)

:: Check for running processes
set "processes_running=0"

:: Check for remaining Python processes
tasklist /FI "IMAGENAME eq python.exe" | findstr /I "python" >nul
if not errorlevel 1 (
    call :color_echo %RED% "[WARNING] Some Python processes are still running"
    set "processes_running=1"
)

:: Check for remaining Dart processes
tasklist /FI "IMAGENAME eq dart.exe" | findstr /I "dart" >nul
if not errorlevel 1 (
    call :color_echo %RED% "[WARNING] Some Dart processes are still running"
    set "processes_running=1"
)

:: Final status
if "%processes_running%"=="0" (
    call :color_echo %GREEN% "[+] All SoundTracker processes have been stopped"
) else (
    call :color_echo %RED% "[WARNING] Some processes might still be running. Please check manually."
)

call :color_echo %GREEN% "[+] Done!"

:: Pause to show output
pause
exit /b 0
