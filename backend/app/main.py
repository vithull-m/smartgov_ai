from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.core.database import Base, engine, ensure_user_reset_columns, SessionLocal
from sqlalchemy import text
from app.models import models  # noqa: F401 ensures models are registered
from app.routers import (
    auth, profile, schemes, eligibility, recommendations,
    saved, compare, notifications, chatbot, admin,
    family, applications, reviews, digilocker, updates,
    speech, ivr,
)

app = FastAPI(title="SmartGov AI", version="2.0.0")

origins = [o.strip() for o in settings.CORS_ORIGINS.split(",")]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Auto-create tables (use database/schema.sql for a full production setup)
Base.metadata.create_all(bind=engine)
ensure_user_reset_columns()

app.include_router(auth.router)
app.include_router(profile.router)
app.include_router(schemes.router)
app.include_router(eligibility.router)
app.include_router(recommendations.router)
app.include_router(saved.router)
app.include_router(compare.router)
app.include_router(notifications.router)
app.include_router(chatbot.router)
app.include_router(admin.router)
app.include_router(family.router)
app.include_router(applications.router)
app.include_router(reviews.router)
app.include_router(digilocker.router)
app.include_router(updates.router)
app.include_router(speech.router)
app.include_router(ivr.router)







@app.get("/")
def root():
    return {"status": "ok", "service": "SmartGov AI backend"}


@app.get("/api/health")
def health():
    try:
        db = SessionLocal()
        db.execute(text("SELECT 1"))
        db.close()
        return {"status": "healthy", "database": "connected"}
    except Exception as e:
        return {"status": "unhealthy", "database": str(e)}
