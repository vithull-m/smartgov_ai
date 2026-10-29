"""
Interactive Voice Response (IVRS) Engine for SmartGov AI.
Handles:
1. Multilingual Phone Menus (Tamil, English, Hindi)
2. DTMF (Keypress: 1, 2, 3...) & Voice Input processing
3. TwiML Generation (Twilio Voice XML standard)
4. Direct Web Dialer Simulator for browser testing
5. Voice agent conversation routing to SmartGovAIAgent
6. Call session management & persistence in SQLite
"""
import uuid
import logging
from typing import Dict, Any, Optional
from xml.sax.saxutils import escape as xml_escape
from sqlalchemy.orm import Session
from app.models.models import IVRCallLog, Scheme
from app.services.agent_orchestrator import SmartGovAIAgent
from app.core.config import settings

logger = logging.getLogger(__name__)

# Language Voice Configuration for Twilio / Browser TTS
VOICE_MAP = {
    "ta": {"voice": "Polly.Valluvar", "lang_code": "ta-IN", "name": "Tamil (தமிழ்)"},
    "hi": {"voice": "Polly.Aditi", "lang_code": "hi-IN", "name": "Hindi (हिंदी)"},
    "en": {"voice": "Polly.Raveena", "lang_code": "en-IN", "name": "English"},
}

IVR_MENUS = {
    "welcome": {
        "text": {
            "en": "Welcome to SmartGov AI Helpline. For English, press 1. தமிழுக்கு எண் இரண்டை அழுத்தவும். हिंदी के लिए तीन दबाएं.",
            "ta": "ஸ்மார்ட்கோவ் உதவி மையத்திற்கு நல்வரவு. தமிழுக்கு எண் 1, English press 2, हिंदी के लिए 3 दबाएं.",
            "hi": "स्मार्टगोव एआई हेल्पलाइन में आपका स्वागत है। हिंदी के लिए 1 दबाएं। For English press 2। தமிழுக்கு 3 அழுத்தவும்."
        }
    },
    "main_menu": {
        "text": {
            "en": (
                "Main Menu: Press 1 for Agriculture and PM-KISAN. "
                "Press 2 for Student Scholarships. "
                "Press 3 for Women Welfare schemes. "
                "Press 4 for Ayushman Bharat Health Insurance. "
                "Press 5 to speak your query or question. "
                "Press 0 to repeat or change language."
            ),
            "ta": (
                "முதன்மை மெனு: விவசாயம் மற்றும் PM-கிசான் திட்டத்திற்கு எண் 1-ஐ அழுத்தவும். "
                "மாணவர் கல்வி உதவித்தொகைக்கு எண் 2-ஐ அழுத்தவும். "
                "மகளிர் நலம் மற்றும் உரிமைத்தொகைக்கு எண் 3-ஐ அழுத்தவும். "
                "ஆயுஷ்மான் பாரத் மருத்துவ காப்பீட்டிற்கு எண் 4-ஐ அழுத்தவும். "
                "உங்கள் கேள்வியை குரல் மூலம் கேட்க எண் 5-ஐ அழுத்தவும். "
                "மொழியை மாற்ற அல்லது மீண்டும் கேட்க 0-ஐ அழுத்தவும்."
            ),
            "hi": (
                "मुख्य मेनू: कृषि और पीएम-किसान के लिए 1 दबाएं। "
                "छात्रवृत्ति योजनाओं के लिए 2 दबाएं। "
                "महिला कल्याण योजनाओं के लिए 3 दबाएं। "
                "आयुष्मान भारत स्वास्थ्य बीमा के लिए 4 दबाएं। "
                "अपना प्रश्न बोलकर पूछने के लिए 5 दबाएं। "
                "भाषा बदलने के लिए 0 दबाएं।"
            )
        }
    }
}


