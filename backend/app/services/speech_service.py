"""
Speech Audio Transcription Service.
Supports:
1. Cloud Hosted Whisper Transcription (via OpenAI client if OPENAI_API_KEY is configured)
2. Audio format handling and fallback error reporting.
"""
import io
import logging
from typing import Optional, Dict, Any
from app.core.config import settings

logger = logging.getLogger(__name__)


def transcribe_audio_file(file_bytes: bytes, filename: str = "audio.webm") -> Dict[str, Any]:
    """
    Transcribe audio file bytes using configured cloud speech API.
    If no cloud speech key is provided, returns informative status.
    """
    if not settings.OPENAI_API_KEY or not settings.OPENAI_API_KEY.strip():
        return {
            "success": False,
            "error": "Cloud Speech API is not configured (OPENAI_API_KEY is not set). Please use browser speech recognition or configure an API key.",
            "text": "",
        }

    try:
        from openai import OpenAI
        client = OpenAI(
            api_key=settings.OPENAI_API_KEY,
            base_url=settings.OPENAI_BASE_URL,
        )

        audio_buffer = io.BytesIO(file_bytes)
        audio_buffer.name = filename

        # Whisper automatically detects spoken language (Tamil, Hindi, English, etc.)
        transcript_obj = client.audio.transcriptions.create(
            model="whisper-1",
            file=audio_buffer,
        )

        text = transcript_obj.text.strip()
        return {
            "success": True,
            "text": text,
        }
    except Exception as exc:
        logger.error("Audio transcription failed: %s", exc)
        return {
            "success": False,
            "error": f"Transcription error: {str(exc)}",
            "text": "",
        }
