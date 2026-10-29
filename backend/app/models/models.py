from sqlalchemy import (
    Column, Integer, String, Float, Boolean, Text, DateTime, ForeignKey, Enum
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base
import enum


class RoleEnum(str, enum.Enum):
    citizen = "citizen"
    admin = "admin"


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    full_name = Column(String(150), nullable=False)
    email = Column(String(150), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    role = Column(Enum(RoleEnum), default=RoleEnum.citizen, nullable=False)
    preferred_language = Column(String(5), default="en")
    reset_token = Column(String(255), nullable=True)
    reset_token_expires_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    profile = relationship("UserProfile", back_populates="user", uselist=False, cascade="all, delete-orphan")
    saved_schemes = relationship("SavedScheme", back_populates="user", cascade="all, delete-orphan")
    notifications = relationship("Notification", back_populates="user", cascade="all, delete-orphan")
    family_members = relationship("FamilyMember", back_populates="user", cascade="all, delete-orphan")
    applications = relationship("ApplicationTracker", back_populates="user", cascade="all, delete-orphan")
    reviews = relationship("SchemeReview", back_populates="user", cascade="all, delete-orphan")


class UserProfile(Base):
    __tablename__ = "user_profiles"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True, nullable=False)
    age = Column(Integer)
    gender = Column(String(20))
    income = Column(Float)
    occupation = Column(String(50))
    education = Column(String(50))
    state = Column(String(50))
    category = Column(String(20))  # General/OBC/SC/ST/EWS
    is_student = Column(Boolean, default=False)
    is_farmer = Column(Boolean, default=False)
    has_disability = Column(Boolean, default=False)
    is_digilocker_verified = Column(Boolean, default=False)
    digilocker_id = Column(String(100), nullable=True)
    digilocker_linked_at = Column(DateTime(timezone=True), nullable=True)
    aadhaar_last4 = Column(String(4), nullable=True)
    verification_mode = Column(String(50), default="none")  # digilocker, kisan_portal, ration_pds, csc_assisted
    verified_name = Column(String(150), nullable=True)
    farmer_id = Column(String(100), nullable=True)  # PM-KISAN / AgriStack Farmer ID
    land_record_no = Column(String(100), nullable=True)  # RoR / Khata / Patta / Khasra No
    csc_agent_id = Column(String(100), nullable=True)  # CSC VLE ID for assisted mode
    ration_card_no = Column(String(100), nullable=True)
    kcc_account_no = Column(String(100), nullable=True)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), server_default=func.now())

    user = relationship("User", back_populates="profile")


class DigiLockerDocument(Base):
    __tablename__ = "digilocker_documents"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    doc_type = Column(String(50), nullable=False)  # aadhaar, income, caste, education, disability, ration
    doc_name = Column(String(150), nullable=False)
    issuer = Column(String(150), nullable=False)  # UIDAI, Revenue Dept, State Board, etc.
    doc_number = Column(String(100), nullable=False)
    verified_at = Column(DateTime(timezone=True), server_default=func.now())
    is_verified = Column(Boolean, default=True)
    file_uri = Column(String(255), nullable=True)
    metadata_json = Column(Text, nullable=True)
    security_hash = Column(String(128), nullable=True)
    source_channel = Column(String(50), default="digilocker")  # digilocker, pm_kisan, ration_pds, csc_vle

    user = relationship("User")



class Scheme(Base):
    __tablename__ = "schemes"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False)
    department = Column(String(150))
    description = Column(Text)
    benefits = Column(Text)
    category = Column(String(50))  # e.g. Education, Agriculture, Women, Employment
    target_group = Column(String(100))
    state = Column(String(50), default="All India")
    official_link = Column(String(255))
    application_deadline = Column(DateTime, nullable=True)
    is_active = Column(Boolean, default=True)
    # Provenance and Update fields
    government_level = Column(String(50), default="Central")  # Central, State, Concurrent
    source_url = Column(String(500), nullable=True)          # Trusted portal source (e.g. myscheme.gov.in)
    source_status = Column(String(50), default="verified")   # verified, needs_review, unverified
    last_checked_at = Column(DateTime(timezone=True), server_default=func.now())
    last_verified_at = Column(DateTime(timezone=True), server_default=func.now())
    provenance_note = Column(String(255), default="Official Gazette / National Portal Verified")
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    rules = relationship("EligibilityRule", back_populates="scheme", cascade="all, delete-orphan")
    documents = relationship("SchemeDocument", back_populates="scheme", cascade="all, delete-orphan")
    steps = relationship("ApplicationStep", back_populates="scheme", cascade="all, delete-orphan")
    saved_by = relationship("SavedScheme", back_populates="scheme", cascade="all, delete-orphan")
    applications = relationship("ApplicationTracker", back_populates="scheme", cascade="all, delete-orphan")
    reviews = relationship("SchemeReview", back_populates="scheme", cascade="all, delete-orphan")
    updates = relationship("SchemeUpdateHistory", back_populates="scheme", cascade="all, delete-orphan")


