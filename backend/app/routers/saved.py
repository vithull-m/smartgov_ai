from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.utils.dependencies import get_current_user
from app.models.models import User, SavedScheme, Scheme
from app.schemas.schemas import SavedSchemeOut

router = APIRouter(prefix="/api/saved", tags=["Saved Schemes"])


@router.get("", response_model=list[SavedSchemeOut])
def list_saved(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return db.query(SavedScheme).filter(SavedScheme.user_id == user.id).all()


@router.post("/{scheme_id}", response_model=SavedSchemeOut, status_code=201)
def save_scheme(scheme_id: int, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    scheme = db.query(Scheme).filter(Scheme.id == scheme_id).first()
    if not scheme:
        raise HTTPException(status_code=404, detail="Scheme not found")

    existing = db.query(SavedScheme).filter(
        SavedScheme.user_id == user.id, SavedScheme.scheme_id == scheme_id
    ).first()
    if existing:
        return existing

    saved = SavedScheme(user_id=user.id, scheme_id=scheme_id)
    db.add(saved)
    db.commit()
    db.refresh(saved)
    return saved


@router.delete("/{scheme_id}", status_code=204)
def unsave_scheme(scheme_id: int, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    saved = db.query(SavedScheme).filter(
        SavedScheme.user_id == user.id, SavedScheme.scheme_id == scheme_id
    ).first()
    if saved:
        db.delete(saved)
        db.commit()
    return None
