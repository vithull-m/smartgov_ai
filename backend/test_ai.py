import sys
import io
from app.core.database import SessionLocal
from app.services.ai_service import chat_completion

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
db = SessionLocal()

tests = [
    ('farmer loan subsidy scheme', 'en'),
    ('scholarship for higher education', 'en'),
    ('விவசாய கடன் திட்டம்', 'ta'),
    ('महिला स्वरोजगार योजना', 'hi')
]

for q, lang in tests:
    print('========================================')
    print(f'TEST: "{q}" ({lang})')
    print('========================================')
    reply = chat_completion(q, language=lang, db=db)
    print(reply[:300] + '...\n')

db.close()
