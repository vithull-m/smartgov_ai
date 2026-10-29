"""
SmartGov AI Agent Orchestrator.
Coordinates:
1. Automatic Language Detection (Tamil, English, Hindi, Tanglish, Indian scripts)
2. Intent Analysis & Information Extraction
3. Real Python Tool Execution:
   - detect_language
   - search_schemes
   - get_scheme_details
   - check_eligibility
   - get_required_documents
   - get_application_steps
   - get_scheme_source
   - check_update_status
4. Cloud AI Model reasoning layer (OpenAI / configured LLM) with graceful fallback
5. Explanations in the user's detected language with accurate scheme names, official URLs,
   and clear distinction between verified data and preliminary estimates.
"""
import logging
import re
from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session
from app.core.config import settings
from app.services.language_detector import detect_language
from app.services.agent_tools import (
    search_schemes,
    get_scheme_details,
    check_eligibility,
    get_required_documents,
    get_application_steps,
    get_scheme_source,
    check_update_status,
)
from app.services.eligibility_engine import EligibilityStatus
from app.schemas.schemas import RecommendedSchemeCard, ChatResponse
from app.models.models import User, UserProfile, Scheme

logger = logging.getLogger(__name__)

# System instructions for LLM
AGENT_SYSTEM_PROMPT = """You are SmartGov AI, an official multilingual Indian Government Schemes Assistant.
You assist citizens with scholarships, farming subsidies, health coverage, pension, women empowerment, and loans.

CRITICAL INSTRUCTIONS:
1. Speak in the EXACT language used by the user: {language_name}. If the user typed Tamil or Tanglish, reply in clear Tamil. If English, reply in English. If Hindi, reply in Hindi.
2. KEEP SCHEME NAMES AND OFFICIAL URLs ACCURATE AND UNTRANSLATED (e.g. keep 'PM-KISAN Samman Nidhi', 'https://pmkisan.gov.in', 'scholarships.gov.in').
3. DO NOT INVENT or hallucinate schemes, rules, income limits, or deadlines.
4. Ground your answer in the verified scheme database tools provided below.
5. If the user's question lacks details (like age, student status, or income), ask for ONLY the missing details politely.
6. Clearly state that preliminary eligibility assessment does not guarantee government approval.

Database Grounding Context:
{context}
"""

INTENT_KEYWORDS = {
    "scholarship": ["scholarship", "study", "college", "student", "degree", "fees", "கல்வி", "மாணவர்", "மாணவி", "படிப்ப", "छात्रवृत्ति", "पढ़ाई"],
    "farmer": ["farmer", "kisan", "crop", "agriculture", "land", "patta", "விவசாயி", "விவசாயம்", "நிலம்", "किसान", "खेती"],
    "health": ["health", "hospital", "medical", "treatment", "ayushman", "maruthuvam", "மருத்துவம்", "சிகிச்சை", "स्वास्थ्य", "इलाज"],
    "women": ["woman", "women", "girl", "daughter", "mahila", "pen", "pengal", "பெண்", "மகளிர்", "महिला", "बेटी"],
    "housing": ["house", "housing", "awas", "pmay", "veedu", "வீடு", "घर", "मकान"],
    "loan": ["loan", "business", "mudra", "svanidhi", "kadan", "சுயதொழில்", "கடன்", "ऋण", "लोन"],
    "pension": ["pension", "old age", "senior", "elder", "oap", "oyvudhiyam", "முதியோர்", "ஓய்வூதியம்", "पेंशन", "वृद्धावस्था"],
    "disability": ["disability", "disabled", "handicapped", "divyang", "maatrudhiranali", "மாற்றுத்திறனாளி", "दिव्यांग"],
}


def _extract_profile_hints(text: str) -> Dict[str, Any]:
    """Extract profile clues from user query without asking unnecessary questions."""
    lower = text.lower()
    hints: Dict[str, Any] = {}

    if any(k in lower for k in ["student", "college", "school", "studying", "degree", "மாணவர்", "மாணவி", "छात्र"]):
        hints["is_student"] = True
    if any(k in lower for k in ["farmer", "agriculture", "farming", "landowner", "விவசாயி", "किसान"]):
        hints["is_farmer"] = True
    if any(k in lower for k in ["disabled", "disability", "handicapped", "மாற்றுத்திறனாளி", "दिव्यांग"]):
        hints["has_disability"] = True
    if any(k in lower for k in ["female", "woman", "girl", "mother", "daughter", "பெண்", "महिला", "लड़की"]):
        hints["gender"] = "Female"
    elif any(k in lower for k in ["male", "boy", "son", "father", "ஆண்", "पुरुष"]):
        hints["gender"] = "Male"

    # Age pattern (e.g. 20 years old, age 22, வயது 20)
    age_match = re.search(r"(?:age|வயது|आयु)\s*(?:is|:)?\s*(\d{1,2})", lower) or re.search(r"(\d{1,2})\s*(?:years old|yrs old|வருடம்|வயது)", lower)
    if age_match:
        try:
            hints["age"] = int(age_match.group(1))
        except ValueError:
            pass

    # Income pattern (e.g. income 150000, 2 lakh income)
    if "lakh" in lower:
        lakh_match = re.search(r"(\d+(?:\.\d+)?)\s*lakh", lower)
        if lakh_match:
            try:
                hints["income"] = float(lakh_match.group(1)) * 100000
            except ValueError:
                pass

    return hints


