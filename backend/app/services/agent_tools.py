"""
Agent tools implementation for SmartGov AI.
These real Python functions allow the agent to query the verified database
and evaluate eligibility deterministically without inventing data.
"""
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from sqlalchemy import or_
from app.models.models import Scheme, SchemeDocument, ApplicationStep, UserProfile, SchemeUpdateHistory
from app.services.eligibility_engine import evaluate_scheme_detailed, EligibilityStatus
from app.services.language_detector import detect_language as detect_lang_service


def detect_language(text: str) -> Dict[str, Any]:
    """Detect language and return language code and confidence."""
    lang, conf, needs_clar = detect_lang_service(text)
    return {
        "language": lang,
        "confidence": conf,
        "needs_clarification": needs_clar,
    }


def search_schemes(query: str, db: Session, limit: int = 6) -> List[Dict[str, Any]]:
    """
    Search schemes in SQLite database using title, description, category, or target group.
    """
    q = query.strip()
    if not q:
        schemes = db.query(Scheme).filter(Scheme.is_active == True).limit(limit).all()  # noqa: E712
    else:
        schemes = db.query(Scheme).filter(
            Scheme.is_active == True,  # noqa: E712
            or_(
                Scheme.title.ilike(f"%{q}%"),
                Scheme.description.ilike(f"%{q}%"),
                Scheme.category.ilike(f"%{q}%"),
                Scheme.target_group.ilike(f"%{q}%"),
                Scheme.department.ilike(f"%{q}%"),
            )
        ).limit(limit).all()

    results = []
    for s in schemes:
        results.append({
            "id": s.id,
            "title": s.title,
            "category": s.category,
            "department": s.department,
            "target_group": s.target_group,
            "state": s.state,
            "benefits": s.benefits,
            "official_link": s.official_link,
            "source_url": getattr(s, "source_url", None) or s.official_link,
            "source_status": getattr(s, "source_status", "verified"),
            "last_verified_at": str(getattr(s, "last_verified_at", "") or ""),
        })
    return results


def get_scheme_details(scheme_id: int, db: Session) -> Optional[Dict[str, Any]]:
    """Get full details of a specific scheme."""
    scheme = db.query(Scheme).filter(Scheme.id == scheme_id).first()
    if not scheme:
        return None

    docs = [
        {"name": d.document_name, "is_mandatory": d.is_mandatory}
        for d in scheme.documents
    ]
    steps = [
        {"step_number": st.step_number, "instruction": st.instruction}
        for st in scheme.steps
    ]
    rules = [
        {"field": r.field_name, "operator": r.operator, "value": r.value, "description": r.description}
        for r in scheme.rules
    ]

    return {
        "id": scheme.id,
        "title": scheme.title,
        "department": scheme.department,
        "category": scheme.category,
        "target_group": scheme.target_group,
        "description": scheme.description,
        "benefits": scheme.benefits,
        "state": scheme.state,
        "official_link": scheme.official_link,
        "source_url": getattr(scheme, "source_url", None) or scheme.official_link,
        "source_status": getattr(scheme, "source_status", "verified"),
        "last_verified_at": str(getattr(scheme, "last_verified_at", "") or ""),
        "provenance_note": getattr(scheme, "provenance_note", "Official National Portal Verified"),
        "documents": docs,
        "application_steps": steps,
        "rules": rules,
    }


def check_eligibility(scheme_id: int, profile_data: Dict[str, Any], db: Session) -> Dict[str, Any]:
    """
    Check citizen eligibility for a scheme using deterministic engine.
    """
    scheme = db.query(Scheme).filter(Scheme.id == scheme_id).first()
    if not scheme:
        return {"error": f"Scheme with ID {scheme_id} not found"}

    result = evaluate_scheme_detailed(scheme, profile_data)
    return {
        "scheme_id": scheme.id,
        "title": scheme.title,
        "status": result.status,
        "match_score": result.match_score,
        "is_eligible": result.is_eligible,
        "passed_conditions": result.passed_conditions,
        "failed_conditions": result.failed_conditions,
        "missing_information": result.missing_information,
        "required_documents": result.required_documents,
        "official_link": result.official_link,
        "source_status": result.source_status,
        "disclaimer": result.disclaimer,
    }


def get_required_documents(scheme_id: int, db: Session) -> List[Dict[str, Any]]:
    """Retrieve verified required documents for a scheme."""
    docs = db.query(SchemeDocument).filter(SchemeDocument.scheme_id == scheme_id).all()
    return [
        {"document_name": d.document_name, "is_mandatory": d.is_mandatory}
        for d in docs
    ]


def get_application_steps(scheme_id: int, db: Session) -> List[Dict[str, Any]]:
    """Retrieve ordered application steps for a scheme."""
    steps = db.query(ApplicationStep).filter(ApplicationStep.scheme_id == scheme_id).order_by(ApplicationStep.step_number).all()
    return [
        {"step_number": s.step_number, "instruction": s.instruction}
        for s in steps
    ]


def get_scheme_source(scheme_id: int, db: Session) -> Dict[str, Any]:
    """Retrieve provenance information and official source link for a scheme."""
    scheme = db.query(Scheme).filter(Scheme.id == scheme_id).first()
    if not scheme:
        return {"error": "Scheme not found"}
    return {
        "scheme_id": scheme.id,
        "title": scheme.title,
        "official_link": scheme.official_link,
        "source_url": getattr(scheme, "source_url", None) or scheme.official_link,
        "source_status": getattr(scheme, "source_status", "verified"),
        "government_level": getattr(scheme, "government_level", "Central"),
        "last_verified_at": str(getattr(scheme, "last_verified_at", "") or ""),
        "last_checked_at": str(getattr(scheme, "last_checked_at", "") or ""),
        "provenance_note": getattr(scheme, "provenance_note", "Official National Portal Verified"),
    }


def check_update_status(db: Session) -> Dict[str, Any]:
    """Retrieve scheme database update and verification status."""
    latest_update = db.query(SchemeUpdateHistory).order_by(SchemeUpdateHistory.created_at.desc()).first()
    total_schemes = db.query(Scheme).count()
    verified_schemes = db.query(Scheme).filter(Scheme.source_status == "verified").count()
    needs_review = db.query(Scheme).filter(Scheme.source_status == "needs_review").count()

    return {
        "service_status": "operational",
        "total_schemes": total_schemes,
        "verified_schemes": verified_schemes,
        "schemes_needing_review": needs_review,
        "last_update_timestamp": str(latest_update.created_at) if latest_update else None,
        "last_update_type": latest_update.update_type if latest_update else "seed",
    }
