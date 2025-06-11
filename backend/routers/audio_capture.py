"""
FastAPI router for audio capture and streaming API endpoints.

This module provides WebSocket and REST endpoints for real-time audio level monitoring
and control of the audio capture system.
"""

import asyncio
import json
import logging
import os
from datetime import datetime
from typing import List, Dict, Any, Optional, Callable

from fastapi import APIRouter, HTTPException, WebSocket, WebSocketDisconnect, status
from fastapi.responses import HTMLResponse

from ..audio_capture import AudioCapture, AudioSample, list_audio_devices
from ..config import settings

# Create a router for audio capture endpoints
router = APIRouter(prefix="/audio", tags=["audio"])

# Create a separate router for WebSocket to avoid the /api/v1 prefix
ws_router = APIRouter()

# Configure logging
logger = logging.getLogger(__name__)

# Global audio capture instance
audio_capture: Optional[AudioCapture] = None

# WebSocket connections
active_connections: List[WebSocket] = []

# Audio processing callback
def audio_callback(sample: AudioSample):
    """Process audio samples and broadcast to WebSocket clients."""
    if not audio_capture:
        return
        
    # Prepare data to send
    data = {
        "type": "audio_level",
        "timestamp": sample.timestamp.isoformat(),
        "rms": sample.rms,
        "db": sample.db,
        "sample_rate": sample.sample_rate,
        "channels": audio_capture.channels
    }
    
    # Broadcast to all connected WebSocket clients
    disconnected = []
    for connection in active_connections:
        try:
            asyncio.create_task(connection.send_json(data))
        except Exception as e:
            logger.warning(f"Error sending to WebSocket, will disconnect: {e}")
            disconnected.append(connection)
    
    # Clean up disconnected clients
    for connection in disconnected:
        if connection in active_connections:
            active_connections.remove(connection)

async def start_audio_capture() -> bool:
    """Initialize and start the audio capture system."""
    global audio_capture
    
    if audio_capture and audio_capture.is_running():
        logger.warning("Audio capture is already running")
        return True
    
    try:
        # Stop existing capture if any
        if audio_capture:
            await stop_audio_capture()
        
        # Create new audio capture instance
        audio_capture = AudioCapture(
            sample_rate=settings.AUDIO_SAMPLE_RATE,
            channels=settings.AUDIO_CHANNELS,
            block_size=settings.AUDIO_BLOCK_SIZE,
            device=settings.AUDIO_DEVICE
        )
        
        # Start capture with callback
        audio_capture.start(callback=audio_callback)
        logger.info(f"Audio capture started on device {settings.AUDIO_DEVICE}")
        return True
        
    except AudioDeviceError as e:
        logger.error(f"Audio device error: {e}")
        return False
    except Exception as e:
        logger.error(f"Failed to start audio capture: {e}", exc_info=True)
        return False

async def stop_audio_capture() -> bool:
    """Stop the audio capture system."""
    global audio_capture
    
    if not audio_capture:
        return True
    
    try:
        audio_capture.stop()
        logger.info("Audio capture stopped")
        return True
    except Exception as e:
        logger.error(f"Error stopping audio capture: {e}", exc_info=True)
        return False

