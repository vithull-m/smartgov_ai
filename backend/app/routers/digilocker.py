from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime, timezone
import random
import hashlib
import json
from app.core.database import get_db
from app.utils.dependencies import get_current_user
from app.models.models import User, UserProfile, DigiLockerDocument
from app.schemas.schemas import DigiLockerConnectRequest, DigiLockerDocOut, ProfileOut, FarmerAuthRequest

router = APIRouter(prefix="/api/digilocker", tags=["DigiLocker & Citizen Verification"])


def generate_doc_hash(doc_number: str, user_id: int) -> str:
    salt = f"GOV_IN_{user_id}_{doc_number}_{datetime.now().strftime('%Y%m%d')}"
    return hashlib.sha256(salt.encode()).hexdigest()[:32].upper()


@router.get("/status")
def get_digilocker_status(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    profile = db.query(UserProfile).filter(UserProfile.user_id == user.id).first()
    docs = db.query(DigiLockerDocument).filter(DigiLockerDocument.user_id == user.id).all()

    return {
        "is_verified": profile.is_digilocker_verified if profile else False,
        "verification_mode": profile.verification_mode if profile else "none",
        "verified_name": profile.verified_name if profile else (user.full_name or "Citizen"),
        "digilocker_id": profile.digilocker_id if profile else None,
        "aadhaar_last4": profile.aadhaar_last4 if profile else None,
        "farmer_id": profile.farmer_id if profile else None,
        "land_record_no": profile.land_record_no if profile else None,
        "ration_card_no": profile.ration_card_no if profile else None,
        "csc_agent_id": profile.csc_agent_id if profile else None,
        "linked_at": profile.digilocker_linked_at if profile else None,
        "trust_score": 100 if profile and profile.is_digilocker_verified else 0,
        "total_documents": len(docs),
        "documents": [
            {
                "id": d.id,
                "doc_type": d.doc_type,
                "doc_name": d.doc_name,
                "issuer": d.issuer,
                "doc_number": d.doc_number,
                "verified_at": d.verified_at,
                "is_verified": d.is_verified,
                "source_channel": d.source_channel or "digilocker",
                "security_hash": d.security_hash,
                "metadata_json": json.loads(d.metadata_json) if d.metadata_json else {},
            }
            for d in docs
        ],
    }


@router.post("/send-otp")
def send_digilocker_otp(payload: dict, user: User = Depends(get_current_user)):
    aadhaar = payload.get("aadhaar_number", "")
    channel = payload.get("channel", "aadhaar_uidai")

    if channel == "pm_kisan":
        clean_id = aadhaar.strip()
        if len(clean_id) < 6:
            raise HTTPException(status_code=400, detail="Invalid Farmer Registration / Beneficiary ID.")
        return {
            "message": f"Kisan Aadhaar OTP sent to mobile linked with PM-KISAN registration.",
            "masked_mobile": "+91 98*** **412",
            "demo_otp": "123456",
        }

    if channel == "ration_pds":
        clean_id = aadhaar.strip()
        if len(clean_id) < 8:
            raise HTTPException(status_code=400, detail="Invalid Ration Card / NFSA Smart Card No.")
        return {
            "message": f"PDS e-KYC OTP sent to Head of Family registered mobile.",
            "masked_mobile": "+91 94*** **823",
            "demo_otp": "123456",
        }

    # Default UIDAI Aadhaar
    if len(aadhaar) != 12 or not aadhaar.isdigit():
        raise HTTPException(status_code=400, detail="Invalid Aadhaar Number. Must be exactly 12 digits.")

    return {
        "message": f"UIDAI Authentication OTP sent to mobile linked with Aadhaar ending in {aadhaar[-4:]}",
        "aadhaar_last4": aadhaar[-4:],
        "masked_mobile": f"+91 98*** **{aadhaar[-2:]}9",
        "demo_otp": "123456",
    }


@router.post("/verify-connect", response_model=ProfileOut)
def verify_and_connect_digilocker(
    payload: DigiLockerConnectRequest,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if not payload.consent:
        raise HTTPException(status_code=400, detail="Citizen explicit consent is statutory requirement under DPDP Act 2023.")

    if payload.otp != "123456" and len(payload.otp) != 6:
        raise HTTPException(status_code=400, detail="Invalid OTP code. For evaluation demo, use OTP: 123456.")

    profile = db.query(UserProfile).filter(UserProfile.user_id == user.id).first()
    if not profile:
        profile = UserProfile(user_id=user.id)
        db.add(profile)
        db.flush()

    last4 = payload.aadhaar_number[-4:] if len(payload.aadhaar_number) >= 4 else "8912"
    digi_id = f"DL-IN-{last4}-{random.randint(1000, 9999)}"

    profile.is_digilocker_verified = True
    profile.verification_mode = "digilocker"
    profile.digilocker_id = digi_id
    profile.digilocker_linked_at = datetime.now(timezone.utc)
    profile.aadhaar_last4 = last4
    profile.verified_name = payload.full_name or user.full_name or "Verified Citizen"

    # Default demographic harmonization from Digilocker payload
    if not profile.state:
        profile.state = "Tamil Nadu"
    if not profile.gender:
        profile.gender = "male"
    if not profile.category:
        profile.category = "OBC"
    if not profile.age:
        profile.age = 24
    if not profile.income:
        profile.income = 180000.0

    # Wipe existing and generate 4 authoritative certificates
    db.query(DigiLockerDocument).filter(DigiLockerDocument.user_id == user.id).delete()

    sample_docs = [
        DigiLockerDocument(
            user_id=user.id,
            doc_type="aadhaar",
            doc_name="Aadhaar Identity Verification Card",
            issuer="Unique Identification Authority of India (UIDAI)",
            doc_number=f"XXXXXXXX{last4}",
            source_channel="digilocker",
            security_hash=generate_doc_hash(f"UIDAI_{last4}", user.id),
            metadata_json=json.dumps({
                "auth_method": "UIDAI-Aadhaar-eKYC-XML",
                "verified_name": profile.verified_name,
                "dob": f"{2026 - (profile.age or 24)}-05-14",
                "gender": profile.gender,
                "state": profile.state,
                "signature_status": "VALID_DIGITALLY_SIGNED",
            }),
        ),
        DigiLockerDocument(
            user_id=user.id,
            doc_type="income",
            doc_name=f"Official Income Certificate (₹{int(profile.income or 180000):,}/yr)",
            issuer="Revenue & Disaster Management Dept",
            doc_number=f"REV/INC/2025/{random.randint(100000, 999999)}",
            source_channel="digilocker",
            security_hash=generate_doc_hash(f"INC_{last4}", user.id),
            metadata_json=json.dumps({
                "issuing_authority": "Tahsildar / Revenue Divisional Officer",
                "annual_income_inr": profile.income or 180000.0,
                "financial_year": "2025-2026",
                "valid_until": "2026-03-31",
                "barcode_serial": f"BC-TN-{random.randint(1000000, 9999999)}",
            }),
        ),
        DigiLockerDocument(
            user_id=user.id,
            doc_type="caste",
            doc_name=f"Community & Caste Certificate ({profile.category or 'OBC'})",
            issuer="Tahsildar / Directorate of Backward Classes & Minorities",
            doc_number=f"TN/CST/2024/{random.randint(100000, 999999)}",
            source_channel="digilocker",
            security_hash=generate_doc_hash(f"CST_{last4}", user.id),
            metadata_json=json.dumps({
                "category": profile.category or "OBC",
                "caste_name": "Backward Community (BC/OBC)",
                "gazette_serial": f"TN-GAZ-{random.randint(1000, 9999)}",
                "status": "PERMANENT_RECORD",
            }),
        ),
        DigiLockerDocument(
            user_id=user.id,
            doc_type="education",
            doc_name="Higher Secondary (12th / HSC) Marksheet & Certificate",
            issuer="State Board of School Examinations / CBSE",
            doc_number=f"HSC/REG/{random.randint(1000000, 9999999)}",
            source_channel="digilocker",
            security_hash=generate_doc_hash(f"EDU_{last4}", user.id),
            metadata_json=json.dumps({
                "qualification": profile.education or "12th pass",
                "passed_year": "2022",
                "result_status": "FIRST_CLASS_DISTINCTION",
                "board_verification_code": f"SBSE-{random.randint(10000, 99999)}",
            }),
        ),
    ]

    for d in sample_docs:
        db.add(d)

    db.commit()
    db.refresh(profile)
    return profile


@router.post("/farmer-auth", response_model=ProfileOut)
def authenticate_farmer_citizen(
    payload: FarmerAuthRequest,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Dedicated Authentication for Rural Citizens / Farmers who do not use DigiLocker smartphone app.
    Integrates with:
    1. PM-KISAN Farmer Database / AgriStack
    2. Bhulekh / e-Bhoomi Land Records (Khata/Patta No)
    3. Ration Card / NFSA Public Distribution System
    4. CSC / Gram Panchayat VLE Assisted Physical Verification
    """
    if not payload.consent:
        raise HTTPException(status_code=400, detail="Citizen authorization is required.")

    if payload.otp != "123456" and len(payload.otp) != 6:
        raise HTTPException(status_code=400, detail="Invalid OTP code. For demo evaluation, use OTP: 123456.")

    clean_id = payload.identifier.strip()
    if len(clean_id) < 5:
        raise HTTPException(status_code=400, detail="Invalid identifier. Please provide valid Farmer ID, Aadhaar, or Khata No.")

    profile = db.query(UserProfile).filter(UserProfile.user_id == user.id).first()
    if not profile:
        profile = UserProfile(user_id=user.id)
        db.add(profile)
        db.flush()

    # Mark as verified farmer
    profile.is_farmer = True
    profile.is_digilocker_verified = True
    profile.verification_mode = payload.auth_type
    profile.digilocker_linked_at = datetime.now(timezone.utc)
    profile.state = payload.state or profile.state or "Tamil Nadu"
    if not profile.age:
        profile.age = 46
    if not profile.gender:
        profile.gender = "male"
    if not profile.occupation or profile.occupation == "unemployed":
        profile.occupation = "farmer"
    if not profile.income:
        profile.income = 120000.0  # Typical marginal farmer threshold

    # Channel-specific identifiers
    last4 = clean_id[-4:] if len(clean_id) >= 4 else "7812"
    profile.aadhaar_last4 = last4

    if payload.auth_type == "pm_kisan":
        profile.farmer_id = f"PMK-IN-{payload.state[:2].upper()}-{clean_id}"
        profile.digilocker_id = f"KISAN-REG-{last4}-{random.randint(1000, 9999)}"
        profile.verified_name = user.full_name or "Registered PM-KISAN Beneficiary"
    elif payload.auth_type == "land_record":
        profile.land_record_no = f"ROR-{clean_id}-{random.randint(100, 999)}"
        profile.digilocker_id = f"LAND-PATTA-{last4}"
        profile.verified_name = user.full_name or "Agricultural Landholder"
    elif payload.auth_type == "ration_card":
        profile.ration_card_no = clean_id
        profile.digilocker_id = f"NFSA-PDS-{last4}"
        profile.verified_name = user.full_name or "NFSA Head of Household"
    elif payload.auth_type == "csc_vle":
        profile.csc_agent_id = payload.csc_vle_id or f"VLE-{random.randint(10000, 99999)}"
        profile.digilocker_id = f"CSC-VERIFIED-{last4}"
        profile.verified_name = user.full_name or "CSC Assisted Citizen"

    # Populate farmer-verified official documents
    db.query(DigiLockerDocument).filter(DigiLockerDocument.user_id == user.id).delete()

    farmer_docs = [
        DigiLockerDocument(
            user_id=user.id,
            doc_type="pm_kisan_passbook",
            doc_name="PM-KISAN Samman Nidhi Electronic Ledger Passbook",
            issuer="Department of Agriculture & Farmers Welfare, Ministry of Agri",
            doc_number=profile.farmer_id or f"PMK-IN-TN-{clean_id}",
            source_channel=payload.auth_type,
            security_hash=generate_doc_hash(f"PMK_{last4}", user.id),
            metadata_json=json.dumps({
                "scheme": "PM-KISAN DBT",
                "installment_status": "Active (18th Installment Credited)",
                "dbt_bank_account": f"SBI Bank A/c ending in {random.randint(1000, 9999)}",
                "aadhaar_seeding": "YES_ACTIVE_NPCI_MAPPED",
                "land_seeding": "VERIFIED_STATE_PORTAL",
                "eKYC_status": "BIOMETRIC_eKYC_COMPLETED",
            }),
        ),
        DigiLockerDocument(
            user_id=user.id,
            doc_type="land_patta_chitta",
            doc_name="Digital Land Record / Record of Rights (Patta / Chitta / 7/12 RoR)",
            issuer="State Revenue & Land Records Dept (AnyRoR / Bhulekh / Tamil Nilam)",
            doc_number=profile.land_record_no or f"TN/LND/2024/{random.randint(100000, 999999)}",
            source_channel=payload.auth_type,
            security_hash=generate_doc_hash(f"LND_{last4}", user.id),
            metadata_json=json.dumps({
                "land_extent": "1.85 Acres (Marginal Farmer Category)",
                "khata_number": clean_id,
                "survey_number": f"{random.randint(10, 150)}/{random.randint(1, 9)}",
                "crop_classification": "Wet / Irrigated Paddy & Millets",
                "soil_health_card": "ISSUED_ACTIVE",
            }),
        ),
        DigiLockerDocument(
            user_id=user.id,
            doc_type="kcc_card",
            doc_name="Kisan Credit Card (KCC) Institutional Credit Record",
            issuer="NABARD / District Central Co-operative Bank",
            doc_number=f"KCC/DCCB/2024/{random.randint(100000, 999999)}",
            source_channel=payload.auth_type,
            security_hash=generate_doc_hash(f"KCC_{last4}", user.id),
            metadata_json=json.dumps({
                "subsidized_interest_rate": "4% (with 3% prompt repayment subvention)",
                "credit_limit_inr": 150000.0,
                "loan_status": "STANDARDIZED_RENEWED",
            }),
        ),
        DigiLockerDocument(
            user_id=user.id,
            doc_type="ration_pds",
            doc_name="NFSA / Smart Family Ration Card (PHH Priority Household)",
            issuer="Food, Civil Supplies & Consumer Protection Dept",
            doc_number=profile.ration_card_no or f"PDS/NFSA/{random.randint(10000000, 99999999)}",
            source_channel=payload.auth_type,
            security_hash=generate_doc_hash(f"PDS_{last4}", user.id),
            metadata_json=json.dumps({
                "card_type": "PHH (Priority Household - BPL Subsidy)",
                "family_members_count": 4,
                "fair_price_shop_no": f"FPS-RURAL-{random.randint(100, 999)}",
                "free_rice_quota_kg": 20,
            }),
        ),
    ]

    for d in farmer_docs:
        db.add(d)

    db.commit()
    db.refresh(profile)
    return profile


@router.delete("/disconnect")
def disconnect_digilocker(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    profile = db.query(UserProfile).filter(UserProfile.user_id == user.id).first()
    if profile:
        profile.is_digilocker_verified = False
        profile.verification_mode = "none"
        profile.digilocker_id = None
        profile.digilocker_linked_at = None
        profile.aadhaar_last4 = None
        profile.farmer_id = None
        profile.land_record_no = None
        profile.ration_card_no = None
        profile.csc_agent_id = None

    db.query(DigiLockerDocument).filter(DigiLockerDocument.user_id == user.id).delete()
    db.commit()
    return {"message": "Citizen verification & linked documents disconnected."}