def build_twiml_response(say_text: str, language: str = "en", gather_action: Optional[str] = None, num_digits: int = 1, timeout: int = 5, record_speech: bool = False) -> str:
    """Generate standard TwiML XML response."""
    voice_info = VOICE_MAP.get(language, VOICE_MAP["en"])
    voice_name = voice_info["voice"]
    lang_code = voice_info["lang_code"]
    escaped_text = xml_escape(say_text)

    xml = ['<?xml version="1.0" encoding="UTF-8"?>', '<Response>']

    if record_speech and gather_action:
        # Gather voice speech input
        xml.append(f'  <Gather input="speech" action="{gather_action}" language="{lang_code}" timeout="{timeout}">')
        xml.append(f'    <Say voice="{voice_name}" language="{lang_code}">{escaped_text}</Say>')
        xml.append('  </Gather>')
        xml.append(f'  <Say voice="{voice_name}" language="{lang_code}">We did not receive any input. Goodbye.</Say>')
        xml.append('  <Hangup/>')
    elif gather_action:
        # Gather DTMF keypress
        xml.append(f'  <Gather input="dtmf" numDigits="{num_digits}" timeout="{timeout}" action="{gather_action}">')
        xml.append(f'    <Say voice="{voice_name}" language="{lang_code}">{escaped_text}</Say>')
        xml.append('  </Gather>')
        xml.append(f'  <Say voice="{voice_name}" language="{lang_code}">No key was pressed. Thank you for calling SmartGov AI.</Say>')
        xml.append('  <Hangup/>')
    else:
        xml.append(f'  <Say voice="{voice_name}" language="{lang_code}">{escaped_text}</Say>')
        xml.append('  <Hangup/>')

    xml.append('</Response>')
    return '\n'.join(xml)


