from fastapi import APIRouter, UploadFile, File, HTTPException
from ..ai import identify_sound
from ..schemas import AISoundIdentifyResponse

router = APIRouter(prefix="/ai", tags=["AI"])

@router.post("/identify", response_model=AISoundIdentifyResponse)
def identify_endpoint(file: UploadFile = File(...)):
    if file.content_type not in ["audio/wav", "audio/x-wav", "audio/wave", "audio/vnd.wave"]:
        raise HTTPException(status_code=400, detail="Only WAV audio files are supported.")
    audio_bytes = file.file.read()
    label = identify_sound(audio_bytes)
    return AISoundIdentifyResponse(label=label)