class SchemeUpdateHistory(Base):
    __tablename__ = "scheme_update_history"

    id = Column(Integer, primary_key=True, index=True)
    scheme_id = Column(Integer, ForeignKey("schemes.id"), nullable=True)
    scheme_title = Column(String(200), nullable=False)
    update_type = Column(String(50), nullable=False)  # 'created', 'updated', 'verified', 'flagged'
    field_changed = Column(String(100), nullable=True)
    old_value = Column(Text, nullable=True)
    new_value = Column(Text, nullable=True)
    source_url = Column(String(500), nullable=True)
    status = Column(String(50), default="success")  # success, warning, needs_review
    details = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    scheme = relationship("Scheme", back_populates="updates")



class EligibilityRule(Base):
    __tablename__ = "eligibility_rules"

    id = Column(Integer, primary_key=True, index=True)
    scheme_id = Column(Integer, ForeignKey("schemes.id"), nullable=False)
    field_name = Column(String(50), nullable=False)  # age, income, gender, occupation, education, state, category, is_student, is_farmer, has_disability
    operator = Column(String(10), nullable=False)     # eq, neq, lte, gte, lt, gt, in
    value = Column(String(255), nullable=False)        # comma-separated for 'in'
    description = Column(String(255))                  # human-readable reason text

    scheme = relationship("Scheme", back_populates="rules")


class SchemeDocument(Base):
    __tablename__ = "scheme_documents"

    id = Column(Integer, primary_key=True, index=True)
    scheme_id = Column(Integer, ForeignKey("schemes.id"), nullable=False)
    document_name = Column(String(150), nullable=False)
    is_mandatory = Column(Boolean, default=True)

    scheme = relationship("Scheme", back_populates="documents")


class ApplicationStep(Base):
    __tablename__ = "application_steps"

    id = Column(Integer, primary_key=True, index=True)
    scheme_id = Column(Integer, ForeignKey("schemes.id"), nullable=False)
    step_number = Column(Integer, nullable=False)
    instruction = Column(Text, nullable=False)

    scheme = relationship("Scheme", back_populates="steps")


class SavedScheme(Base):
    __tablename__ = "saved_schemes"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    scheme_id = Column(Integer, ForeignKey("schemes.id"), nullable=False)
    saved_at = Column(DateTime(timezone=True), server_default=func.now())

    user = relationship("User", back_populates="saved_schemes")
    scheme = relationship("Scheme", back_populates="saved_by")


class Notification(Base):
    __tablename__ = "notifications"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    scheme_id = Column(Integer, ForeignKey("schemes.id"), nullable=True)
    message = Column(String(255), nullable=False)
    is_read = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    user = relationship("User", back_populates="notifications")


class FamilyMember(Base):
    __tablename__ = "family_members"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    name = Column(String(100), nullable=False)
    relation = Column(String(50), nullable=False)  # Father, Mother, Spouse, Son, Daughter, etc.
    age = Column(Integer)
    gender = Column(String(20))
    income = Column(Float, default=0.0)
    occupation = Column(String(50))
    education = Column(String(50))
    state = Column(String(50))
    category = Column(String(20))
    is_student = Column(Boolean, default=False)
    is_farmer = Column(Boolean, default=False)
    has_disability = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    user = relationship("User", back_populates="family_members")


class ApplicationStatusEnum(str, enum.Enum):
    applied = "applied"
    in_progress = "in_progress"
    approved = "approved"
    rejected = "rejected"


class ApplicationTracker(Base):
    __tablename__ = "application_tracker"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    scheme_id = Column(Integer, ForeignKey("schemes.id"), nullable=False)
    family_member_name = Column(String(100), nullable=True)  # Applied for whom (self or family member)
    status = Column(String(30), default="applied", nullable=False)  # applied, in_progress, approved, rejected
    application_reference = Column(String(100), nullable=True)
    notes = Column(Text, nullable=True)
    applied_date = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), server_default=func.now())

    user = relationship("User", back_populates="applications")
    scheme = relationship("Scheme", back_populates="applications")


class SchemeReview(Base):
    __tablename__ = "scheme_reviews"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    scheme_id = Column(Integer, ForeignKey("schemes.id"), nullable=False)
    rating = Column(Integer, nullable=False)  # 1 to 5
    comment = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    user = relationship("User", back_populates="reviews")
    scheme = relationship("Scheme", back_populates="reviews")


class IVRCallLog(Base):
    __tablename__ = "ivr_call_logs"

    id = Column(Integer, primary_key=True, index=True)
    call_sid = Column(String(100), unique=True, index=True, nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    caller_phone = Column(String(30), nullable=True)
    language = Column(String(10), default="en")
    status = Column(String(30), default="completed")  # ringing, in_progress, completed, failed
    duration_seconds = Column(Integer, default=0)
    user_transcript = Column(Text, nullable=True)
    bot_response = Column(Text, nullable=True)
    dtmf_digits = Column(String(50), nullable=True)
    schemes_mentioned = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    user = relationship("User")


