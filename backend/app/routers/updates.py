from fastapi import APIRouter, Depends, HTTPException, Header, Query
from sqlalchemy.orm import Session
from typing import Optional, List, Dict, Any
from app.core.database import get_db
from app.core.config import settings
from app.schemas.schemas import SchemeUpdateStatusResponse, SchemeUpdateHistoryOut
from app.services.scheme_updater import SchemeUpdateService

router = APIRouter(prefix="/api/updates", tags=["Updates"])


@router.get("/status", response_model=SchemeUpdateStatusResponse)
def get_update_status(db: Session = Depends(get_db)):
    """
    Get scheme update service status, last successful update timestamp,
    total schemes checked, and update history.
    """
    status_data = SchemeUpdateService.get_status(db)
    return status_data


@router.post("/sync")
def trigger_manual_sync(
    x_admin_key: Optional[str] = Header(None, alias="X-Admin-Key"),
    db: Session = Depends(get_db)
):
    """
    Manually trigger sync against official portal datasets.
    Protected by administrative header or secret key.
    """
    if x_admin_key != settings.ADMIN_API_KEY:
        raise HTTPException(status_code=403, detail="Invalid admin authorization key")

    result = SchemeUpdateService.trigger_scheduled_sync(db)
    return result


@router.post("/scheme-entry")
def sync_scheme_entry(
    payload: Dict[str, Any],
    source_url: str = Query(..., description="Official government source URL"),
    x_admin_key: Optional[str] = Header(None, alias="X-Admin-Key"),
    db: Session = Depends(get_db)
):
    """
    Admin endpoint to ingest or update a verified scheme with source validation and provenance logging.
    """
    if x_admin_key != settings.ADMIN_API_KEY:
        raise HTTPException(status_code=403, detail="Invalid admin authorization key")

    res = SchemeUpdateService.sync_verified_scheme(
        scheme_data=payload,
        source_url=source_url,
        db=db,
        admin_verified=True
    )
    return res
