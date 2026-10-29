from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.utils.dependencies import get_current_user
from app.models.models import User, UserProfile
from app.schemas.schemas import ProfileOut, ProfileUpdate

router = APIRouter(prefix="/api/profile", tags=["Profile"])


@router.get("/me", response_model=ProfileOut)
def get_my_profile(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    profile = db.query(UserProfile).filter(UserProfile.user_id == user.id).first()
    if not profile:
        profile = UserProfile(user_id=user.id)
        db.add(profile)
        db.commit()
        db.refresh(profile)
    return profile


@router.put("/me", response_model=ProfileOut)
def update_my_profile(payload: ProfileUpdate, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    profile = db.query(UserProfile).filter(UserProfile.user_id == user.id).first()
    if not profile:
        profile = UserProfile(user_id=user.id)
        db.add(profile)

    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(profile, field, value)

    db.commit()
    db.refresh(profile)
    return profile
