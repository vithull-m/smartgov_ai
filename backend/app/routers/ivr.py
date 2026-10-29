from fastapi import APIRouter, Depends, Form, Query, Request, Response, HTTPException
from sqlalchemy.orm import Session
from typing import Optional, List, Dict, Any
from pydantic import BaseModel
from app.core.database import get_db
from app.services.ivr_service import IVRService, IVR_MENUS
from app.models.models import IVRCallLog
import uuid

router = APIRouter(prefix="/api/ivr", tags=["IVRS Helpline"])


class WebCallStartRequest(BaseModel):
    phone_number: Optional[str] = "+919876543210"
    preferred_language: Optional[str] = "en"


class WebCallActionRequest(BaseModel):
    call_sid: str
    digit: Optional[str] = None
    speech_text: Optional[str] = None
    current_step: str


class CallLogOut(BaseModel):
    id: int
    call_sid: str
    caller_phone: Optional[str]
    language: str
    status: str
    duration_seconds: int
    user_transcript: Optional[str]
    bot_response: Optional[str]
    dtmf_digits: Optional[str]
    schemes_mentioned: Optional[str]
    created_at: Any

    class Config:
        from_attributes = True


# ==========================================
# 1. Web Dialer Simulator Endpoints (Browser)
# ==========================================

@router.post("/call/start")
def start_web_call(payload: WebCallStartRequest, db: Session = Depends(get_db)):
    """
    Start an interactive phone call session from the web browser dialer.
    """
    call_sid = f"CA_{uuid.uuid4().hex[:16]}"
    result = IVRService.handle_initial_call(
        call_sid=call_sid,
        caller_phone=payload.phone_number,
        db=db,
    )
    return result


@router.post("/call/action")
def send_web_call_action(payload: WebCallActionRequest, db: Session = Depends(get_db)):
    """
    Process keypress (DTMF) or voice speech from the interactive web dialer.
    """
    result = IVRService.process_step(
        call_sid=payload.call_sid,
        digit=payload.digit,
        speech_text=payload.speech_text,
        current_step=payload.current_step,
        db=db,
    )
    return result


@router.get("/logs", response_model=List[CallLogOut])
def get_call_logs(limit: int = 15, db: Session = Depends(get_db)):
    """
    Retrieve call records and history for the IVRS helpline.
    """
    logs = db.query(IVRCallLog).order_by(IVRCallLog.created_at.desc()).limit(limit).all()
    return logs


# ==========================================
# 2. Twilio Telephony Webhook Endpoints
# ==========================================

@router.post("/incoming")
async def twilio_incoming_call(
    request: Request,
    CallSid: Optional[str] = Form(None),
    From: Optional[str] = Form(None),
    db: Session = Depends(get_db)
):
    """
    Twilio Webhook: Triggered when a citizen calls the official helpline phone number.
    Returns standard TwiML XML.
    """
    call_sid = CallSid or f"TW_{uuid.uuid4().hex[:16]}"
    caller = From or "+919876543210"

    result = IVRService.handle_initial_call(
        call_sid=call_sid,
        caller_phone=caller,
        db=db,
    )
    return Response(content=result["twiml"], media_type="application/xml")


@router.post("/menu")
async def twilio_menu_webhook(
    request: Request,
    step: str = Query("language"),
    call_sid: str = Query(...),
    Digits: Optional[str] = Form(None),
    SpeechResult: Optional[str] = Form(None),
    db: Session = Depends(get_db)
):
    """
    Twilio Webhook: Receives DTMF Digits or SpeechResult from citizen and responds with TwiML.
    """
    result = IVRService.process_step(
        call_sid=call_sid,
        digit=Digits,
        speech_text=SpeechResult,
        current_step=step,
        db=db,
    )
    return Response(content=result["twiml"], media_type="application/xml")