class IVRService:
    """Core state machine and query handler for SmartGov IVRS."""

    @staticmethod
    def get_or_create_call_log(call_sid: str, caller_phone: Optional[str], db: Session) -> IVRCallLog:
        log = db.query(IVRCallLog).filter(IVRCallLog.call_sid == call_sid).first()
        if not log:
            log = IVRCallLog(
                call_sid=call_sid,
                caller_phone=caller_phone or "+919876543210",
                language="en",
                status="in_progress",
            )
            db.add(log)
            db.commit()
            db.refresh(log)
        return log

    @staticmethod
    def handle_initial_call(call_sid: str, caller_phone: Optional[str], db: Session) -> Dict[str, Any]:
        """Start an IVR call session with language selection."""
        log = IVRService.get_or_create_call_log(call_sid, caller_phone, db)
        welcome_text = IVR_MENUS["welcome"]["text"]["en"]
        
        twiml = build_twiml_response(
            say_text=welcome_text,
            language="en",
            gather_action=f"{settings.BASE_WEBHOOK_URL}/api/ivr/menu?step=language&call_sid={call_sid}",
            num_digits=1,
            timeout=6,
        )

        return {
            "call_sid": call_sid,
            "current_step": "language_selection",
            "prompt": welcome_text,
            "twiml": twiml,
            "options": [
                {"digit": "1", "label": "English"},
                {"digit": "2", "label": "தமிழ் (Tamil)"},
                {"digit": "3", "label": "हिंदी (Hindi)"},
            ]
        }

    @staticmethod
    def process_step(
        call_sid: str,
        digit: Optional[str],
        speech_text: Optional[str],
        current_step: str,
        db: Session
    ) -> Dict[str, Any]:
        """Process caller DTMF keypress or voice question."""
        log = IVRService.get_or_create_call_log(call_sid, None, db)
        lang = log.language or "en"

        # 1. Handle Language Selection Step
        if current_step == "language" or current_step == "language_selection":
            if digit == "2":
                lang = "ta"
            elif digit == "3":
                lang = "hi"
            else:
                lang = "en"
            
            log.language = lang
            db.commit()

            main_menu_text = IVR_MENUS["main_menu"]["text"].get(lang, IVR_MENUS["main_menu"]["text"]["en"])
            twiml = build_twiml_response(
                say_text=main_menu_text,
                language=lang,
                gather_action=f"{settings.BASE_WEBHOOK_URL}/api/ivr/menu?step=main&call_sid={call_sid}",
                num_digits=1,
                timeout=7,
            )

            options = []
            if lang == "ta":
                options = [
                    {"digit": "1", "label": "விவசாயம் & PM-KISAN"},
                    {"digit": "2", "label": "மாணவர் கல்வி உதவித்தொகை"},
                    {"digit": "3", "label": "மகளிர் நலம் & கலைஞர் உரிமைத்தொகை"},
                    {"digit": "4", "label": "ஆயுஷ்மான் பாரத் மருத்துவ காப்பீடு"},
                    {"digit": "5", "label": "குரல் மூலம் கேள்வி கேட்க"},
                    {"digit": "0", "label": "மொழி மாற்றம்"},
                ]
            elif lang == "hi":
                options = [
                    {"digit": "1", "label": "कृषि और पीएम-किसान"},
                    {"digit": "2", "label": "छात्रवृत्ति योजनाएं"},
                    {"digit": "3", "label": "महिला कल्याण योजनाएं"},
                    {"digit": "4", "label": "आयुष्मान भारत स्वास्थ्य बीमा"},
                    {"digit": "5", "label": "बोलकर प्रश्न पूछें"},
                    {"digit": "0", "label": "भाषा बदलें"},
                ]
            else:
                options = [
                    {"digit": "1", "label": "Agriculture & PM-KISAN"},
                    {"digit": "2", "label": "Student Scholarships"},
                    {"digit": "3", "label": "Women Welfare Schemes"},
                    {"digit": "4", "label": "Ayushman Bharat Healthcare"},
                    {"digit": "5", "label": "Speak your question"},
                    {"digit": "0", "label": "Change language"},
                ]

            return {
                "call_sid": call_sid,
                "current_step": "main_menu",
                "language": lang,
                "prompt": main_menu_text,
                "twiml": twiml,
                "options": options,
            }

        # 2. Handle Main Menu Selection Step
        if current_step == "main" or current_step == "main_menu":
            log.dtmf_digits = (log.dtmf_digits or "") + (digit or "")
            db.commit()

            if digit == "0":
                # Go back to language selection
                return IVRService.handle_initial_call(call_sid, log.caller_phone, db)

            if digit == "5":
                # User wants to speak their query
                prompt_speak = {
                    "ta": "தயவுசெய்து உங்கள் கேள்வியை பீப் சத்தத்திற்கு பிறகு தெளிவாக பேசவும்.",
                    "hi": "कृपया बीप के बाद अपनी समस्या या प्रश्न स्पष्ट रूप से बोलें।",
                    "en": "Please speak your government scheme question clearly after the tone.",
                }.get(lang, "Please speak your question.")

                twiml = build_twiml_response(
                    say_text=prompt_speak,
                    language=lang,
                    gather_action=f"{settings.BASE_WEBHOOK_URL}/api/ivr/menu?step=speech_query&call_sid={call_sid}",
                    record_speech=True,
                    timeout=5,
                )
                return {
                    "call_sid": call_sid,
                    "current_step": "speech_input",
                    "language": lang,
                    "prompt": prompt_speak,
                    "twiml": twiml,
                    "options": [],
                    "is_speech_mode": True,
                }

            # Map digits 1-4 to specific scheme queries
            query_map = {
                "1": ("pm-kisan", "PM-KISAN Samman Nidhi"),
                "2": ("scholarship", "PM Scholarship Scheme"),
                "3": ("women welfare", "Mahila Samman Savings and Women Schemes"),
                "4": ("ayushman bharat", "Ayushman Bharat PM-JAY"),
            }

            intent_info = query_map.get(digit)
            if intent_info:
                search_term, title = intent_info
                log.schemes_mentioned = title
                # Run through agent
                agent_res = SmartGovAIAgent.run_turn(
                    message=f"Explain benefits, eligibility and documents for {title}",
                    user=None,
                    db=db,
                    explicit_language=lang,
                )

                # Formulate concise spoken summary for phone audio
                concise_summary = IVRService._make_phone_friendly_summary(agent_res.reply, lang)
                log.bot_response = concise_summary
                db.commit()

                twiml = build_twiml_response(
                    say_text=concise_summary + (" Press 9 for main menu, or hang up to exit."),
                    language=lang,
                    gather_action=f"{settings.BASE_WEBHOOK_URL}/api/ivr/menu?step=post_answer&call_sid={call_sid}",
                    num_digits=1,
                    timeout=6,
                )

                return {
                    "call_sid": call_sid,
                    "current_step": "scheme_detail",
                    "language": lang,
                    "prompt": concise_summary,
                    "twiml": twiml,
                    "schemes": [s.model_dump() for s in agent_res.schemes_recommended],
                    "options": [
                        {"digit": "9", "label": "Back to Main Menu"},
                        {"digit": "0", "label": "Change Language"},
                        {"digit": "*", "label": "End Call"},
                    ]
                }
            else:
                invalid_msg = {
                    "ta": "தவறான எண். தயவுசெய்து மெனுவில் உள்ள எண்ணை அழுத்தவும்.",
                    "hi": "अमान्य विकल्प। कृपया सूची में से सही संख्या दबाएं।",
                    "en": "Invalid key pressed. Please select a valid option from the menu.",
                }.get(lang, "Invalid selection.")
                return IVRService.process_step(call_sid, None, None, "language", db)

        # 3. Handle Voice Speech Input Step
        if current_step == "speech_query" or current_step == "speech_input":
            query_text = speech_text or "General government schemes"
            log.user_transcript = query_text

            agent_res = SmartGovAIAgent.run_turn(
                message=query_text,
                user=None,
                db=db,
                explicit_language=lang,
            )

            spoken_reply = IVRService._make_phone_friendly_summary(agent_res.reply, lang)
            log.bot_response = spoken_reply
            db.commit()

            twiml = build_twiml_response(
                say_text=spoken_reply + " Press 9 for main menu, or stay on the line to finish.",
                language=lang,
                gather_action=f"{settings.BASE_WEBHOOK_URL}/api/ivr/menu?step=post_answer&call_sid={call_sid}",
                num_digits=1,
                timeout=6,
            )

            return {
                "call_sid": call_sid,
                "current_step": "speech_response",
                "language": lang,
                "prompt": spoken_reply,
                "user_transcript": query_text,
                "twiml": twiml,
                "schemes": [s.model_dump() for s in agent_res.schemes_recommended],
                "options": [
                    {"digit": "9", "label": "Back to Main Menu"},
                    {"digit": "*", "label": "End Call"},
                ]
            }

        # 4. Handle Post Answer Follow-up
        if digit == "9":
            return IVRService.process_step(call_sid, None, None, "language", db)

        # End call
        farewell = {
            "ta": "ஸ்மார்ட்கோவ் உதவி மையத்தை தொடர்பு கொண்டமைக்கு நன்றி. வணக்கம்.",
            "hi": "स्मार्टगोव हेल्पलाइन पर कॉल करने के लिए धन्यवाद। आपका दिन शुभ हो।",
            "en": "Thank you for contacting SmartGov AI Helpline. Have a great day.",
        }.get(lang, "Thank you for calling. Goodbye.")
        
        log.status = "completed"
        db.commit()

        twiml = build_twiml_response(say_text=farewell, language=lang)
        return {
            "call_sid": call_sid,
            "current_step": "call_ended",
            "prompt": farewell,
            "twiml": twiml,
            "options": [],
        }

    @staticmethod
    def _make_phone_friendly_summary(text: str, lang: str) -> str:
        """Convert markdown bullet points into concise spoken conversational audio."""
        clean = text.replace("**", "").replace("•", "").replace("🏛️", "").replace("✅", "").replace("ℹ️", "").replace("❌", "")
        # Remove URLs for voice speech
        import re
        clean = re.sub(r'\[([^\]]+)\]\([^\)]+\)', r'\1', clean)
        clean = re.sub(r'https?://\S+', '', clean)
        lines = [line.strip() for line in clean.split("\n") if line.strip()]
        # Pick first 4 key informative lines for spoken response
        spoken = ". ".join(lines[:4])
        return spoken[:450]
