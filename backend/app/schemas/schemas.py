from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime


# ---------- Auth ----------
class UserCreate(BaseModel):
    full_name: str
    email: EmailStr
    password: str


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class ForgotPasswordRequest(BaseModel):
    email: EmailStr


class ForgotPasswordResponse(BaseModel):
    message: str
    otp: Optional[str] = None
    email_sent: bool = False




class ResetPasswordRequest(BaseModel):
    otp: str
    new_password: str


class ResetPasswordResponse(BaseModel):
    message: str


class UserOut(BaseModel):
    id: int
    full_name: str
    email: EmailStr
    role: str
    preferred_language: str

    class Config:
        from_attributes = True


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserOut


# ---------- Profile ----------
class ProfileBase(BaseModel):
    age: Optional[int] = None
    gender: Optional[str] = None
    income: Optional[float] = None
    occupation: Optional[str] = None
    education: Optional[str] = None
    state: Optional[str] = None
    category: Optional[str] = None
    is_student: Optional[bool] = False
    is_farmer: Optional[bool] = False
    has_disability: Optional[bool] = False
    is_digilocker_verified: Optional[bool] = False
    digilocker_id: Optional[str] = None
    aadhaar_last4: Optional[str] = None
    verification_mode: Optional[str] = "none"
    verified_name: Optional[str] = None
    farmer_id: Optional[str] = None
    land_record_no: Optional[str] = None
    csc_agent_id: Optional[str] = None
    ration_card_no: Optional[str] = None
    kcc_account_no: Optional[str] = None


class ProfileUpdate(ProfileBase):
    pass


class ProfileOut(ProfileBase):
    id: int
    user_id: int
    digilocker_linked_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# ---------- DigiLocker ----------
class DigiLockerDocOut(BaseModel):
    id: int
    doc_type: str
    doc_name: str
    issuer: str
    doc_number: str
    verified_at: datetime
    is_verified: bool
    source_channel: Optional[str] = "digilocker"
    security_hash: Optional[str] = None
    metadata_json: Optional[str] = None

    class Config:
        from_attributes = True


class DigiLockerConnectRequest(BaseModel):
    aadhaar_number: str  # 12 digits
    otp: str  # 6 digits
    consent: bool = True
    full_name: Optional[str] = None


class FarmerAuthRequest(BaseModel):
    auth_type: str  # 'pm_kisan', 'land_record', 'ration_card', 'csc_vle'
    identifier: str  # Farmer ID / Aadhaar / Land Khata No / Ration Card No
    state: Optional[str] = "Tamil Nadu"
    district: Optional[str] = None
    village: Optional[str] = None
    otp: Optional[str] = "123456"
    csc_vle_id: Optional[str] = None
    consent: bool = True



# ---------- Scheme ----------
class RuleBase(BaseModel):
    field_name: str
    operator: str
    value: str
    description: Optional[str] = None


class RuleOut(RuleBase):
    id: int

    class Config:
        from_attributes = True


class DocumentBase(BaseModel):
    document_name: str
    is_mandatory: bool = True


class DocumentOut(DocumentBase):
    id: int

    class Config:
        from_attributes = True


class StepBase(BaseModel):
    step_number: int
    instruction: str


class StepOut(StepBase):
    id: int

    class Config:
        from_attributes = True


class SchemeBase(BaseModel):
    title: str
    department: Optional[str] = None
    description: Optional[str] = None
    benefits: Optional[str] = None
    category: Optional[str] = None
    target_group: Optional[str] = None
    state: Optional[str] = "All India"
    official_link: Optional[str] = None
    application_deadline: Optional[datetime] = None
    is_active: bool = True
    government_level: Optional[str] = "Central"
    source_url: Optional[str] = None
    source_status: Optional[str] = "verified"
    last_checked_at: Optional[datetime] = None
    last_verified_at: Optional[datetime] = None
    provenance_note: Optional[str] = "Official National Portal Verified"


class SchemeCreate(SchemeBase):
    rules: List[RuleBase] = []
    documents: List[DocumentBase] = []
    steps: List[StepBase] = []


class SchemeUpdate(SchemeCreate):
    pass


class SchemeOut(SchemeBase):
    id: int
    rules: List[RuleOut] = []
    documents: List[DocumentOut] = []
    steps: List[StepOut] = []

    class Config:
        from_attributes = True


class SchemeListOut(SchemeBase):
    id: int

    class Config:
        from_attributes = True


# ---------- Eligibility / Recommendation ----------
class EligibilityStatus(str):
    LIKELY_ELIGIBLE = "likely_eligible"
    NOT_ELIGIBLE = "not_eligible"
    NEEDS_MORE_INFO = "needs_more_information"
    UNVERIFIED = "unverified_scheme_data"


class EligibilityEvaluationResult(BaseModel):
    scheme_id: int
    title: str
    status: str  # likely_eligible, not_eligible, needs_more_information, unverified_scheme_data
    match_score: float
    is_eligible: bool
    passed_conditions: List[str] = []
    failed_conditions: List[str] = []
    missing_information: List[str] = []
    required_documents: List[str] = []
    official_link: Optional[str] = None
    source_url: Optional[str] = None
    last_verified_at: Optional[datetime] = None
    source_status: Optional[str] = "verified"
    disclaimer: str = (
        "Preliminary eligibility evaluation based on available rules. "
        "Does not guarantee official government approval. Please verify with official portal."
    )


class EligibilityResult(BaseModel):
    scheme_id: int
    title: str
    match_score: float
    is_eligible: bool
    status: Optional[str] = "likely_eligible"
    matched_reasons: List[str] = []
    unmatched_reasons: List[str] = []
