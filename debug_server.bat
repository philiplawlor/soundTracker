@echo on

echo Current directory:
cd

echo.
echo Python version:
python --version

echo.
echo Flutter version:
flutter --version

echo.
echo Setting up Python virtual environment...
python -m venv venv
call venv\Scripts\activate.bat

pip install --upgrade pip
pip install uvicorn[standard] fastapi python-dotenv sounddevice numpy websockets

echo.
echo Starting backend server...
set PYTHONPATH=%CD%
python -m uvicorn src.backend.main:app --host 0.0.0.0 --port 8000 --reload

pause
