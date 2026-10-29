from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.utils.dependencies import get_current_user
from app.models.models import User, UserProfile, Scheme
from app.schemas.schemas import EligibilityResult
from app.services.eligibility_engine import recommend_schemes

router = APIRouter(prefix="/api/recommendations", tags=["Recommendations"])


@router.get("", response_model=list[EligibilityResult])
def get_recommendations(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    profile = db.query(UserProfile).filter(UserProfile.user_id == user.id).first()
    if not profile:
        raise HTTPException(status_code=400, detail="Please complete your profile first")

    schemes = db.query(Scheme).filter(Scheme.is_active == True).all()  # noqa: E712
    return recommend_schemes(schemes, profile)
