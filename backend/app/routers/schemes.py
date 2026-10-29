from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional
from app.core.database import get_db
from app.models.models import Scheme
from app.schemas.schemas import SchemeOut, SchemeListOut

router = APIRouter(prefix="/api/schemes", tags=["Schemes"])


@router.get("", response_model=list[SchemeListOut])
def list_schemes(
    category: Optional[str] = None,
    state: Optional[str] = None,
    search: Optional[str] = None,
    db: Session = Depends(get_db),
):
    query = db.query(Scheme).filter(Scheme.is_active == True)  # noqa: E712
    if category:
        query = query.filter(Scheme.category == category)
    if state:
        query = query.filter((Scheme.state == state) | (Scheme.state == "All India"))
    if search:
        query = query.filter(Scheme.title.ilike(f"%{search}%"))
    return query.order_by(Scheme.created_at.desc()).all()


@router.get("/{scheme_id}", response_model=SchemeOut)
def get_scheme(scheme_id: int, db: Session = Depends(get_db)):
    scheme = db.query(Scheme).filter(Scheme.id == scheme_id).first()
    if not scheme:
        raise HTTPException(status_code=404, detail="Scheme not found")
    return scheme
