@echo off
REM Activate venv and run backend (Windows)
IF NOT EXIST venv (
    python -m venv venv
)
CALL venv\Scripts\activate.bat
pip install -r requirements.txt
uvicorn main:app --reload
