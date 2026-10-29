from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, declarative_base
from app.core.config import settings

engine = create_engine(settings.DATABASE_URL, pool_pre_ping=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def ensure_schema_migrations():
    """Safely apply non-destructive schema migrations without losing existing data."""
    db = SessionLocal()
    try:
        dialect = db.get_bind().dialect.name
        if dialect == "sqlite":
            # Users table migration
            user_cols = [row[1] for row in db.execute(text("PRAGMA table_info(users)"))]
            if "reset_token" not in user_cols:
                db.execute(text("ALTER TABLE users ADD COLUMN reset_token VARCHAR(255)"))
            if "reset_token_expires_at" not in user_cols:
                db.execute(text("ALTER TABLE users ADD COLUMN reset_token_expires_at DATETIME"))

            # Schemes table migration
            scheme_cols = [row[1] for row in db.execute(text("PRAGMA table_info(schemes)"))]
            if "government_level" not in scheme_cols:
                db.execute(text("ALTER TABLE schemes ADD COLUMN government_level VARCHAR(50) DEFAULT 'Central'"))
            if "source_url" not in scheme_cols:
                db.execute(text("ALTER TABLE schemes ADD COLUMN source_url VARCHAR(500)"))
            if "source_status" not in scheme_cols:
                db.execute(text("ALTER TABLE schemes ADD COLUMN source_status VARCHAR(50) DEFAULT 'verified'"))
            if "last_checked_at" not in scheme_cols:
                db.execute(text("ALTER TABLE schemes ADD COLUMN last_checked_at DATETIME"))
            if "last_verified_at" not in scheme_cols:
                db.execute(text("ALTER TABLE schemes ADD COLUMN last_verified_at DATETIME"))
            if "provenance_note" not in scheme_cols:
                db.execute(text("ALTER TABLE schemes ADD COLUMN provenance_note VARCHAR(255) DEFAULT 'Official National Portal Verified'"))
            
            db.commit()
    except Exception:
        pass
    finally:
        db.close()


def ensure_user_reset_columns():
    ensure_schema_migrations()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
