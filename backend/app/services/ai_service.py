"""
SmartGov AI Assistant Service.
Supports OpenAI API with automatic fallback to an intelligent contextual
knowledge engine built for Indian government welfare schemes.
Supports multilingual responses (English, Hindi, Tamil).
"""
import logging
from typing import Optional, List
from openai import OpenAI
from sqlalchemy.orm import Session
from app.core.config import settings
from app.models.models import Scheme

logger = logging.getLogger(__name__)

_client: Optional[OpenAI] = None


def get_client() -> Optional[OpenAI]:
    global _client
    if settings.OPENAI_API_KEY and settings.OPENAI_API_KEY.strip():
        if _client is None:
            try:
                _client = OpenAI(
                    api_key=settings.OPENAI_API_KEY,
                    base_url=settings.OPENAI_BASE_URL,
                )
            except Exception as e:
                logger.warning("Could not initialize OpenAI client: %s", e)
                return None
        return _client
    return None


LANGUAGE_NAMES = {"en": "English", "ta": "Tamil", "hi": "Hindi"}

SYSTEM_PROMPT = """You are SmartGov AI, an expert, courteous assistant specialized in Indian government welfare schemes and citizen services.
Help citizens understand eligibility requirements, scheme benefits, application procedures, required documentation, and deadlines.

Available Schemes Context:
{schemes_context}

Guidelines:
- Answer accurately using the schemes provided above or general public knowledge of Indian welfare policies.
- If asked whether the user is eligible, explain the key criteria clearly and recommend checking the Eligibility Checker in the app.
- Provide clear, bulleted instructions for application steps and document checklists.
- Be concise, supportive, and professional.
- Respond in the requested language: {language}.
"""


def _build_schemes_context(db: Optional[Session] = None) -> str:
    if db is None:
        return "National Schemes: PM-KISAN, PM Scholarship Scheme, Mahila Samman Savings, National Career Service, National Old Age Pension, National Disability Pension."
    try:
        schemes = db.query(Scheme).filter(Scheme.is_active == True).all()  # noqa: E712
        if not schemes:
            return ""
        lines = []
        for s in schemes:
            doc_names = ", ".join([d.document_name for d in s.documents]) if s.documents else "Aadhaar Card"
            lines.append(
                f"- Scheme: {s.title} ({s.category or 'General'})\n"
                f"  Department: {s.department or 'N/A'}\n"
                f"  Benefits: {s.benefits or 'N/A'}\n"
                f"  Target Group: {s.target_group or 'N/A'}, State: {s.state or 'All India'}\n"
                f"  Key Documents: {doc_names}\n"
                f"  Official Link: {s.official_link or 'N/A'}"
            )
        return "\n".join(lines)
    except Exception:
        return ""