# ---------- Saved ----------
class SavedSchemeOut(BaseModel):
    id: int
    scheme: SchemeListOut
    saved_at: datetime

    class Config:
        from_attributes = True


# ---------- Notification ----------
class NotificationOut(BaseModel):
    id: int
    scheme_id: Optional[int]
    message: str
    is_read: bool
    created_at: datetime

    class Config:
        from_attributes = True


class UserProfileInput(BaseModel):

    age: Optional[int] = None
    gender: Optional[str] = None
    income: Optional[float] = None
    occupation: Optional[str] = None
    education: Optional[str] = None
    state: Optional[str] = None
    category: Optional[str] = None
    is_student: Optional[bool] = None
    is_farmer: Optional[bool] = None
    has_disability: Optional[bool] = None


class DirectEligibilityCheckRequest(BaseModel):
    scheme_id: Optional[int] = None
    category: Optional[str] = None
    profile: UserProfileInput


class DirectEligibilityCheckResponse(BaseModel):
    results: List[EligibilityEvaluationResult]


# ---------- Agent & Chatbot ----------
class RecommendedSchemeCard(BaseModel):
    scheme_id: int
    title: str
    department: Optional[str] = None
    target_group: Optional[str] = None
    benefits: Optional[str] = None
    eligibility_status: str
    reasons: List[str] = []
    missing_information: List[str] = []
    required_documents: List[str] = []
    application_steps: List[str] = []
    official_link: Optional[str] = None
    source_url: Optional[str] = None
    last_verified_at: Optional[str] = None
    data_confidence: str = "High (Official Source)"


class ChatRequest(BaseModel):
    message: str
    language: Optional[str] = None  # None allows automatic language detection
    conversation_history: Optional[List[dict]] = None
    session_id: Optional[str] = None


class ChatResponse(BaseModel):
    reply: str
    detected_language: str
    language_confidence: float = 1.0
    needs_language_clarification: bool = False
    schemes_recommended: List[RecommendedSchemeCard] = []
    follow_up_questions: List[str] = []
    missing_profile_fields: List[str] = []
    tool_calls_executed: List[str] = []
    disclaimer: str = (
        "Preliminary eligibility assessment provided by SmartGov AI. "
        "Does not constitute official government approval. Always refer to official government websites."
    )


# ---------- Scheme Update Service Models ----------
class SchemeUpdateHistoryOut(BaseModel):
    id: int
    scheme_id: Optional[int] = None
    scheme_title: str
    update_type: str
    field_changed: Optional[str] = None
    old_value: Optional[str] = None
    new_value: Optional[str] = None
    source_url: Optional[str] = None
    status: str
    details: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


class SchemeUpdateStatusResponse(BaseModel):
    last_successful_update: Optional[datetime] = None
    total_schemes_checked: int = 0
    updated_count: int = 0
    new_count: int = 0
    flagged_for_review_count: int = 0
    configured_sources: List[str] = []
    service_status: str = "operational"
    schedule_interval_hours: int = 24
    recent_history: List[SchemeUpdateHistoryOut] = []



# ---------- Family Member ----------
class FamilyMemberBase(BaseModel):
    name: str
    relation: str
    age: Optional[int] = None
    gender: Optional[str] = None
    income: Optional[float] = 0.0
    occupation: Optional[str] = None
    education: Optional[str] = None
    state: Optional[str] = None
    category: Optional[str] = None
    is_student: Optional[bool] = False
    is_farmer: Optional[bool] = False
    has_disability: Optional[bool] = False


class FamilyMemberCreate(FamilyMemberBase):
    pass


class FamilyMemberUpdate(FamilyMemberBase):
    pass


class FamilyMemberOut(FamilyMemberBase):
    id: int
    user_id: int
    created_at: datetime

    class Config:
        from_attributes = True


# ---------- Application Tracker ----------
class ApplicationCreate(BaseModel):
    scheme_id: int
    family_member_name: Optional[str] = None
    status: Optional[str] = "applied"
    application_reference: Optional[str] = None
    notes: Optional[str] = None


class ApplicationUpdate(BaseModel):
    status: Optional[str] = None
    application_reference: Optional[str] = None
    notes: Optional[str] = None


class ApplicationOut(BaseModel):
    id: int
    user_id: int
    scheme_id: int
    family_member_name: Optional[str] = None
    status: str
    application_reference: Optional[str] = None
    notes: Optional[str] = None
    applied_date: datetime
    updated_at: Optional[datetime] = None
    scheme: Optional[SchemeListOut] = None

    class Config:
        from_attributes = True


# ---------- Scheme Review ----------
class ReviewCreate(BaseModel):
    rating: int  # 1 to 5
    comment: Optional[str] = None


class ReviewOut(BaseModel):
    id: int
    user_id: int
    scheme_id: int
    rating: int
    comment: Optional[str] = None
    created_at: datetime
    user_name: Optional[str] = None

    class Config:
        from_attributes = True


class SchemeReviewStats(BaseModel):
    average_rating: float
    total_reviews: int
    reviews: List[ReviewOut] = []


# ---------- Admin Analytics ----------
class CategoryCount(BaseModel):
    category: str
    count: int


class StatusCount(BaseModel):
    status: str
    count: int


class AdminAnalyticsOut(BaseModel):
    total_users: int
    total_schemes: int
    total_applications: int
    total_saved: int
    total_reviews: int
    average_rating_overall: float
    schemes_by_category: List[CategoryCount]
    applications_by_status: List[StatusCount]
    recent_applications: List[ApplicationOut]
