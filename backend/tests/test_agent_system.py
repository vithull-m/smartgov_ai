"""
Comprehensive test suite for SmartGov AI.
Covers:
- Automatic language detection (Tamil, English, Tanglish, Hindi)
- Deterministic eligibility engine rules (eligible, ineligible, incomplete profile, unverified data)
- Real agent tools execution
- Scheme update service duplicate prevention & history logging
- API endpoints (chat, eligibility check, update status, health)
"""
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient

from app.core.database import Base
from app.models.models import Scheme, EligibilityRule, SchemeDocument, ApplicationStep, SchemeUpdateHistory
from app.services.language_detector import detect_language
from app.services.eligibility_engine import (
    evaluate_scheme_detailed,
    EligibilityStatus,
    UserProfileInput,
)
from app.services.agent_tools import (
    search_schemes,
    check_eligibility,
    get_required_documents,
    get_application_steps,
    get_scheme_source,
    check_update_status,
)
from app.services.scheme_updater import SchemeUpdateService
from app.main import app


# Setup in-memory test database
TEST_DB_URL = "sqlite:///:memory:"
test_engine = create_engine(TEST_DB_URL)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)


@pytest.fixture(scope="function")
def test_db():
    Base.metadata.create_all(bind=test_engine)
    db = TestingSessionLocal()
    try:
        # Populate verified test scheme
        scholarship = Scheme(
            id=1,
            title="National Merit Scholarship",
            department="Ministry of Education",
            description="College scholarship for students from low-income families",
            benefits="Rs. 50,000 per year",
            category="Education",
            target_group="Students",
            state="All India",
            official_link="https://scholarships.gov.in",
            source_url="https://scholarships.gov.in",
            source_status="verified",
            provenance_note="Official National Portal Verified",
            is_active=True,
        )
        db.add(scholarship)

        # Rules
        db.add(EligibilityRule(scheme_id=1, field_name="is_student", operator="eq", value="true", description="Must be student"))
        db.add(EligibilityRule(scheme_id=1, field_name="income", operator="lte", value="250000", description="Income must be <= 2.5L"))
        db.add(EligibilityRule(scheme_id=1, field_name="age", operator="lte", value="25", description="Age must be <= 25"))

        # Documents
        db.add(SchemeDocument(scheme_id=1, document_name="Aadhaar Card", is_mandatory=True))
        db.add(SchemeDocument(scheme_id=1, document_name="College ID", is_mandatory=True))

        # Steps
        db.add(ApplicationStep(scheme_id=1, step_number=1, instruction="Apply on NSP"))

        # Unverified test scheme
        unverified_scheme = Scheme(
            id=2,
            title="Unverified Regional Subsidy",
            department="State Dept",
            category="Agriculture",
            source_status="unverified",
            is_active=True,
        )
        db.add(unverified_scheme)

        db.commit()
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=test_engine)


# 1. Tests for Language Detection
def test_language_detection_tamil():
    lang, conf, _ = detect_language("நான் ஒரு கல்லூரி மாணவர், எனக்கு என்ன உதவித்தொகை கிடைக்கும்?")
    assert lang == "ta"
    assert conf > 0.7


def test_language_detection_english():
    lang, conf, _ = detect_language("I am a college student. Which scholarships can I apply for?")
    assert lang == "en"
    assert conf > 0.7


def test_language_detection_tanglish():
    lang, conf, _ = detect_language("Enakku college scholarship kedaikkuma thittam solunga?")
    assert lang == "ta"


def test_language_detection_hindi():
    lang, conf, _ = detect_language("प्रधानमंत्री किसान सम्मान निधि योजना के बारे में बताएं")
    assert lang == "hi"


# 2. Tests for Eligibility Engine
def test_eligibility_likely_eligible(test_db):
    scheme = test_db.query(Scheme).filter(Scheme.id == 1).first()
    profile = UserProfileInput(is_student=True, income=180000, age=20)
    result = evaluate_scheme_detailed(scheme, profile)
    assert result.status == EligibilityStatus.LIKELY_ELIGIBLE
    assert result.is_eligible is True
    assert result.match_score == 100.0


