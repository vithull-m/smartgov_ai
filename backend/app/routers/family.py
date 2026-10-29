from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.utils.dependencies import get_current_user
from app.models.models import User, FamilyMember, Scheme
from app.schemas.schemas import FamilyMemberCreate, FamilyMemberUpdate, FamilyMemberOut, EligibilityResult
from app.services.eligibility_engine import recommend_schemes

router = APIRouter(prefix="/api/family", tags=["Family"])


@router.get("", response_model=list[FamilyMemberOut])
def get_family_members(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return db.query(FamilyMember).filter(FamilyMember.user_id == user.id).all()


@router.post("", response_model=FamilyMemberOut, status_code=201)
def add_family_member(payload: FamilyMemberCreate, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    member = FamilyMember(user_id=user.id, **payload.model_dump())
    db.add(member)
    db.commit()
    db.refresh(member)
    return member


@router.put("/{member_id}", response_model=FamilyMemberOut)
def update_family_member(member_id: int, payload: FamilyMemberUpdate, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    member = db.query(FamilyMember).filter(FamilyMember.id == member_id, FamilyMember.user_id == user.id).first()
    if not member:
        raise HTTPException(status_code=404, detail="Family member not found")

    for key, value in payload.model_dump().items():
        setattr(member, key, value)

    db.commit()
    db.refresh(member)
    return member


@router.delete("/{member_id}", status_code=204)
def delete_family_member(member_id: int, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    member = db.query(FamilyMember).filter(FamilyMember.id == member_id, FamilyMember.user_id == user.id).first()
    if not member:
        raise HTTPException(status_code=404, detail="Family member not found")
    db.delete(member)
    db.commit()
    return None


@router.get("/{member_id}/recommendations", response_model=list[EligibilityResult])
def get_family_member_recommendations(member_id: int, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    member = db.query(FamilyMember).filter(FamilyMember.id == member_id, FamilyMember.user_id == user.id).first()
    if not member:
        raise HTTPException(status_code=404, detail="Family member not found")

    schemes = db.query(Scheme).filter(Scheme.is_active == True).all()  # noqa: E712
    # The member model has all profile fields (age, gender, income, occupation, education, state, category, is_student, is_farmer, has_disability)
    return recommend_schemes(schemes, member)