class SmartGovAIAgent:
    """Agent that selects and executes appropriate tools based on user input."""

    @classmethod
    def run_turn(
        cls,
        message: str,
        user: Optional[User],
        db: Session,
        explicit_language: Optional[str] = None
    ) -> ChatResponse:
        tools_executed: List[str] = []

        # Step 1: Detect Language
        tools_executed.append("detect_language")
        if explicit_language:
            lang = explicit_language
            confidence = 1.0
            needs_clar = False
        else:
            lang, confidence, needs_clar = detect_language(message)

        # Merge user profile if logged in
        profile_data: Dict[str, Any] = {}
        if user and user.profile:
            p = user.profile
            profile_data = {
                "age": p.age,
                "gender": p.gender,
                "income": p.income,
                "occupation": p.occupation,
                "education": p.education,
                "state": p.state or "All India",
                "category": p.category,
                "is_student": p.is_student,
                "is_farmer": p.is_farmer,
                "has_disability": p.has_disability,
            }

        # Step 2: Extract explicit hints from message
        message_hints = _extract_profile_hints(message)
        profile_data.update({k: v for k, v in message_hints.items() if v is not None})

        # Step 3: Search schemes tool
        tools_executed.append("search_schemes")
        search_query = message
        # Check intent categories
        for category_name, keywords in INTENT_KEYWORDS.items():
            if any(k in message.lower() for k in keywords):
                search_query = category_name
                break

        found_schemes = search_schemes(search_query, db, limit=6)
        if not found_schemes and search_query != message:
            found_schemes = search_schemes(message, db, limit=4)

        # Step 4: Evaluate Eligibility & Gather Documents / Steps for Top Matches
        recommended_cards: List[RecommendedSchemeCard] = []
        follow_up_questions: List[str] = []
        missing_fields_all: List[str] = []

        for s_summary in found_schemes[:4]:
            s_id = s_summary["id"]
            tools_executed.append("check_eligibility")
            eval_res = check_eligibility(s_id, profile_data, db)

            tools_executed.append("get_required_documents")
            docs_data = get_required_documents(s_id, db)

            tools_executed.append("get_application_steps")
            steps_data = get_application_steps(s_id, db)

            tools_executed.append("get_scheme_source")
            source_data = get_scheme_source(s_id, db)

            # Map status
            status = eval_res.get("status", "likely_eligible")
            missing = eval_res.get("missing_information", [])
            missing_fields_all.extend(missing)

            doc_names = [d["document_name"] for d in docs_data]
            step_instructions = [f"{s['step_number']}. {s['instruction']}" for s in steps_data]

            reasons = eval_res.get("passed_conditions", [])
            if status == EligibilityStatus.NOT_ELIGIBLE:
                reasons = eval_res.get("failed_conditions", [])

            card = RecommendedSchemeCard(
                scheme_id=s_id,
                title=s_summary["title"],
                department=s_summary.get("department"),
                target_group=s_summary.get("target_group"),
                benefits=s_summary.get("benefits"),
                eligibility_status=status,
                reasons=reasons,
                missing_information=missing,
                required_documents=doc_names,
                application_steps=step_instructions,
                official_link=s_summary.get("official_link"),
                source_url=source_data.get("source_url"),
                last_verified_at=source_data.get("last_verified_at"),
                data_confidence="High (Official Government Source)",
            )
            recommended_cards.append(card)

        # Step 5: Check Update Status tool
        tools_executed.append("check_update_status")
        update_info = check_update_status(db)

        # Unique missing fields
        missing_unique = list(dict.fromkeys(missing_fields_all))

        # Generate polite follow-up questions for missing fields in target language
        if missing_unique:
            if lang == "ta":
                follow_up_questions.append(
                    f"துல்லியமான தகுதி சரிபார்ப்பிற்கு தயவுசெய்து உங்கள் {', '.join(missing_unique[:2])} விவரங்களை பகிரவும்."
                )
            elif lang == "hi":
                follow_up_questions.append(
                    f"सटीक पात्रता जांच के लिए कृपया अपना {', '.join(missing_unique[:2])} विवरण बताएं।"
                )
            else:
                follow_up_questions.append(
                    f"To verify full eligibility, please provide your {', '.join(missing_unique[:2])}."
                )

        # Step 6: Generate Multilingual Conversational Reply
        # Try configured hosted LLM first; if not configured or failed, use rule-based reasoning synthesizer
        reply_text = cls._generate_conversational_reply(
            message=message,
            lang=lang,
            recommended_cards=recommended_cards,
            missing_fields=missing_unique,
            follow_ups=follow_up_questions,
            db=db,
        )

        return ChatResponse(
            reply=reply_text,
            detected_language=lang,
            language_confidence=confidence,
            needs_language_clarification=needs_clar,
            schemes_recommended=recommended_cards,
            follow_up_questions=follow_up_questions,
            missing_profile_fields=missing_unique,
            tool_calls_executed=list(dict.fromkeys(tools_executed)),
        )

    @classmethod
    def _generate_conversational_reply(
        cls,
        message: str,
        lang: str,
        recommended_cards: List[RecommendedSchemeCard],
        missing_fields: List[str],
        follow_ups: List[str],
        db: Session,
    ) -> str:
        # Check if OpenAI is configured and available
        if settings.OPENAI_API_KEY and settings.OPENAI_API_KEY.strip():
            try:
                from openai import OpenAI
                client = OpenAI(
                    api_key=settings.OPENAI_API_KEY,
                    base_url=settings.OPENAI_BASE_URL,
                )
                lang_name = "Tamil" if lang == "ta" else ("Hindi" if lang == "hi" else "English")
                
                # Context from retrieved tools
                card_context = []
                for c in recommended_cards:
                    card_context.append(
                        f"- Scheme: {c.title}\n"
                        f"  Benefits: {c.benefits}\n"
                        f"  Status: {c.eligibility_status}\n"
                        f"  Required Documents: {', '.join(c.required_documents[:3])}\n"
                        f"  Official Link: {c.official_link}\n"
                        f"  Reasons: {'; '.join(c.reasons[:2])}\n"
                        f"  Missing: {', '.join(c.missing_information)}"
                    )
                context_str = "\n".join(card_context) if card_context else "No direct matching scheme found in database."

                sys_prompt = AGENT_SYSTEM_PROMPT.format(language_name=lang_name, context=context_str)
                resp = client.chat.completions.create(
                    model=settings.OPENAI_MODEL,
                    messages=[
                        {"role": "system", "content": sys_prompt},
                        {"role": "user", "content": message},
                    ],
                    temperature=0.3,
                    max_tokens=650,
                )
                return resp.choices[0].message.content
            except Exception as e:
                logger.warning("Hosted LLM API call failed or unavailable (%s). Using verified reasoning synthesizer.", e)

        # Deterministic multilingual synthesizer based on verified tool data
        return cls._synthesize_verified_response(
            lang=lang,
            recommended_cards=recommended_cards,
            missing_fields=missing_fields,
            follow_ups=follow_ups,
        )

    @classmethod
    def _synthesize_verified_response(
        cls,
        lang: str,
        recommended_cards: List[RecommendedSchemeCard],
        missing_fields: List[str],
        follow_ups: List[str],
    ) -> str:
        if not recommended_cards:
            if lang == "ta":
                return (
                    "மன்னிக்கவும், உங்கள் கேள்விக்கான குறிப்பிட்ட அரசு திட்டங்கள் எதுவும் தற்போது தரவுத்தளத்தில் கண்டறியப்படவில்லை. "
                    "தயவுசெய்து கல்வி, விவசாயம், மகளிர் நலம், அல்லது வணிக கடன் போன்ற குறிப்பிட்ட துறையைக் குறிப்பிடவும்."
                )
            elif lang == "hi":
                return (
                    "क्षमा करें, आपके अनुरोध से मेल खाने वाली कोई सरकारी योजना नहीं मिली। "
                    "कृपया छात्रवृत्ति, किसान, स्वास्थ्य, या महिला कल्याण जैसे विशिष्ट विषय के बारे में पूछें।"
                )
            return (
                "No verified government schemes directly matched your criteria. "
                "Please mention specific areas like scholarships, farming support, women welfare, or business loans."
            )

        top = recommended_cards[0]
        sections = []

        if lang == "ta":
            sections.append(f"🏛️ **{top.title}**")
            sections.append(f"• **நன்மைகள்**: {top.benefits or 'அரசு உதவி வழங்கப்படுகிறது'}")
            
            # Status explanation
            if top.eligibility_status == EligibilityStatus.LIKELY_ELIGIBLE:
                sections.append("• **தகுதி நிலை**: ✅ நீங்கள் இந்த திட்டத்திற்கு தகுதியுடையவராக இருக்கலாம் (Likely Eligible).")
                if top.reasons:
                    sections.append(f"• **காரணங்கள்**: {'; '.join(top.reasons[:2])}")
            elif top.eligibility_status == EligibilityStatus.NEEDS_MORE_INFO:
                sections.append("• **தகுதி நிலை**: ℹ️ கூடுதல் தகவல் தேவை (Needs More Information).")
                if top.missing_information:
                    sections.append(f"• **தேவைப்படும் விவரங்கள்**: {', '.join(top.missing_information[:2])}")
            elif top.eligibility_status == EligibilityStatus.NOT_ELIGIBLE:
                sections.append("• **தகுதி நிலை**: ❌ தற்போது நீங்கள் நிர்ணயிக்கப்பட்ட தகுதி அளவுகோல்களை பூர்த்தி செய்யவில்லை.")
            
            if top.required_documents:
                sections.append(f"• **தேவையான ஆவணங்கள்**: {', '.join(top.required_documents[:4])}")
            if top.official_link:
                sections.append(f"• **அதிகாரப்பூர்வ தளம்**: [{top.official_link}]({top.official_link})")
            
            if follow_ups:
                sections.append(f"\n💡 *{follow_ups[0]}*")

        elif lang == "hi":
            sections.append(f"🏛️ **{top.title}**")
            sections.append(f"• **लाभ**: {top.benefits or 'सरकारी सहायता उपलब्ध है'}")
            if top.eligibility_status == EligibilityStatus.LIKELY_ELIGIBLE:
                sections.append("• **पात्रता स्थिति**: ✅ आप इस योजना के लिए पात्र हो सकते हैं (Likely Eligible)।")
                if top.reasons:
                    sections.append(f"• **कारण**: {'; '.join(top.reasons[:2])}")
            elif top.eligibility_status == EligibilityStatus.NEEDS_MORE_INFO:
                sections.append("• **पात्रता स्थिति**: ℹ️ अतिरिक्त जानकारी आवश्यक (Needs More Information)।")
                if top.missing_information:
                    sections.append(f"• **अपेक्षित विवरण**: {', '.join(top.missing_information[:2])}")
            elif top.eligibility_status == EligibilityStatus.NOT_ELIGIBLE:
                sections.append("• **पात्रता स्थिति**: ❌ आप वर्तमान में योजना की शर्तों को पूरा नहीं करते हैं।")
            
            if top.required_documents:
                sections.append(f"• **आवश्यक दस्तावेज़**: {', '.join(top.required_documents[:4])}")
            if top.official_link:
                sections.append(f"• **आधिकारिक पोर्टल**: [{top.official_link}]({top.official_link})")
            
            if follow_ups:
                sections.append(f"\n💡 *{follow_ups[0]}*")

        else:
            # English
            sections.append(f"🏛️ **{top.title}**")
            sections.append(f"• **Benefits**: {top.benefits or 'Government assistance provided'}")
            if top.eligibility_status == EligibilityStatus.LIKELY_ELIGIBLE:
                sections.append("• **Eligibility Assessment**: ✅ Likely Eligible based on verified criteria.")
                if top.reasons:
                    sections.append(f"• **Key Reasons**: {'; '.join(top.reasons[:2])}")
            elif top.eligibility_status == EligibilityStatus.NEEDS_MORE_INFO:
                sections.append("• **Eligibility Assessment**: ℹ️ Needs More Information to confirm.")
                if top.missing_information:
                    sections.append(f"• **Details Needed**: {', '.join(top.missing_information[:2])}")
            elif top.eligibility_status == EligibilityStatus.NOT_ELIGIBLE:
                sections.append("• **Eligibility Assessment**: ❌ Does not meet all eligibility rules.")
                if top.reasons:
                    sections.append(f"• **Unmatched criteria**: {'; '.join(top.reasons[:2])}")
            
            if top.required_documents:
                sections.append(f"• **Required Documents**: {', '.join(top.required_documents[:4])}")
            if top.official_link:
                sections.append(f"• **Official Portal**: [{top.official_link}]({top.official_link})")
            
            if follow_ups:
                sections.append(f"\n💡 *{follow_ups[0]}*")

        # Mention other matching schemes if present
        if len(recommended_cards) > 1:
            others = [c.title for c in recommended_cards[1:3]]
            if lang == "ta":
                sections.append(f"\n🔗 **தொடர்புடைய பிற திட்டங்கள்**: {', '.join(others)}")
            elif lang == "hi":
                sections.append(f"\n🔗 **अन्य संबंधित योजनाएं**: {', '.join(others)}")
            else:
                sections.append(f"\n🔗 **Other Related Schemes**: {', '.join(others)}")

        return "\n".join(sections)
