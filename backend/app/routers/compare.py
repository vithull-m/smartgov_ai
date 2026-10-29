from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.models import Scheme
from app.schemas.schemas import SchemeOut

router = APIRouter(prefix="/api/compare", tags=["Compare"])


@router.get("", response_model=list[SchemeOut])
def compare_schemes(ids: str = Query(..., description="Comma-separated scheme IDs, e.g. 1,2,3"), db: Session = Depends(get_db)):
    try:
        id_list = [int(i.strip()) for i in ids.split(",") if i.strip()]
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid scheme IDs")

    if len(id_list) < 2 or len(id_list) > 4:
        raise HTTPException(status_code=400, detail="Select between 2 and 4 schemes to compare")

    schemes = db.query(Scheme).filter(Scheme.id.in_(id_list)).all()
    if len(schemes) != len(id_list):
        raise HTTPException(status_code=404, detail="One or more schemes not found")
    return schemes
