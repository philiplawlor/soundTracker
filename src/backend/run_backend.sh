#!/bin/bash
# Activate venv and run backend (Linux/Mac/WSL)

# Get the directory where this script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

# Change to the project root directory
cd "$PROJECT_ROOT"

# Create virtual environment if it doesn't exist
if [ ! -d "backend/.venv" ]; then
  echo "Creating virtual environment..."
  python3 -m venv backend/.venv
  source backend/.venv/bin/activate
  echo "Upgrading pip..."
  pip install --upgrade pip
  echo "Installing requirements..."
  pip install -r backend/requirements.txt
else
  source backend/.venv/bin/activate
fi

# Install in development mode
pip install -e .

# Export PYTHONPATH to include the project root
export PYTHONPATH="$PROJECT_ROOT:$PYTHONPATH"

# Run the FastAPI application
uvicorn backend.main:app --reload --app-dir=.
