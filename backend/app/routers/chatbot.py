from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Optional
from app.core.database import get_db
from app.utils.dependencies import get_optional_current_user
from app.models.models import User
from app.schemas.schemas import ChatRequest, ChatResponse
from app.services.agent_orchestrator import SmartGovAIAgent

router = APIRouter(prefix="/api/chatbot", tags=["Chatbot"])


@router.post("", response_model=ChatResponse)
@router.post("/chat", response_model=ChatResponse)
def chat(
    payload: ChatRequest,
    user: Optional[User] = Depends(get_optional_current_user),
    db: Session = Depends(get_db),
):
    """
    Multilingual AI Agent endpoint with automatic language detection,
    deterministic tool calling, eligibility calculation, and source attribution.
    """
    if not payload.message or not payload.message.strip():
        raise HTTPException(status_code=400, detail="User message cannot be empty")

    try:
        response = SmartGovAIAgent.run_turn(
            message=payload.message.strip(),
            user=user,
            db=db,
            explicit_language=payload.language,
        )
        return response
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Agent error: {str(exc)}")