def _fallback_knowledge_engine(message: str, language: str = "en", db: Optional[Session] = None) -> str:
    """
    Intelligent built-in assistant when OpenAI API key is not configured or unavailable.
    Provides comprehensive, structured guidance in English, Hindi, and Tamil.
    """
    msg_lower = message.lower()

    # Query active schemes from DB if available
    schemes = []
    if db:
        try:
            schemes = db.query(Scheme).filter(Scheme.is_active == True).all()  # noqa: E712
        except Exception:
            pass

    # Helper to match keywords
    def matches(*keywords):
        return any(k in msg_lower for k in keywords)

    # 1. Agriculture / Farmers
    if matches("farmer", "kisan", "pm-kisan", "pmkisan", "agriculture", "krishi", "land", "crop", "விவசாயி", "किसान"):
        if language == "hi":
            return (
                "🌾 **पीएम-किसान सम्मान निधि (PM-KISAN)**:\n\n"
                "• **लाभ**: सभी पात्र किसान परिवारों को प्रति वर्ष ₹6,000 (3 समान किस्तों में ₹2,000)।\n"
                "• **पात्रता**: भूमिधारी किसान परिवार जिनकी पारिवारिक आय ₹2,00,000 या कम है।\n"
                "• **आवश्यक दस्तावेज़**: आधार कार्ड, भूमि स्वामित्व अभिलेख (खसरा/खतौनी), बैंक पासबुक।\n"
                "• **आवेदन कैसे करें**: निकटतम जन सेवा केंद्र (CSC) या [pmkisan.gov.in](https://pmkisan.gov.in) पर आवेदन करें।"
            )
        elif language == "ta":
            return (
                "🌾 **பிரதமர் கிசான் சம்மான் நிதி (PM-KISAN)**:\n\n"
                "• **நன்மைகள்**: தகுதியான விவசாய குடும்பங்களுக்கு ஆண்டுக்கு ₹6,000 (3 தவணைகளில் ₹2,000).\n"
                "• **தகுதி**: ₹2,00,000 அல்லது அதற்கும் குறைவான வருமானம் கொண்ட நில உரிமையாளர் விவசாயிகள்.\n"
                "• **தேவையான ஆவணங்கள்**: ஆதார் அட்டை, நில பட்டா/உரிமை ஆவணங்கள், வங்கி பாஸ்புக்.\n"
                "• **விண்ணப்பிக்கும் முறை**: [pmkisan.gov.in](https://pmkisan.gov.in) இணையதளத்தில் அல்லது அருகிலுள்ள இ-சேவை மையத்தில் விண்ணப்பிக்கவும்."
            )
        else:
            return (
                "🌾 **PM-KISAN Samman Nidhi (Ministry of Agriculture)**\n\n"
                "• **Benefits**: ₹6,000 per year paid in three equal installments of ₹2,000 directly to bank accounts.\n"
                "• **Eligibility**: Small and marginal landholding farmer families with modest annual income (≤ ₹2,00,000).\n"
                "• **Documents Required**: Aadhaar Card, Land Ownership Papers (Khata/Khesra), Bank Passbook.\n"
                "• **How to Apply**: Visit your nearest Common Service Centre (CSC) or apply online at [pmkisan.gov.in](https://pmkisan.gov.in)."
            )

    # 2. Education / Scholarships / Students
    if matches("student", "scholarship", "education", "study", "college", "school", "fee", "மாணவர்", "छात्र", "छात्रवृत्ति"):
        if language == "hi":
            return (
                "🎓 **प्रधानमंत्री छात्रवृत्ति योजना (PM Scholarship Scheme)**:\n\n"
                "• **लाभ**: उच्च शिक्षा के लिए प्रति वर्ष ₹50,000 तक की वित्तीय सहायता।\n"
                "• **पात्रता**: वर्तमान में अध्ययनरत छात्र, 25 वर्ष या उससे कम आयु, पारिवारिक आय ₹2,50,000 से कम।\n"
                "• **आवश्यक दस्तावेज़**: आधार कार्ड, आय प्रमाण पत्र, पिछली परीक्षा की मार्कशीट।\n"
                "• **आवेदन कैसे करें**: राष्ट्रीय छात्रवृत्ति पोर्टल [scholarships.gov.in](https://scholarships.gov.in) पर ऑनलाइन आवेदन करें।"
            )
        elif language == "ta":
            return (
                "🎓 **பிரதமர் கல்வி உதவித்தொகை திட்டம் (PM Scholarship Scheme)**:\n\n"
                "• **நன்மைகள்**: உயர்கல்வி கட்டணம் மற்றும் படிப்புச் செலவுகளுக்கு ஆண்டுக்கு ₹50,000 வரை உதவித்தொகை.\n"
                "• **தகுதி**: கல்லூரியில் பயிலும் மாணவர்கள், வயது 25 அல்லது அதற்கும் குறைவு, குடும்ப வருமானம் ₹2,50,000க்குள்.\n"
                "• **தேவையான ஆவணங்கள்**: ஆதார் அட்டை, வருமான சான்றிதழ், மதிப்பெண் சான்றிதழ்.\n"
                "• **விண்ணப்பிக்கும் முறை**: தேசிய உதவித்தொகை இணையதளமான [scholarships.gov.in](https://scholarships.gov.in) வழியாக விண்ணப்பிக்கவும்."
            )
        else:
            return (
                "🎓 **PM Scholarship Scheme (Ministry of Education)**\n\n"
                "• **Benefits**: Financial assistance up to ₹50,000 per year for tuition and living expenses.\n"
                "• **Eligibility**: Meritorious enrolled students, age ≤ 25 years, annual family income ≤ ₹2,50,000.\n"
                "• **Documents Required**: Aadhaar Card, Income Certificate, Marksheet of last qualifying exam.\n"
                "• **How to Apply**: Register on the National Scholarship Portal at [scholarships.gov.in](https://scholarships.gov.in)."
            )

    # 3. Women Welfare
    if matches("women", "woman", "female", "girl", "mahila", "ladli", "பெண்", "महिला"):
        if language == "hi":
            return (
                "🌸 **महिला सम्मान बचत प्रमाणपत्र (Mahila Samman Savings)**:\n\n"
                "• **लाभ**: महिलाओं और बालिकाओं के लिए 2 वर्ष की अवधि में ₹2 लाख तक की जमा पर 7.5% निश्चित ब्याज दर।\n"
                "• **पात्रता**: केवल महिला या बालिका के नाम पर खाता खोला जा सकता है।\n"
                "• **आवश्यक दस्तावेज़**: आधार कार्ड, पैन कार्ड (वैकल्पिक), पासपोर्ट साइज फोटो।\n"
                "• **आवेदन कैसे करें**: किसी भी डाकघर या अधिकृत बैंक शाखा में जाएं।"
            )
        elif language == "ta":
            return (
                "🌸 **மகிளா சம்மான் சேமிப்புச் சான்றிதழ் (Mahila Samman Savings)**:\n\n"
                "• **நன்மைகள்**: பெண்கள் மற்றும் பெண் குழந்தைகளுக்காக 2 ஆண்டுகளுக்கு ₹2 லட்சம் வரையிலான சேமிப்பிற்கு 7.5% நிலையான வட்டி.\n"
                "• **தகுதி**: பெண்கள் மற்றும் பெண் குழந்தைகள் மட்டுமே.\n"
                "• **தேவையான ஆவணங்கள்**: ஆதார் அட்டை, பான் கார்டு, புகைப்படங்கள்.\n"
                "• **விண்ணப்பிக்கும் முறை**: அருகிலுள்ள அஞ்சலகம் அல்லது தேசியமயமாக்கப்பட்ட வங்கிகளில் கணக்கு தொடங்கலாம்."
            )
        else:
            return (
                "🌸 **Mahila Samman Savings Certificate (Ministry of Finance)**\n\n"
                "• **Benefits**: 7.5% fixed interest rate on deposits up to ₹2 Lakh for a 2-year tenure.\n"
                "• **Eligibility**: Exclusively for women and girl children.\n"
                "• **Documents Required**: Aadhaar Card, PAN Card (optional), Passport photo.\n"
                "• **How to Apply**: Visit any Post Office or designated public sector bank branch."
            )

    # 4. Jobs / Employment / Unemployment
    if matches("job", "employment", "career", "unemployed", "ncs", "resume", "வேலை", "रोजगार", "नौकरी"):
        if language == "hi":
            return (
                "💼 **राष्ट्रीय करियर सेवा (National Career Service - NCS)**:\n\n"
                "• **लाभ**: निःशुल्क नौकरी के अवसर, कौशल प्रशिक्षण और करियर परामर्श।\n"
                "• **पात्रता**: न्यूनतम आयु 18 वर्ष, वर्तमान में बेरोजगार या नौकरी की तलाश में।\n"
                "• **आवश्यक दस्तावेज़**: आधार कार्ड, शैक्षणिक योग्यता प्रमाण पत्र, बायोडाटा (रिज्यूमे)।\n"
                "• **आवेदन कैसे करें**: [ncs.gov.in](https://ncs.gov.in) पर पंजीकरण करें।"
            )
        elif language == "ta":
            return (
                "💼 **தேசிய தொழில் சேவை போர்டல் (National Career Service - NCS)**:\n\n"
                "• **நன்மைகள்**: இலவச வேலை வாய்ப்புகள், திறன் பயிற்சி மற்றும் தொழில் வழிகாட்டுதல்.\n"
                "• **தகுதி**: 18 வயது அல்லது அதற்கு மேற்பட்ட வேலை தேடுபவர்கள்.\n"
                "• **தேவையான ஆவணங்கள்**: ஆதார் அட்டை, கல்வி சான்றிதழ்கள், சுயவிவர குறிப்பு (Resume).\n"
                "• **விண்ணப்பிக்கும் முறை**: [ncs.gov.in](https://ncs.gov.in) தளத்தில் பதிவு செய்து வேலைக்கு விண்ணப்பிக்கலாம்."
            )
        else:
            return (
                "💼 **National Career Service (Ministry of Labour & Employment)**\n\n"
                "• **Benefits**: Free employment matching, skills development, and certified career counselling.\n"
                "• **Eligibility**: Job seekers aged 18+, currently unemployed or seeking better jobs.\n"
                "• **Documents Required**: Aadhaar Card, Educational Certificates, Resume.\n"
                "• **How to Apply**: Register your profile at [ncs.gov.in](https://ncs.gov.in)."
            )

    # 5. Senior Citizens / Pension
    if matches("senior", "pension", "old age", "elderly", "60", "முதியோர்", "ஓய்வூதியம்", "पेंशन", "वृद्धावस्था"):
        if language == "hi":
            return (
                "👴 **इंदिरा गांधी राष्ट्रीय वृद्धावस्था पेंशन योजना**:\n\n"
                "• **लाभ**: बीपीएल परिवारों के 60 वर्ष या उससे अधिक आयु के वरिष्ठ नागरिकों के लिए मासिक पेंशन।\n"
                "• **पात्रता**: आयु 60 वर्ष या अधिक, बीपीएल (गरीबी रेखा से नीचे) परिवार।\n"
                "• **आवश्यक दस्तावेज़**: आधार कार्ड, आयु प्रमाण पत्र, बीपीएल प्रमाण पत्र, बैंक पासबुक।\n"
                "• **आवेदन कैसे करें**: स्थानीय ग्राम पंचायत या नगर पालिका कार्यालय में संपर्क करें।"
            )
        elif language == "ta":
            return (
                "👴 **இந்திரா காந்தி தேசிய முதியோர் ஓய்வூதிய திட்டம்**:\n\n"
                "• **நன்மைகள்**: 60 வயதுக்கு மேற்பட்ட வறுமைக் கோட்டிற்கு கீழ் உள்ள முதியோருக்கு மாதாந்திர ஓய்வூதியம்.\n"
                "• **தகுதி**: 60 வயது மற்றும் அதற்கு மேற்பட்ட முதியவர்கள், குறைந்த வருமானம்.\n"
                "• **தேவையான ஆவணங்கள்**: ஆதார் அட்டை, வயது சான்றிதழ், பிபிஎல் அட்டை, வங்கி பாஸ்புக்.\n"
                "• **விண்ணப்பிக்கும் முறை**: உள்ளூர் கிராம பஞ்சாயத்து அல்லது நகராட்சி அலுவலகத்தில் விண்ணப்பிக்கவும்."
            )
        else:
            return (
                "👴 **Indira Gandhi National Old Age Pension Scheme**\n\n"
                "• **Benefits**: Monthly pension support for low-income senior citizens.\n"
                "• **Eligibility**: Senior citizens aged 60 years or above from BPL/low-income households.\n"
                "• **Documents Required**: Aadhaar Card, Age Proof, BPL/Income Certificate, Bank Details.\n"
                "• **How to Apply**: Apply through your local Gram Panchayat or Municipal Ward Office."
            )

    # 6. Disability / Special Needs
    if matches("disability", "disabled", "divyang", "handicap", "மாற்றுத்திறனாளி", "दिव्यांग"):
        if language == "hi":
            return (
                "♿ **राष्ट्रीय दिव्यांग पेंशन एवं सहायता योजना**:\n\n"
                "• **लाभ**: मासिक पेंशन सहायता और सहायक उपकरण प्रदान किए जाते हैं।\n"
                "• **पात्रता**: प्रमाणित दिव्यांगता (40% या अधिक), कम आय वर्ग।\n"
                "• **आवश्यक दस्तावेज़**: आधार कार्ड, दिव्यांगता प्रमाण पत्र (UDID), आय प्रमाण पत्र।\n"
                "• **आवेदन कैसे करें**: जिला समाज कल्याण कार्यालय या [disabilityaffairs.gov.in](https://disabilityaffairs.gov.in) पर आवेदन करें।"
            )
        elif language == "ta":
            return (
                "♿ **தேசிய மாற்றுத்திறனாளிகள் ஓய்வூதிய திட்டம்**:\n\n"
                "• **நன்மைகள்**: மாதாந்திர ஓய்வூதியம் மற்றும் உதவி உபகரணங்கள்.\n"
                "• **தகுதி**: அரசு மருத்துவ சான்றளிக்கப்பட்ட மாற்றுத்திறனாளிகள் (UDID).\n"
                "• **தேவையான ஆவணங்கள்**: ஆதார் அட்டை, மாற்றுத்திறனாளி சான்றிதழ், வருமான சான்றிதழ்.\n"
                "• **விண்ணப்பிக்கும் முறை**: மாவட்ட சமூக நல அலுவலகம் மூலமாக அல்லது [disabilityaffairs.gov.in](https://disabilityaffairs.gov.in) மூலம் விண்ணப்பிக்கலாம்."
            )
        else:
            return (
                "♿ **National Disability Pension Scheme**\n\n"
                "• **Benefits**: Monthly financial assistance plus subsidized assistive devices.\n"
                "• **Eligibility**: Persons with certified disability (UDID card), low-income household.\n"
                "• **Documents Required**: Aadhaar Card, Government Disability Certificate / UDID, Income Proof.\n"
                "• **How to Apply**: Apply at the District Social Welfare Office or online at [disabilityaffairs.gov.in](https://disabilityaffairs.gov.in)."
            )

    # 7. General list or greetings
    if matches("hello", "hi", "hey", "help", "who", "what", "scheme", "list", "வணக்கம்", "नमस्ते"):
        if language == "hi":
            return (
                "नमस्ते! 🙏 मैं आपका **स्मार्टगव AI सहायक** हूँ।\n\n"
                "मैं इन क्षेत्रों में सरकारी योजनाओं की पूरी जानकारी दे सकता हूँ:\n"
                "• 🎓 **शिक्षा एवं छात्रवृत्ति**: पीएम स्कॉलरशिप आदि\n"
                "• 🌾 **कृषि ও किसान**: पीएम-किसान सम्मान निधि\n"
                "• 🌸 **महिला कल्याण**: महिला सम्मान बचत योजना\n"
                "• 💼 **रोजगार एवं कौशल**: राष्ट्रीय करियर सेवा (NCS)\n"
                "• 👴 **वरिष्ठ नागरिक**: वृद्धावस्था पेंशन योजना\n"
                "• ♿ **दिव्यांगजन सहायता**: दिव्यांग पेंशन योजना\n\n"
                "👉 अपने लिए सटीक पात्रता जानने के लिए ऐप के **'डैशबोर्ड'** या **'पात्रता जांचें'** विकल्प का उपयोग करें!"
            )
        elif language == "ta":
            return (
                "வணக்கம்! 🙏 நான் உங்கள் **ஸ்மார்ட்கவ் AI உதவியாளர்**.\n\n"
                "அரசு நலத்திட்டங்கள் குறித்த அனைத்து தகவல்களையும் நான் உங்களுக்கு வழங்க முடியும்:\n"
                "• 🎓 **கல்வி மற்றும் உதவித்தொகை**: பிரதமர் கல்வி உதவித்தொகை\n"
                "• 🌾 **விவசாயம்**: பிரதமர் கிசான் சம்மான் நிதி\n"
                "• 🌸 **மகளிர் நலம்**: மகிளா சம்மான் சேமிப்புத் திட்டம்\n"
                "• 💼 **வேலைவாய்ப்பு**: தேசிய தொழில் சேவை (NCS)\n"
                "• 👴 **முதியோர் ஓய்வூதியம்**: இந்திரா காந்தி முதியோர் உதவித்தொகை\n"
                "• ♿ **மாற்றுத்திறனாளிகள் உதவி**: மாற்றுத்திறனாளி ஓய்வூதியம்\n\n"
                "👉 உங்கள் சுயவிவரத்திற்கான துல்லியமான தகுதியை சரிபார்க்க **'டாஷ்போர்டு'** பகுதியை பார்க்கவும்!"
            )
        else:
            return (
                "Hello! 👋 I'm your **SmartGov AI Assistant**.\n\n"
                "I can help you explore government schemes across key sectors:\n"
                "• 🎓 **Education & Scholarships**: PM Scholarship Scheme\n"
                "• 🌾 **Agriculture & Farmers**: PM-KISAN Samman Nidhi\n"
                "• 🌸 **Women Welfare**: Mahila Samman Savings Certificate\n"
                "• 💼 **Employment & Skills**: National Career Service (NCS)\n"
                "• 👴 **Senior Citizens**: National Old Age Pension Scheme\n"
                "• ♿ **Disability Support**: National Disability Pension Scheme\n\n"
                "👉 For tailored recommendations based on your exact age, income, and occupation, check your **Dashboard** or use the **Eligibility Checker**!"
            )

    # Default fallback summary
    if language == "hi":
        return (
            f"सरकारी योजनाओं से संबंधित आपका प्रश्न: \"{message}\"\n\n"
            "कृपया किसी विशिष्ट विषय (जैसे: शिक्षा, छात्रवृत्ति, किसान, महिला कल्याण, पेंशन, या रोजगार) के बारे में पूछें। "
            "आप अपनी प्रोफ़ाइल के आधार पर तुरंत उपयुक्त योजनाएं देखने के लिए **डैशबोर्ड** भी देख सकते हैं।"
        )
    elif language == "ta":
        return (
            f"அரசு திட்டங்கள் தொடர்பான உங்கள் கேள்வி: \"{message}\"\n\n"
            "கல்வி, விவசாயம், மகளிர் நலம், வேலைவாய்ப்பு, அல்லது ஓய்வூதியம் போன்ற குறிப்பிட்ட தலைப்புகளைப் பற்றி கேளுங்கள். "
            "உங்கள் தகுதிக்கேற்ற திட்டங்களை உடனடியாகக் காண **டாஷ்போர்டு** பகுதியை பார்வையிடவும்."
        )
    else:
        return (
            f"Regarding your query about: \"{message}\"\n\n"
            "To give you the most accurate advice, please mention your area of interest (e.g., Scholarships, Farmer Support, Women Welfare, Senior Pension, or Employment). "
            "You can also navigate to the **Schemes** tab to view all active government schemes or check the **Dashboard** for instant eligibility analysis!"
        )


