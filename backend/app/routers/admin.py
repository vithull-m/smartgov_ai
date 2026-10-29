from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.utils.dependencies import get_current_admin
from app.models.models import Scheme, EligibilityRule, SchemeDocument, ApplicationStep, User
from app.schemas.schemas import SchemeCreate, SchemeUpdate, SchemeOut, UserOut

router = APIRouter(prefix="/api/admin", tags=["Admin"])


@router.get("/schemes", response_model=list[SchemeOut])
def admin_list_schemes(db: Session = Depends(get_db), _=Depends(get_current_admin)):
    return db.query(Scheme).order_by(Scheme.created_at.desc()).all()


@router.post("/schemes", response_model=SchemeOut, status_code=201)
def create_scheme(payload: SchemeCreate, db: Session = Depends(get_db), _=Depends(get_current_admin)):
    data = payload.model_dump(exclude={"rules", "documents", "steps"})
    scheme = Scheme(**data)
    db.add(scheme)
    db.flush()

    for r in payload.rules:
        db.add(EligibilityRule(scheme_id=scheme.id, **r.model_dump()))
    for d in payload.documents:
        db.add(SchemeDocument(scheme_id=scheme.id, **d.model_dump()))
    for s in payload.steps:
        db.add(ApplicationStep(scheme_id=scheme.id, **s.model_dump()))

    db.commit()
    db.refresh(scheme)
    return scheme


@router.put("/schemes/{scheme_id}", response_model=SchemeOut)
def update_scheme(scheme_id: int, payload: SchemeUpdate, db: Session = Depends(get_db), _=Depends(get_current_admin)):
    scheme = db.query(Scheme).filter(Scheme.id == scheme_id).first()
    if not scheme:
        raise HTTPException(status_code=404, detail="Scheme not found")

    data = payload.model_dump(exclude={"rules", "documents", "steps"})
    for field, value in data.items():
        setattr(scheme, field, value)

    db.query(EligibilityRule).filter(EligibilityRule.scheme_id == scheme_id).delete()
    db.query(SchemeDocument).filter(SchemeDocument.scheme_id == scheme_id).delete()
    db.query(ApplicationStep).filter(ApplicationStep.scheme_id == scheme_id).delete()

    for r in payload.rules:
        db.add(EligibilityRule(scheme_id=scheme.id, **r.model_dump()))
    for d in payload.documents:
        db.add(SchemeDocument(scheme_id=scheme.id, **d.model_dump()))
    for s in payload.steps:
        db.add(ApplicationStep(scheme_id=scheme.id, **s.model_dump()))

    db.commit()
    db.refresh(scheme)
    return scheme


@router.delete("/schemes/{scheme_id}", status_code=204)
def delete_scheme(scheme_id: int, db: Session = Depends(get_db), _=Depends(get_current_admin)):
    scheme = db.query(Scheme).filter(Scheme.id == scheme_id).first()
    if scheme:
        db.delete(scheme)
        db.commit()
    return None


@router.get("/users", response_model=list[UserOut])
def admin_list_users(db: Session = Depends(get_db), _=Depends(get_current_admin)):
    return db.query(User).all()


@router.get("/analytics")
def admin_analytics(db: Session = Depends(get_db), _=Depends(get_current_admin)):
    from app.models.models import ApplicationTracker, SavedScheme, SchemeReview
    from sqlalchemy import func

    total_users = db.query(User).count()
    total_schemes = db.query(Scheme).count()
    total_applications = db.query(ApplicationTracker).count()
    total_saved = db.query(SavedScheme).count()
    total_reviews = db.query(SchemeReview).count()

    avg_rating_row = db.query(func.avg(SchemeReview.rating)).scalar()
    avg_rating = round(float(avg_rating_row), 1) if avg_rating_row else 0.0

    # Schemes by category
    categories_raw = (
        db.query(Scheme.category, func.count(Scheme.id))
        .group_by(Scheme.category)
        .all()
    )
    schemes_by_category = [{"category": c or "Uncategorized", "count": cnt} for c, cnt in categories_raw]

    # Applications by status
    status_raw = (
        db.query(ApplicationTracker.status, func.count(ApplicationTracker.id))
        .group_by(ApplicationTracker.status)
        .all()
    )
    applications_by_status = [{"status": s, "count": cnt} for s, cnt in status_raw]

    # Recent applications
    recent = (
        db.query(ApplicationTracker)
        .order_by(ApplicationTracker.applied_date.desc())
        .limit(10)
        .all()
    )
    recent_list = []
    for r in recent:
        scheme_obj = db.query(Scheme).filter(Scheme.id == r.scheme_id).first()
        user_obj = db.query(User).filter(User.id == r.user_id).first()
        recent_list.append({
            "id": r.id,
            "scheme_id": r.scheme_id,
            "scheme_title": scheme_obj.title if scheme_obj else "Unknown",
            "user_name": user_obj.full_name if user_obj else "Unknown",
            "family_member_name": r.family_member_name,
            "status": r.status,
            "applied_date": str(r.applied_date),
        })

    return {
        "total_users": total_users,
        "total_schemes": total_schemes,
        "total_applications": total_applications,
        "total_saved": total_saved,
        "total_reviews": total_reviews,
        "average_rating_overall": avg_rating,
        "schemes_by_category": schemes_by_category,
        "applications_by_status": applications_by_status,
        "recent_applications": recent_list,
    }

