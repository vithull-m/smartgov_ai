"""
Deterministic, verified Government Scheme Eligibility Engine.
Strictly evaluates rules against citizen profile data.
Does NOT guess or use AI models to decide eligibility.
Returns one of:
- 'likely_eligible'
- 'not_eligible'
- 'needs_more_information'
- 'unverified_scheme_data'
"""
from typing import List, Tuple, Dict, Any, Optional
from datetime import datetime
from app.models.models import Scheme, EligibilityRule, UserProfile
from app.schemas.schemas import EligibilityEvaluationResult, EligibilityStatus, UserProfileInput

FIELD_LABELS = {
    "age": "Age",
    "income": "Annual family income",
    "gender": "Gender",
    "occupation": "Occupation",
    "education": "Education level",
    "state": "State of residence",
    "category": "Caste / Social category",
    "is_student": "Student status",
    "is_farmer": "Farmer status",
    "has_disability": "Disability status",
}

OPERATOR_LABELS = {
    "eq": "equal to",
    "neq": "not equal to",
    "lte": "at most",
    "gte": "at least",
    "lt": "less than",
    "gt": "greater than",
    "in": "one of",
}


def _get_val(profile: Any, field_name: str):
    """Retrieve field value from either UserProfile OR UserProfileInput / dict."""
    if profile is None:
        return None
    if isinstance(profile, dict):
        return profile.get(field_name)
    return getattr(profile, field_name, None)


def _eval_single_rule(rule: EligibilityRule, profile: Any) -> Tuple[Optional[bool], str]:
    """
    Evaluates a single rule.
    Returns:
        (is_passed, label) where is_passed is True, False, or None (if field is missing/unknown)
    """
    actual = _get_val(profile, rule.field_name)
    field_label = FIELD_LABELS.get(rule.field_name, rule.field_name)
    op_label = OPERATOR_LABELS.get(rule.operator, rule.operator)
    desc = rule.description or f"{field_label} must be {op_label} {rule.value}"

    if actual is None:
        # Unknown/missing value: do NOT assume True or False
        return None, desc

    op = rule.operator.strip().lower()
    raw_value = str(rule.value).strip()

    # Boolean fields
    if isinstance(actual, bool) or str(actual).lower() in ("true", "false", "yes", "no"):
        if isinstance(actual, str):
            actual_bool = actual.lower() in ("true", "1", "yes")
        else:
            actual_bool = bool(actual)
        expected_bool = raw_value.lower() in ("true", "1", "yes")
        passed = (actual_bool == expected_bool) if op == "eq" else (actual_bool != expected_bool)
        return passed, desc

    # Numeric fields (age, income)
    if isinstance(actual, (int, float)) or (isinstance(actual, str) and actual.replace(".", "", 1).isdigit()):
        try:
            actual_num = float(actual)
            if op == "in":
                allowed = [float(v.strip()) for v in raw_value.split(",")]
                return (actual_num in allowed), desc
            expected_num = float(raw_value)
            if op == "eq":
                return (actual_num == expected_num), desc
            elif op == "neq":
                return (actual_num != expected_num), desc
            elif op == "lte":
                return (actual_num <= expected_num), desc
            elif op == "gte":
                return (actual_num >= expected_num), desc
            elif op == "lt":
                return (actual_num < expected_num), desc
            elif op == "gt":
                return (actual_num > expected_num), desc
            return False, desc
        except ValueError:
            return False, desc

    # String fields (gender, occupation, state, category, education)
    actual_str = str(actual).strip().lower()
    if op == "in":
        allowed = [v.strip().lower() for v in raw_value.split(",")]
        return (actual_str in allowed), desc
    elif op == "eq":
        return (actual_str == raw_value.lower()), desc
    elif op == "neq":
        return (actual_str != raw_value.lower()), desc

    return False, desc


