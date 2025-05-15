#!/bin/bash
# Activate venv and run backend (Linux/Mac/WSL)

if [ ! -d "venv" ]; then
  python3 -m venv venv
fi
source venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --reload