def test_eligibility_ineligible(test_db):
    scheme = test_db.query(Scheme).filter(Scheme.id == 1).first()
    # Income exceeds 250000
    profile = UserProfileInput(is_student=True, income=500000, age=20)
    result = evaluate_scheme_detailed(scheme, profile)
    assert result.status == EligibilityStatus.NOT_ELIGIBLE
    assert result.is_eligible is False
    assert len(result.failed_conditions) > 0


def test_eligibility_missing_information(test_db):
    scheme = test_db.query(Scheme).filter(Scheme.id == 1).first()
    # Student is true, but income and age are missing (None)
    profile = UserProfileInput(is_student=True)
    result = evaluate_scheme_detailed(scheme, profile)
    assert result.status == EligibilityStatus.NEEDS_MORE_INFO
    assert result.is_eligible is False
    assert "Annual family income" in result.missing_information
    assert "Age" in result.missing_information


def test_eligibility_unverified_scheme_data(test_db):
    scheme = test_db.query(Scheme).filter(Scheme.id == 2).first()
    profile = UserProfileInput(is_student=True, income=100000)
    result = evaluate_scheme_detailed(scheme, profile)
    assert result.status == EligibilityStatus.UNVERIFIED
    assert result.is_eligible is False


# 3. Tests for Real Agent Tools
def test_agent_tools_search_and_provenance(test_db):
    results = search_schemes("National Merit", test_db)
    assert len(results) == 1
    assert results[0]["title"] == "National Merit Scholarship"

    docs = get_required_documents(1, test_db)
    assert len(docs) == 2
    assert docs[0]["document_name"] == "Aadhaar Card"

    steps = get_application_steps(1, test_db)
    assert len(steps) == 1

    source = get_scheme_source(1, test_db)
    assert source["source_status"] == "verified"
    assert "scholarships.gov.in" in source["official_link"]


# 4. Tests for Scheme Update Service & Duplicate Prevention
def test_scheme_update_duplicate_prevention(test_db):
    # Try updating existing scheme
    update_data = {
        "title": "National Merit Scholarship",
        "benefits": "Updated Rs. 60,000 per year",
    }
    res = SchemeUpdateService.sync_verified_scheme(
        scheme_data=update_data,
        source_url="https://scholarships.gov.in/update",
        db=test_db,
    )
    assert res["success"] is True
    assert res["action"] == "updated"

    # Verify no duplicate scheme created
    count = test_db.query(Scheme).filter(Scheme.title == "National Merit Scholarship").count()
    assert count == 1

    # Verify change was logged in update history
    history = test_db.query(SchemeUpdateHistory).filter(SchemeUpdateHistory.scheme_id == 1).first()
    assert history is not None
    assert history.field_changed == "benefits"


# 5. Tests for API Endpoints using TestClient
def test_api_health_endpoint():
    client = TestClient(app)
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


def test_api_chat_endpoint_multilingual():
    client = TestClient(app)
    
    # Tamil test message
    ta_resp = client.post("/api/chatbot", json={"message": "கல்லூரி மாணவர்களுக்கான உதவித்தொகை என்ன?"})
    assert ta_resp.status_code == 200
    data = ta_resp.json()
    assert data["detected_language"] == "ta"
    assert len(data["reply"]) > 0
    assert "detect_language" in data["tool_calls_executed"]

    # English test message
    en_resp = client.post("/api/chatbot", json={"message": "I am a farmer looking for subsidy schemes"})
    assert en_resp.status_code == 200
    assert en_resp.json()["detected_language"] == "en"


def test_api_updates_status_endpoint():
    client = TestClient(app)
    response = client.get("/api/updates/status")
    assert response.status_code == 200
    data = response.json()
    assert "configured_sources" in data
    assert data["service_status"] == "operational"
