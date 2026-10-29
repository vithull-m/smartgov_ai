from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session, joinedload
from app.core.database import get_db
from app.utils.dependencies import get_current_user
from app.models.models import User, ApplicationTracker, Scheme
from app.schemas.schemas import ApplicationCreate, ApplicationUpdate, ApplicationOut

router = APIRouter(prefix="/api/applications", tags=["Applications"])


@router.get("", response_model=list[ApplicationOut])
def get_user_applications(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return (
        db.query(ApplicationTracker)
        .options(joinedload(ApplicationTracker.scheme))
        .filter(ApplicationTracker.user_id == user.id)
        .order_by(ApplicationTracker.applied_date.desc())
        .all()
    )


@router.post("", response_model=ApplicationOut, status_code=201)
def track_application(payload: ApplicationCreate, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    scheme = db.query(Scheme).filter(Scheme.id == payload.scheme_id).first()
    if not scheme:
        raise HTTPException(status_code=404, detail="Scheme not found")

    app = ApplicationTracker(user_id=user.id, **payload.model_dump())
    db.add(app)
    db.commit()
    db.refresh(app)
    return app


@router.put("/{app_id}", response_model=ApplicationOut)
def update_application(app_id: int, payload: ApplicationUpdate, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    app = db.query(ApplicationTracker).filter(ApplicationTracker.id == app_id, ApplicationTracker.user_id == user.id).first()
    if not app:
        raise HTTPException(status_code=404, detail="Application record not found")

    for key, value in payload.model_dump(exclude_unset=True).items():
        if value is not None:
            setattr(app, key, value)

    db.commit()
    db.refresh(app)
    return app


@router.delete("/{app_id}", status_code=204)
def delete_application(app_id: int, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    app = db.query(ApplicationTracker).filter(ApplicationTracker.id == app_id, ApplicationTracker.user_id == user.id).first()
    if not app:
        raise HTTPException(status_code=404, detail="Application record not found")
    db.delete(app)
    db.commit()
    return None