def chat_completion(message: str, language: str = "en", db: Optional[Session] = None) -> str:
    client = get_client()
    if client:
        try:
            lang_name = LANGUAGE_NAMES.get(language, "English")
            schemes_ctx = _build_schemes_context(db)
            system_msg = SYSTEM_PROMPT.format(language=lang_name, schemes_context=schemes_ctx)
            response = client.chat.completions.create(
                model=settings.OPENAI_MODEL,
                messages=[
                    {"role": "system", "content": system_msg},
                    {"role": "user", "content": message},
                ],
                temperature=0.4,
                max_tokens=600,
            )
            return response.choices[0].message.content
        except Exception as exc:
            logger.warning("OpenAI chat failed, using fallback knowledge engine: %s", exc)

    return _fallback_knowledge_engine(message, language=language, db=db)


def explain_eligibility_result(
    scheme_title: str, matched: list, unmatched: list, language: str = "en"
) -> str:
    client = get_client()
    lang_name = LANGUAGE_NAMES.get(language, "English")
    if client:
        try:
            prompt = (
                f"Scheme: {scheme_title}\n"
                f"Conditions met: {matched}\n"
                f"Conditions not met: {unmatched}\n"
                f"Explain in one short, friendly paragraph in {lang_name} whether this looks promising "
                f"for the citizen and what they should check next."
            )
            response = client.chat.completions.create(
                model=settings.OPENAI_MODEL,
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT.format(language=lang_name, schemes_context="")},
                    {"role": "user", "content": prompt},
                ],
                temperature=0.3,
                max_tokens=300,
            )
            return response.choices[0].message.content
        except Exception as exc:
            logger.warning("OpenAI explain failed: %s", exc)

    # Local fallback explanation
    if not unmatched:
        if language == "hi":
            return f"बधाई हो! आप '{scheme_title}' के लिए सभी पात्रता शर्तों को पूरा करते हैं। आप आधिकारिक पोर्टल पर आवेदन कर सकते हैं।"
        elif language == "ta":
            return f"வாழ்த்துகள்! நீங்கள் '{scheme_title}' திட்டத்தின் அனைத்து தகுதி நிபந்தனைகளையும் பூர்த்தி செய்கிறீர்கள்."
        return f"Great news! You meet all listed eligibility requirements for {scheme_title}. We recommend applying via the official link with your documents ready."
    else:
        unmatched_str = ", ".join(unmatched[:2])
        if language == "hi":
            return f"आप '{scheme_title}' के लिए कुछ शर्तों को पूरा नहीं करते हैं (जैसे: {unmatched_str})। कृपया दिशानिर्देश देखें।"
        elif language == "ta":
            return f"நீங்கள் '{scheme_title}' திட்டத்திற்கான சில நிபந்தனைகளை பூர்த்தி செய்யவில்லை ({unmatched_str})."
        return f"You currently meet some requirements for {scheme_title}, but check the conditions not met ({unmatched_str}) before applying."
