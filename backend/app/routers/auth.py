import secrets
from datetime import datetime, timedelta, timezone
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.security import hash_password, verify_password, create_access_token
from app.models.models import User, UserProfile
from app.schemas.schemas import (
    UserCreate, UserLogin, Token, UserOut,
    ForgotPasswordRequest, ForgotPasswordResponse,
    ResetPasswordRequest, ResetPasswordResponse,
)

router = APIRouter(prefix="/api/auth", tags=["Auth"])


@router.post("/register", response_model=Token, status_code=status.HTTP_201_CREATED)
def register(payload: UserCreate, db: Session = Depends(get_db)):
    if db.query(User).filter(User.email == payload.email).first():
        raise HTTPException(status_code=400, detail="Email already registered")

    user = User(
        full_name=payload.full_name,
        email=payload.email,
        hashed_password=hash_password(payload.password),
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    db.add(UserProfile(user_id=user.id))
    db.commit()

    token = create_access_token({"sub": str(user.id)})
    return Token(access_token=token, user=UserOut.model_validate(user))


@router.post("/login", response_model=Token)
def login(payload: UserLogin, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == payload.email).first()
    if not user or not verify_password(payload.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid email or password")

    token = create_access_token({"sub": str(user.id)})
    return Token(access_token=token, user=UserOut.model_validate(user))


@router.post("/forgot-password", response_model=ForgotPasswordResponse)
def forgot_password(payload: ForgotPasswordRequest, db: Session = Depends(get_db)):
    from app.services.email_service import send_password_reset_email

    user = db.query(User).filter(User.email == payload.email).first()
    otp = None
    email_sent = False

    if user:
        otp = f"{secrets.randbelow(1000000):06d}"
        user.reset_token = otp
        user.reset_token_expires_at = datetime.now(timezone.utc) + timedelta(minutes=10)
        db.commit()

        email_sent = send_password_reset_email(
            to_email=user.email,
            otp=otp,
            user_name=user.full_name or "Citizen",
        )

        if email_sent:
            msg = f"A 6-digit verification OTP has been sent to {user.email}. Please check your inbox."
        else:
            msg = "Could not deliver email via SMTP. Your reset OTP is shown below."
    else:
        msg = "If an account exists for that email, a reset code has been sent."

    return {
        "message": msg,
        "otp": otp if not email_sent else None,
        "email_sent": email_sent,
    }




@router.post("/reset-password", response_model=ResetPasswordResponse)
def reset_password(payload: ResetPasswordRequest, db: Session = Depends(get_db)):
    if len(payload.new_password) < 6:
        raise HTTPException(status_code=400, detail="Password must be at least 6 characters long")

    user = db.query(User).filter(User.reset_token == payload.otp).first()
    if not user:
        raise HTTPException(status_code=400, detail="Invalid or expired reset token")

    expires_at = user.reset_token_expires_at
    if expires_at is None:
        is_expired = True
    else:
        if expires_at.tzinfo is None:
            expires_at = expires_at.replace(tzinfo=timezone.utc)
        is_expired = expires_at < datetime.now(timezone.utc)

    if is_expired:
        user.reset_token = None
        user.reset_token_expires_at = None
        db.commit()
        raise HTTPException(status_code=400, detail="Invalid or expired reset token")

    user.hashed_password = hash_password(payload.new_password)
    user.reset_token = None
    user.reset_token_expires_at = None
    db.commit()

    return {"message": "Password reset successful. You can now log in with your new password."}
