from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.core.database import get_db
from app.utils.dependencies import get_current_user
from app.models.models import User, SchemeReview, Scheme
from app.schemas.schemas import ReviewCreate, ReviewOut, SchemeReviewStats

router = APIRouter(prefix="/api/reviews", tags=["Reviews"])


@router.get("/scheme/{scheme_id}", response_model=SchemeReviewStats)
def get_scheme_reviews(scheme_id: int, db: Session = Depends(get_db)):
    reviews = (
        db.query(SchemeReview)
        .filter(SchemeReview.scheme_id == scheme_id)
        .order_by(SchemeReview.created_at.desc())
        .all()
    )
    if not reviews:
        return SchemeReviewStats(average_rating=0.0, total_reviews=0, reviews=[])

    avg_rating = sum(r.rating for r in reviews) / len(reviews)
    review_outs = []
    for r in reviews:
        user = db.query(User).filter(User.id == r.user_id).first()
        review_outs.append(
            ReviewOut(
                id=r.id,
                user_id=r.user_id,
                scheme_id=r.scheme_id,
                rating=r.rating,
                comment=r.comment,
                created_at=r.created_at,
                user_name=user.full_name if user else "Anonymous",
            )
        )

    return SchemeReviewStats(
        average_rating=round(avg_rating, 1),
        total_reviews=len(reviews),
        reviews=review_outs,
    )


@router.post("/scheme/{scheme_id}", response_model=ReviewOut, status_code=201)
def add_review(
    scheme_id: int,
    payload: ReviewCreate,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if payload.rating < 1 or payload.rating > 5:
        raise HTTPException(status_code=400, detail="Rating must be between 1 and 5")

    scheme = db.query(Scheme).filter(Scheme.id == scheme_id).first()
    if not scheme:
        raise HTTPException(status_code=404, detail="Scheme not found")

    # Update if already reviewed by user, else create
    existing = (
        db.query(SchemeReview)
        .filter(SchemeReview.scheme_id == scheme_id, SchemeReview.user_id == user.id)
        .first()
    )
    if existing:
        existing.rating = payload.rating
        existing.comment = payload.comment
        db.commit()
        db.refresh(existing)
        return ReviewOut(
            id=existing.id,
            user_id=existing.user_id,
            scheme_id=existing.scheme_id,
            rating=existing.rating,
            comment=existing.comment,
            created_at=existing.created_at,
            user_name=user.full_name,
        )

    review = SchemeReview(
        user_id=user.id,
        scheme_id=scheme_id,
        rating=payload.rating,
        comment=payload.comment,
    )
    db.add(review)
    db.commit()
    db.refresh(review)
    return ReviewOut(
        id=review.id,
        user_id=review.user_id,
        scheme_id=review.scheme_id,
        rating=review.rating,
        comment=review.comment,
        created_at=review.created_at,
        user_name=user.full_name,
    )
