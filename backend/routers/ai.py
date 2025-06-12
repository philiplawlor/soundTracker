from fastapi import APIRouter, UploadFile, File, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.responses import JSONResponse
from typing import List, Optional
import json
import logging

from ..ai import identify_sound, sound_classifier
from ..schemas import AISoundIdentifyResponse, AISoundClassifyResponse, AISoundClassifyRequest

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/ai", tags=["AI"])

@router.post("/identify", response_model=AISoundIdentifyResponse)
async def identify_endpoint(file: UploadFile = File(...)):
    """
    Identify the sound in the uploaded audio file.
    
    Accepts WAV audio files and returns the most likely sound class.
    """
    if not file.content_type or not any(x in file.content_type for x in ["wav", "wave"]):
        raise HTTPException(
            status_code=400, 
            detail="Only WAV audio files are supported. Please upload a .wav file."
        )
    
    try:
        audio_bytes = await file.read()
        if not audio_bytes:
            raise HTTPException(status_code=400, detail="Uploaded file is empty")
            
        label = identify_sound(audio_bytes)
        if label.startswith("error:"):
            raise HTTPException(status_code=400, detail=label[7:])
            
        return AISoundIdentifyResponse(label=label)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error processing audio file: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500, 
            detail=f"Error processing audio file: {str(e)}"
        )

@router.post("/classify", response_model=AISoundClassifyResponse)
async def classify_sound(
    request: AISoundClassifyRequest
) -> AISoundClassifyResponse:
    """
    Classify sound from audio data and return top-k predictions with confidence scores.
    
    Args:
        request: AISoundClassifyRequest containing the audio data and optional top_k parameter
        
    Returns:
        AISoundClassifyResponse with the classification results
    """
    try:
        if not request.audio_data:
            raise HTTPException(status_code=400, detail="No audio data provided")
            
        # Validate audio data size (max 10MB)
        if len(request.audio_data) > 10 * 1024 * 1024:  # 10MB
            raise HTTPException(status_code=400, detail="Audio file too large. Maximum size is 10MB.")
        
        # Get top-k predictions
        top_k = min(max(1, request.top_k or 5), 10)  # Clamp between 1 and 10
        predictions = sound_classifier.classify_sound(request.audio_data, top_k=top_k)
        
        return AISoundClassifyResponse(
            success=True,
            predictions=predictions,
            message="Sound classification completed successfully"
        )
        
    except Exception as e:
        logger.error(f"Error in sound classification: {str(e)}", exc_info=True)
        return AISoundClassifyResponse(
            success=False,
            predictions=[],
            message=f"Error during sound classification: {str(e)}"
        )

@router.websocket("/ws/classify")
async def websocket_classify(websocket: WebSocket):
    """
    WebSocket endpoint for real-time sound classification.
    
    Expected message format:
    {
        "type": "classify",
        "audio_data": "base64_encoded_audio_data",
        "top_k": 3  // optional, default is 3
    }
    """
    await websocket.accept()
    logger.info("WebSocket connection for sound classification established")
    
    try:
        while True:
            # Receive message from client
            data = await websocket.receive_text()
            
            try:
                message = json.loads(data)
                if message.get("type") != "classify":
                    await websocket.send_json({
                        "type": "error",
                        "message": "Invalid message type. Expected 'classify'"
                    })
                    continue
                    
                audio_data = message.get("audio_data")
                if not audio_data:
                    await websocket.send_json({
                        "type": "error",
                        "message": "No audio_data provided in the message"
                    })
                    continue
                
                # Decode base64 audio data
                import base64
                try:
                    audio_bytes = base64.b64decode(audio_data)
                except Exception as e:
                    await websocket.send_json({
                        "type": "error",
                        "message": f"Failed to decode audio data: {str(e)}"
                    })
                    continue
                
                # Classify sound
                top_k = min(max(1, message.get("top_k", 3)), 10)
                predictions = sound_classifier.classify_sound(audio_bytes, top_k=top_k)
                
                # Send response
                await websocket.send_json({
                    "type": "classification_result",
                    "success": True,
                    "predictions": predictions
                })
                
            except json.JSONDecodeError:
                await websocket.send_json({
                    "type": "error",
                    "message": "Invalid JSON format"
                })
            except Exception as e:
                logger.error(f"Error in WebSocket classification: {str(e)}", exc_info=True)
                await websocket.send_json({
                    "type": "error",
                    "message": f"Error processing request: {str(e)}"
                })
                
    except WebSocketDisconnect:
        logger.info("WebSocket connection for sound classification closed")
    except Exception as e:
        logger.error(f"WebSocket error: {str(e)}", exc_info=True)
    finally:
        try:
            await websocket.close()
        except:
            pass
