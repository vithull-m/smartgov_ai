import os
from pathlib import Path
from pydantic_settings import BaseSettings

_ENV_FILE = Path(__file__).resolve().parents[2] / ".env"

class Settings(BaseSettings):
    DATABASE_URL: str = "sqlite:///./smartgov_ai.db"
    SECRET_KEY: str = "change-this-to-a-long-random-string"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440
    OPENAI_API_KEY: str = ""
    OPENAI_BASE_URL: str = "https://api.openai.com/v1"
    OPENAI_MODEL: str = "gpt-4o-mini"
    AI_PROVIDER: str = "openai"  # openai, gemini, groq, mock, fallback
    CORS_ORIGINS: str = "http://localhost:5173"

    # Scheme Update Service Settings
    SCHEME_UPDATE_INTERVAL_HOURS: int = 24
    SCHEME_UPDATE_SOURCE_URL: str = "https://www.myscheme.gov.in/"
    ADMIN_API_KEY: str = "smartgov-admin-secure-key"

    # Speech / Audio Settings
    SPEECH_SERVICE_ENABLED: bool = True
    TTS_DEFAULT_VOICE: str = "default"

    # IVR System Settings
    IVR_ENABLED: bool = True
    IVR_DEFAULT_LANGUAGE: str = "en"
    TWILIO_ACCOUNT_SID: str = ""
    TWILIO_AUTH_TOKEN: str = ""
    TWILIO_PHONE_NUMBER: str = "+18005550199"
    BASE_WEBHOOK_URL: str = "http://localhost:8000"


    # SMTP Email Settings
    SMTP_HOST: str = "smtp.gmail.com"
    SMTP_PORT: int = 587
    SMTP_USER: str = ""
    SMTP_PASSWORD: str = ""
    SMTP_FROM_EMAIL: str = ""
    SMTP_FROM_NAME: str = "SmartGov AI"
    SMTP_TLS: bool = True

    class Config:
        env_file = str(_ENV_FILE)
        extra = "allow"

settings = Settings()