def evaluate_scheme_detailed(scheme: Scheme, profile: Any) -> EligibilityEvaluationResult:
    """
    Evaluates a scheme against profile, returning an EligibilityEvaluationResult
    with strictly verified status:
    - likely_eligible
    - not_eligible
    - needs_more_information
    - unverified_scheme_data
    """
    doc_names = [d.document_name for d in scheme.documents] if scheme.documents else []

    # 1. Check for unverified scheme data or missing provenance
    is_source_unverified = getattr(scheme, "source_status", "verified") in ("unverified", "needs_review")
    if is_source_unverified:
        return EligibilityEvaluationResult(
            scheme_id=scheme.id,
            title=scheme.title,
            status=EligibilityStatus.UNVERIFIED,
            match_score=0.0,
            is_eligible=False,
            passed_conditions=[],
            failed_conditions=["Scheme details are currently unverified and require administrative audit."],
            missing_information=[],
            required_documents=doc_names,
            official_link=scheme.official_link,
            source_url=getattr(scheme, "source_url", None),
            last_verified_at=getattr(scheme, "last_verified_at", None),
            source_status=getattr(scheme, "source_status", "unverified"),
        )

    # 2. If scheme has no rules, everyone is likely eligible
    if not scheme.rules:
        return EligibilityEvaluationResult(
            scheme_id=scheme.id,
            title=scheme.title,
            status=EligibilityStatus.LIKELY_ELIGIBLE,
            match_score=100.0,
            is_eligible=True,
            passed_conditions=["Universal access: No restrictive criteria specified."],
            failed_conditions=[],
            missing_information=[],
            required_documents=doc_names,
            official_link=scheme.official_link,
            source_url=getattr(scheme, "source_url", None),
            last_verified_at=getattr(scheme, "last_verified_at", None),
            source_status=getattr(scheme, "source_status", "verified"),
        )

    passed_conditions: List[str] = []
    failed_conditions: List[str] = []
    missing_information: List[str] = []

    for rule in scheme.rules:
        result, desc = _eval_single_rule(rule, profile)
        if result is True:
            passed_conditions.append(desc)
        elif result is False:
            failed_conditions.append(desc)
        else:
            # Result is None: profile value not supplied
            field_name = rule.field_name
            readable = FIELD_LABELS.get(field_name, field_name)
            missing_information.append(readable)

    total_rules = len(scheme.rules)
    score = round((len(passed_conditions) / max(total_rules, 1)) * 100, 1)

    # Determine status
    if len(failed_conditions) > 0:
        status = EligibilityStatus.NOT_ELIGIBLE
        is_eligible = False
    elif len(missing_information) > 0:
        status = EligibilityStatus.NEEDS_MORE_INFO
        is_eligible = False
    else:
        status = EligibilityStatus.LIKELY_ELIGIBLE
        is_eligible = True

    return EligibilityEvaluationResult(
        scheme_id=scheme.id,
        title=scheme.title,
        status=status,
        match_score=score,
        is_eligible=is_eligible,
        passed_conditions=passed_conditions,
        failed_conditions=failed_conditions,
        missing_information=list(dict.fromkeys(missing_information)),
        required_documents=doc_names,
        official_link=scheme.official_link,
        source_url=getattr(scheme, "source_url", None),
        last_verified_at=getattr(scheme, "last_verified_at", None),
        source_status=getattr(scheme, "source_status", "verified"),
    )


# Backward-compatible function for existing routers
def evaluate_scheme(scheme: Scheme, profile: UserProfile) -> Tuple[float, bool, List[str], List[str]]:
    detailed = evaluate_scheme_detailed(scheme, profile)
    return (
        detailed.match_score,
        detailed.is_eligible,
        detailed.passed_conditions,
        detailed.failed_conditions or [f"Missing information: {', '.join(detailed.missing_information)}"] if detailed.missing_information else detailed.failed_conditions,
    )


def recommend_schemes(schemes: List[Scheme], profile: UserProfile, min_score: float = 1.0):
    results = []
    for scheme in schemes:
        detailed = evaluate_scheme_detailed(scheme, profile)
        if detailed.match_score >= min_score or detailed.status == EligibilityStatus.NEEDS_MORE_INFO:
            results.append({
                "scheme_id": scheme.id,
                "title": scheme.title,
                "status": detailed.status,
                "match_score": detailed.match_score,
                "is_eligible": detailed.is_eligible,
                "matched_reasons": detailed.passed_conditions,
                "unmatched_reasons": detailed.failed_conditions,
                "missing_information": detailed.missing_information,
                "required_documents": detailed.required_documents,
                "official_link": detailed.official_link,
            })
    results.sort(key=lambda r: (r["is_eligible"], r["match_score"]), reverse=True)
    return results