@ws_router.websocket("/ws/audio")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for real-time audio level streaming.
    
    Clients will receive JSON messages with the following format:
    {
        "type": "status" | "audio_level" | "error",
        "message": string,  # Optional status/error message
        "timestamp": "ISO-8601 timestamp",
        "rms": float,  # RMS value (0.0 to 1.0)
        "db": float,   # dBFS value (-inf to 0)
        "sample_rate": int,
        "channels": int,
        "device": string  # Device name/ID
    }
    """
    logger.info("WebSocket connection attempt")
    
    try:
        # Log client information
        client = f"{websocket.client.host}:{websocket.client.port}" if websocket.client else "unknown client"
        logger.info(f"New WebSocket connection from {client}")
        
        # Log headers for debugging
        headers = dict(websocket.headers)
        logger.info(f"WebSocket headers: {headers}")
        
        # Accept the WebSocket connection
        logger.info("Accepting WebSocket connection...")
        await websocket.accept()
        logger.info("WebSocket connection accepted")
        
        # Add to active connections
        active_connections.append(websocket)
        logger.info(f"New WebSocket connection. Active connections: {len(active_connections)}")
        
        # Send initial status
        status_msg = {
            "type": "status",
            "message": "Connected to audio stream",
            "timestamp": datetime.utcnow().isoformat()
        }
        await websocket.send_json(status_msg)
        logger.info(f"Sent initial status: {status_msg}")
        
        # Handle incoming messages
        while True:
            try:
                # Wait for a message from the client
                data = await websocket.receive_text()
                logger.info(f"Received message: {data}")
                
                try:
                    message = json.loads(data)
                    message_type = message.get("type")
                    
                    if message_type == "get_devices":
                        # List available audio devices
                        devices = list_audio_devices()
                        response = {
                            "type": "devices",
                            "devices": devices,
                            "timestamp": datetime.utcnow().isoformat()
                        }
                        await websocket.send_json(response)
                        logger.info(f"Sent devices list: {devices}")
                        
                except json.JSONDecodeError as e:
                    logger.error(f"Error parsing message: {e}")
                    await websocket.send_json({
                        "type": "error",
                        "message": f"Invalid JSON: {e}",
                        "timestamp": datetime.utcnow().isoformat()
                    })
                    
            except WebSocketDisconnect as e:
                logger.info(f"WebSocket disconnected: {e}")
                break
                
            except Exception as e:
                logger.error(f"WebSocket error: {e}", exc_info=True)
                await websocket.send_json({
                    "type": "error",
                    "message": f"Internal server error: {str(e)}",
                    "timestamp": datetime.utcnow().isoformat()
                })
                break
                
    except Exception as e:
        logger.error(f"WebSocket connection error: {e}", exc_info=True)
        
    finally:
        # Remove from active connections
        if websocket in active_connections:
            active_connections.remove(websocket)
            logger.info(f"WebSocket connection closed. Active connections: {len(active_connections)}")
    
    try:
        # Start audio capture if not already running
        if not audio_capture or not audio_capture.is_running():
            logger.info("Starting audio capture...")
            if not await start_audio_capture():
                error_msg = "Failed to start audio capture"
                logger.error(error_msg)
                await websocket.close(code=status.WS_1013_TRY_AGAIN_LATER, reason=error_msg)
                return
        
        # Send initial status with audio capture details
        if audio_capture:
            device_info = audio_capture.get_device_info() or {}
            status_msg = {
                "type": "status",
                "message": "Connected to audio stream",
                "sample_rate": audio_capture.sample_rate,
                "channels": audio_capture.channels,
                "device": device_info.get('name', str(audio_capture.device)),
                "timestamp": datetime.utcnow().isoformat()
            }
            await websocket.send_json(status_msg)
            logger.info(f"Sent initial status: {status_msg}")
        
        # Keep connection alive and handle incoming messages
        while True:
            try:
                # Handle any incoming messages (e.g., control commands)
                data = await asyncio.wait_for(
                    websocket.receive_text(),
                    timeout=1.0
                )
                try:
                    message = json.loads(data)
                    if message.get("type") == "ping":
                        await websocket.send_json({"type": "pong"})
                    elif message.get("type") == "get_devices":
                        # Get list of available audio devices
                        try:
                            devices = list_audio_devices()
                            await websocket.send_json({
                                "type": "devices",
                                "devices": devices,
                                "default_device": settings.AUDIO_DEVICE,
                                "timestamp": datetime.utcnow().isoformat()
                            })
                            logger.info(f"Sent {len(devices)} audio devices to client")
                        except Exception as e:
                            logger.error(f"Error getting audio devices: {e}", exc_info=True)
                            await websocket.send_json({
                                "type": "error",
                                "message": f"Failed to get audio devices: {str(e)}",
                                "timestamp": datetime.utcnow().isoformat()
                            })
                except json.JSONDecodeError:
                    logger.warning(f"Received invalid JSON: {data}")
                    await websocket.send_json({
                        "type": "error",
                        "message": "Invalid JSON received",
                        "timestamp": datetime.utcnow().isoformat()
                    })
                
            except asyncio.TimeoutError:
                # Send periodic pings to keep the connection alive
                await websocket.send_json({"type": "ping"})
            
    except WebSocketDisconnect:
        logger.info("WebSocket client disconnected")
    except Exception as e:
        logger.error(f"WebSocket error: {e}", exc_info=True)
    finally:
        if websocket in active_connections:
            active_connections.remove(websocket)
            logger.info(f"WebSocket disconnected. Active connections: {len(active_connections)}")
        
        # Stop audio capture if no more clients
        if not active_connections and audio_capture and audio_capture.is_running():
            await stop_audio_capture()

@router.get("/devices", response_model=Dict[str, Any])
async def list_audio_devices_route():
    """
    List all available audio input devices.
    
    Returns:
        Dictionary with list of available audio input devices
    """
    try:
        devices = list_audio_devices()
        return {
            "status": "success",
            "devices": devices,
            "default_device": settings.AUDIO_DEVICE
        }
    except Exception as e:
        logger.error(f"Error listing audio devices: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "status": "error",
                "message": "Failed to list audio devices",
                "error": str(e)
            }
        )

@router.get("/status", response_model=Dict[str, Any])
async def get_audio_status():
    """
    Get audio capture status and configuration.
    
    Returns:
        Dictionary with current audio capture status and settings
    """
    device_info = {}
    if audio_capture:
        device_info = audio_capture.get_device_info() or {}
    
    return {
        "status": "success",
        "is_running": bool(audio_capture and audio_capture.is_running()),
        "sample_rate": audio_capture.sample_rate if audio_capture else settings.AUDIO_SAMPLE_RATE,
        "channels": audio_capture.channels if audio_capture else settings.AUDIO_CHANNELS,
        "active_connections": len(active_connections),
        "device": audio_capture.device if audio_capture else settings.AUDIO_DEVICE,
        "device_name": device_info.get('name', 'Not available'),
        "block_size": settings.AUDIO_BLOCK_SIZE
    }

@router.get("/level", response_model=Dict[str, Any])
async def get_audio_level():
    """
    Get current audio level in dBFS.
    
    Returns:
        Dictionary with current audio level information
    """
    if not audio_capture or not audio_capture.is_running():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "status": "error",
                "message": "Audio capture is not running"
            }
        )
    
    level = audio_capture.get_current_level()
    if level is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "status": "error",
                "message": "No audio level available"
            }
        )
    
    return {
        "status": "success",
        "level_db": level.db,
        "rms": level.rms,
        "timestamp": level.timestamp.isoformat(),
        "sample_rate": level.sample_rate
    }

@router.post("/start", response_model=Dict[str, Any])
async def start_capture():
    """
    Start audio capture.
    
    Returns:
        Dictionary with operation status
    """
    if await start_audio_capture():
        return {
            "status": "success",
            "message": "Audio capture started"
        }
    else:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "status": "error",
                "message": "Failed to start audio capture"
            }
        )

@router.post("/stop", response_model=Dict[str, Any])
async def stop_capture():
    """
    Stop audio capture.
    
    Returns:
        Dictionary with operation status
    """
    if not audio_capture or not audio_capture.is_running():
        return {
            "status": "success",
            "message": "Audio capture was not running"
        }
    
    if await stop_audio_capture():
        return {
            "status": "success",
            "message": "Audio capture stopped"
        }
    else:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "status": "error",
                "message": "Error stopping audio capture"
            }
        )

# Cleanup on application shutdown
@ws_router.on_event("shutdown")
async def shutdown_event():
    """Clean up resources on application shutdown."""
    if audio_capture and audio_capture.is_running():
        audio_capture.stop()
        logger.info("Audio capture stopped on application shutdown")
