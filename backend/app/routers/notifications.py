from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.utils.dependencies import get_current_user
from app.models.models import User, Notification
from app.schemas.schemas import NotificationOut

router = APIRouter(prefix="/api/notifications", tags=["Notifications"])


@router.get("", response_model=list[NotificationOut])
def list_notifications(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return db.query(Notification).filter(Notification.user_id == user.id).order_by(Notification.created_at.desc()).all()


@router.put("/{notification_id}/read", response_model=NotificationOut)
def mark_read(notification_id: int, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    note = db.query(Notification).filter(
        Notification.id == notification_id, Notification.user_id == user.id
    ).first()
    if not note:
        raise HTTPException(status_code=404, detail="Notification not found")
    note.is_read = True
    db.commit()
    db.refresh(note)
    return note
