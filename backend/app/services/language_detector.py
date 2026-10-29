"""
Automatic Language Detection Module for SmartGov AI.
Supports Tamil, English, Hindi, Tanglish / mixed code-switching, and Indian languages.
Without language-selection buttons or dropdowns.
"""
import re
from typing import Tuple, Optional

# Unicode ranges for major Indian scripts
# Tamil: 0B80 - 0BFF
# Devanagari (Hindi, Marathi): 0900 - 097F
# Telugu: 0C00 - 0C7F
# Kannada: 0C80 - 0CFF
# Malayalam: 0D00 - 0D7F
# Bengali: 0980 - 09FF

TAMIL_PATTERN = re.compile(r"[\u0B80-\u0BFF]")
DEVANAGARI_PATTERN = re.compile(r"[\u0900-\u097F]")
TELUGU_PATTERN = re.compile(r"[\u0C00-\u0C7F]")
KANNADA_PATTERN = re.compile(r"[\u0C80-\u0CFF]")
MALAYALAM_PATTERN = re.compile(r"[\u0D00-\u0D7F]")
BENGALI_PATTERN = re.compile(r"[\u0980-\u09FF]")

# Common Tamil romanized keywords (Tanglish)
TANGLISH_KEYWORDS = {
    "thittam", "thittangal", "enaku", "enakku", "vivasayi", "vivasayam",
    "manavargal", "manavan", "pengal", "udhavi", "udhavithogai", "kaasu",
    "kadan", "eppadi", "pannuvathu", "theriyuma", "arasaangam",
    "arasu", "naan", "yaarukku", "theva", "thevai", "panam", "patta",
    "kudumbam", "kudumba", "padippu", "kalluri", "palli", "mudiyuma",
    "solunga", "solleenga", "edhavadhu", "edhavathu", "undaa", "irukka",
    "irukku", "vanakkam", "nandri"
}


# Common Hindi romanized keywords (Hinglish)
HINGLISH_KEYWORDS = {
    "yojana", "yojanaye", "yojanayen", "kisan", "krishi", "chhatravritti",
    "chhatra", "mahila", "kare", "karna", "kaise", "milega", "hoga",
    "sarkar", "sarkari", "mujhe", "mera", "meri", "hum", "paisa", "rupaye",
    "batao", "bataiye", "chahiye", "patrata", "aavedan"
}

LANGUAGE_NAMES = {
    "ta": "Tamil (தமிழ்)",
    "en": "English",
    "hi": "Hindi (हिंदी)",
    "te": "Telugu (తెలుగు)",
    "kn": "Kannada (ಕನ್ನಡ)",
    "ml": "Malayalam (മലയാളം)",
    "bn": "Bengali (বাংলা)",
}


def detect_language(text: str, fallback_language: str = "en") -> Tuple[str, float, bool]:
    """
    Detect language of user text.
    Returns:
        (detected_lang_code, confidence_score, needs_clarification)
    """
    if not text or not text.strip():
        return fallback_language, 0.5, False

    clean_text = text.strip()
    words = re.findall(r"\w+", clean_text.lower())
    total_chars = len(clean_text)

    # 1. Native script detection
    tamil_chars = len(TAMIL_PATTERN.findall(clean_text))
    devanagari_chars = len(DEVANAGARI_PATTERN.findall(clean_text))
    telugu_chars = len(TELUGU_PATTERN.findall(clean_text))
    kannada_chars = len(KANNADA_PATTERN.findall(clean_text))
    malayalam_chars = len(MALAYALAM_PATTERN.findall(clean_text))
    bengali_chars = len(BENGALI_PATTERN.findall(clean_text))

    script_counts = [
        ("ta", tamil_chars),
        ("hi", devanagari_chars),
        ("te", telugu_chars),
        ("kn", kannada_chars),
        ("ml", malayalam_chars),
        ("bn", bengali_chars),
    ]
    script_counts.sort(key=lambda x: x[1], reverse=True)
    top_script, top_script_count = script_counts[0]

    if top_script_count > 0:
        # If there are native script characters present
        ratio = top_script_count / max(total_chars, 1)
        # Even a few characters or mixed with English loanwords -> prioritize native script
        if top_script_count >= 2 or ratio > 0.05:
            confidence = min(0.99, 0.70 + (top_script_count / total_chars) * 0.3)
            return top_script, round(confidence, 2), False

    # 2. Tanglish & Hinglish (Romanized / transliterated words)
    tanglish_matches = sum(1 for w in words if w in TANGLISH_KEYWORDS)
    hinglish_matches = sum(1 for w in words if w in HINGLISH_KEYWORDS)

    if tanglish_matches >= 1 and tanglish_matches >= hinglish_matches:
        confidence = min(0.95, 0.65 + (tanglish_matches / max(len(words), 1)) * 0.3)
        return "ta", round(confidence, 2), False

    if hinglish_matches >= 1 and hinglish_matches > tanglish_matches:
        confidence = min(0.95, 0.65 + (hinglish_matches / max(len(words), 1)) * 0.3)
        return "hi", round(confidence, 2), False

    # 3. Pure numbers or 1-character ambiguous text
    letters = re.findall(r"[a-zA-Z]", clean_text)
    if not letters:
        return fallback_language, 0.5, True

    # 4. Standard English
    # English Latin words
    return "en", 0.95, False


def get_language_clarification_prompt(detected_lang: str) -> str:
    """Return polite clarification in detected language if ambiguous."""
    if detected_lang == "ta":
        return "வணக்கம்! நீங்கள் தமிழில் தகவல்களைப் பெற விரும்புகிறீர்களா? உங்கள் கேள்வியை விளக்கமாக கேளுங்கள்."
    elif detected_lang == "hi":
        return "नमस्ते! क्या आप हिंदी में जानकारी प्राप्त करना चाहते हैं? कृपया अपना प्रश्न पूछें।"
    return "Hello! Would you like assistance in English or Tamil? Please tell me about your query."
