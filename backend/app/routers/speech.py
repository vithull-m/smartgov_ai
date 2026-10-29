from fastapi import APIRouter, UploadFile, File, HTTPException
from typing import Dict, Any
from app.services.speech_service import transcribe_audio_file

router = APIRouter(prefix="/api/speech", tags=["Speech"])


@router.post("/transcribe")
async def transcribe(file: UploadFile = File(...)):
    """
    Transcribe audio blob (WebM, WAV, MP3, MP4, M4A) with automatic multilingual language detection.
    """
    contents = await file.read()
    if not contents:
        raise HTTPException(status_code=400, detail="Empty audio file provided")

    result = transcribe_audio_file(contents, filename=file.filename or "audio.webm")
    if not result.get("success"):
        raise HTTPException(status_code=503, detail=result.get("error"))

    return {
        "text": result.get("text"),
        "success": True,
    }
