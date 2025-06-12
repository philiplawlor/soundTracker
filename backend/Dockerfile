# Use official Python 3.11 image
FROM python:3.11-slim

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=off \
    PIP_DISABLE_PIP_VERSION_CHECK=on \
    PIP_DEFAULT_TIMEOUT=100 \
    POETRY_VERSION=1.3.2

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libsndfile1 \
    portaudio19-dev \
    python3-dev \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements and install with pinned versions
COPY requirements.txt .

# Install pip packages with specific versions
RUN pip install --upgrade pip && \
    pip install --no-cache-dir \
    uvicorn==0.22.0 \
    fastapi==0.95.0 \
    python-multipart==0.0.6 \
    python-dotenv==1.0.0 \
    numpy==1.24.3 \
    sounddevice==0.4.6 \
    pydub==0.25.1 \
    librosa==0.10.1 \
    resampy==0.3.1 \
    soundfile==0.12.1 \
    tensorflow==2.12.0 \
    tensorflow-hub==0.13.0 \
    tensorflow-io==0.31.0

# Copy the rest of the application
COPY . .

# Expose the port the app runs on
EXPOSE 8001

# Command to run the application
CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8001", "--reload"]
