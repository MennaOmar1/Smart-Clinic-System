from models.db_models import Doctor
from services.availability_service import AvailabilityService
from services.session_service import SessionService
from services.llm_service import LLMService
from services.chatbot_helpers import create_booking
from datetime import datetime, timedelta
import re

def detect_language(text: str) -> str:
    """Detect if text is primarily Arabic or English"""
    arabic_chars = re.findall(r'[\u0600-\u06FF]', text)
    english_chars = re.findall(r'[a-zA-Z]', text)
    
    if len(arabic_chars) > len(english_chars):
        return "ar"
    return "en"

def ensure_session_structure(session):
    if "booking" not in session:
        session["booking"] = {
            "doctor_id": None,
            "specialization": None,
            "date": None,
            "slot": None
        }

    if "doctors" not in session:
        session["doctors"] = []

    if "state" not in session:
        session["state"] = "start"

    return session

SPECIALIZATION_MAP = {
    "dermatologist": "Dermatology",
    "cardiologist": "Cardiology",
    "neurologist": "Neurology"
}


def normalize_date(date_str):
    if not date_str:
        return None

    date_str = str(date_str).lower()

    if date_str == "today":
        return datetime.now().date()

    if date_str == "tomorrow":
        return (datetime.now() + timedelta(days=1)).date()

    try:
        return datetime.fromisoformat(date_str).date()
    except:
        return None

def ensure_booking(session):
    if "booking" not in session or not isinstance(session["booking"], dict):
        session["booking"] = {}

# ---------------- START ----------------
def handle_start(db, user_id, message, session):

    ensure_booking(session)
    session["booking"].clear()  # 🔥 reset clean
    
    # Detect language
    lang = detect_language(message)
    session["language"] = lang

    intent = LLMService.extract_intent(message)
    specialization = intent.get("specialization")
    suggested_reason = intent.get("suggested_reason", "")

    # If no specialization found, ask user to clarify
    if not specialization:
        if lang == "ar":
            reply = "لم أفهم التخصص المطلوب. هل يمكنك وصف أعراضك أو ما تشكو منه؟"
        else:
            reply = "I couldn't determine which specialist you need. Can you describe your symptoms or what you're concerned about?"
        session["state"] = "start"
        SessionService.update(user_id, session)
        return {"reply": reply}

    specialization = SPECIALIZATION_MAP.get(specialization, specialization)

    # If a specialization was suggested, ask user to confirm
    if suggested_reason and not any(keyword in message.lower() for keyword in ["dermatologist", "cardiologist", "neurologist", "دكتور جلدية", "طبيب قلب", "طبيب أعصاب"]):
        if lang == "ar":
            reply = f"بناءً على ما وصفته، أعتقد أنك تحتاج إلى {specialization}. هل تريد المتابعة؟"
        else:
            reply = f"Based on your symptoms, I suggest seeing a {specialization}. Would you like to proceed?"
        session["state"] = "confirm_specialization"
        session["suggested_specialization"] = specialization
        session["language"] = lang
        SessionService.update(user_id, session)
        return {"reply": reply}

    doctors = db.query(Doctor).filter(
        Doctor.specialization.ilike(f"%{specialization}%")
    ).all()

    if not doctors:
        if lang == "ar":
            reply = "لا توجد أطباء متاحة لهذا التخصص حالياً"
        else:
            reply = "No doctors available for this specialization"
        return {"reply": reply}

    doctors_list = [
        {"option": i + 1, "id": d.id, "name": d.user.name}
        for i, d in enumerate(doctors)
    ]

    session["state"] = "choose_doctor"
    session["booking"]["specialization"] = specialization
    session["doctors"] = doctors_list
    session["language"] = lang

    SessionService.update(user_id, session)

    if lang == "ar":
        reply = "👨‍⚕️ اختر أحد الأطباء:"
    else:
        reply = "👨‍⚕️ Choose a doctor:"
    
    return {
        "reply": reply,
        "doctors": doctors_list
    }


# ---------------- CONFIRM SPECIALIZATION ----------------
def handle_confirm_specialization(db, user_id, message, session):
    lang = session.get("language", "en")
    suggested_spec = session.get("suggested_specialization")
    
    # Check if user confirms (yes, ok, نعم, حسناً, etc.)
    if message.lower() in ["yes", "ok", "sure", "proceed", "نعم", "حسناً", "تمام", "ايه"]:
        doctors = db.query(Doctor).filter(
            Doctor.specialization.ilike(f"%{suggested_spec}%")
        ).all()
        
        if not doctors:
            if lang == "ar":
                reply = "لا توجد أطباء متاحة حالياً"
            else:
                reply = "No doctors available right now"
            return {"reply": reply}
        
        doctors_list = [
            {"option": i + 1, "id": d.id, "name": d.user.name}
            for i, d in enumerate(doctors)
        ]
        
        session["state"] = "choose_doctor"
        session["booking"]["specialization"] = suggested_spec
        session["doctors"] = doctors_list
        SessionService.update(user_id, session)
        
        if lang == "ar":
            reply = "👨‍⚕️ اختر أحد الأطباء:"
        else:
            reply = "👨‍⚕️ Choose a doctor:"
        
        return {
            "reply": reply,
            "doctors": doctors_list
        }
    else:
        if lang == "ar":
            reply = "حسناً، ابدأ من البداية: أخبرني عن مشكلتك الصحية"
        else:
            reply = "Okay, let's start over. Tell me about your health concern"
        session["state"] = "start"
        SessionService.update(user_id, session)
        return {"reply": reply}
    
    
# ---------------- DOCTOR ----------------
def handle_choose_doctor(db, user_id, message, session):

    doctors = session.get("doctors")
    lang = session.get("language", "en")

    if not doctors:
        if lang == "ar":
            reply = "❌ انتهت الجلسة"
        else:
            reply = "❌ Session expired"
        return {"reply": reply}

    try:
        choice = int(message.strip())
        doctor = doctors[choice - 1]
    except:
        if lang == "ar":
            reply = "❌ اختيار غير صحيح"
        else:
            reply = "❌ Invalid choice"
        return {"reply": reply}
    
    ensure_booking(session)
    session["booking"]["doctor_id"] = doctor["id"]   
    session["state"] = "choose_date"

    SessionService.update(user_id, session)

    if lang == "ar":
        reply = "📅 أدخل التاريخ (YYYY-MM-DD أو 'tomorrow'):"
    else:
        reply = "📅 Enter date (YYYY-MM-DD or 'tomorrow')"
    
    return {"reply": reply}

# ---------------- DATE ----------------
def handle_choose_date(db, user_id, message, session):

    doctor_id = session.get("booking", {}).get("doctor_id")
    lang = session.get("language", "en")

    if not doctor_id:
        if lang == "ar":
            reply = "❌ انتهت الجلسة"
        else:
            reply = "❌ Session expired"
        return {"reply": reply}

    date = normalize_date(message)

    if not date:
        if lang == "ar":
            reply = "❌ صيغة التاريخ غير صحيحة"
        else:
            reply = "❌ Invalid date format"
        return {"reply": reply}

    slots = AvailabilityService.get_available_slots(db, doctor_id, date)

    if not slots:
        if lang == "ar":
            reply = "❌ لا توجد فترات متاحة"
        else:
            reply = "❌ No slots available"
        return {"reply": reply}
    
    ensure_booking(session)
    session["booking"]["date"] = str(date)
    session["state"] = "choose_slot"

    session["slots"] = slots

    SessionService.update(user_id, session)

    if lang == "ar":
        reply = "🕒 اختر فترة زمنية:"
    else:
        reply = "🕒 Choose a slot:"
    
    return {
        "reply": reply,
        "slots": [
            {"option": i + 1, "time": s}
            for i, s in enumerate(slots)
        ]
    }

# ---------------- SLOT ----------------
def handle_choose_slot(db, user_id, message, session):

    slots = session.get("slots", [])
    lang = session.get("language", "en")

    if not message.isdigit():
        if lang == "ar":
            reply = "❌ أدخل رقماً"
        else:
            reply = "❌ Enter a number"
        return {"reply": reply}

    idx = int(message) - 1

    if idx < 0 or idx >= len(slots):
        if lang == "ar":
            reply = "❌ فترة غير صحيحة"
        else:
            reply = "❌ Invalid slot"
        return {"reply": reply}

    slot = slots[idx]
    
    ensure_booking(session)
    session["booking"]["slot"] = slot   
    session["state"] = "collect_name"

    SessionService.update(user_id, session)

    if lang == "ar":
        reply = "👤 ما اسمك؟"
    else:
        reply = "👤 What's your name?"
    
    return {"reply": reply}

# ---------------- COLLECT NAME ----------------
def handle_collect_name(db, user_id, message, session):

    name = message.strip()

    if not name or len(name) < 2:
        lang = session.get("language", "en")
        if lang == "ar":
            reply = "❌ الرجاء إدخال اسم صحيح"
        else:
            reply = "❌ Please enter a valid name"
        return {"reply": reply}

    ensure_booking(session)
    session["booking"]["patient_name"] = name
    session["state"] = "collect_phone"

    SessionService.update(user_id, session)

    lang = session.get("language", "en")
    if lang == "ar":
        reply = "📞 رقم هاتفك (مثال: 201001234567):"
    else:
        reply = "📞 Your phone number (example: 201001234567):"
    
    return {"reply": reply}

# ---------------- COLLECT PHONE ----------------
def handle_collect_phone(db, user_id, message, session):

    phone = message.strip().replace(" ", "").replace("-", "")

    # Basic phone validation - should be digits and at least 10 chars
    if not phone.isdigit() or len(phone) < 10:
        lang = session.get("language", "en")
        if lang == "ar":
            reply = "❌ الرجاء إدخال رقم هاتف صحيح"
        else:
            reply = "❌ Please enter a valid phone number"
        return {"reply": reply}

    ensure_booking(session)
    session["booking"]["patient_phone"] = phone
    session["state"] = "confirm"

    SessionService.update(user_id, session)

    lang = session.get("language", "en")
    if lang == "ar":
        reply = f"✅ هل تؤكد الحجز؟ (نعم/لا)"
    else:
        reply = f"✅ Confirm booking? (yes/no)"
    
    return {"reply": reply}

# ---------------- COLLECT EMAIL ----------------
def handle_collect_email(db, user_id, message, session):

    email = message.strip()

    # Basic email validation
    import re
    email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    
    if not re.match(email_pattern, email):
        return {"reply": "❌ Please enter a valid email address:"}

    ensure_booking(session)
    session["booking"]["patient_email"] = email
    session["state"] = "confirm"

    SessionService.update(user_id, session)

    slot = session["booking"].get("slot")
    return {"reply": f"✅ Confirm booking at {slot}? (yes/no)"}


# ---------------- CONFIRM ----------------
def handle_confirm(db, user_id, message, session):

    msg = message.lower().strip()

    ensure_booking(session)
    booking = session["booking"]

    doctor_id = booking.get("doctor_id")
    slot = booking.get("slot")
    patient_name = booking.get("patient_name", "Chat User")
    patient_phone = booking.get("patient_phone")

    # 🔥 DEBUG (optional but powerful)
    print("BOOKING DEBUG:", booking)

    if not doctor_id or not slot:
        SessionService.reset(user_id)
        lang = session.get("language", "en")
        if lang == "ar":
            reply = "❌ انتهت الجلسة (بيانات ناقصة)"
        else:
            reply = "❌ Session expired (missing data)"
        return {"reply": reply}

    if msg in ["yes", "y", "ok", "confirm", "تمام", "أيوه", "نعم"]:

        try:
            start_time = datetime.fromisoformat(slot)
        except:
            lang = session.get("language", "en")
            if lang == "ar":
                reply = "❌ صيغة الوقت غير صحيحة"
            else:
                reply = "❌ Invalid slot format"
            return {"reply": reply}

        try:
            create_booking(db, {
                "doctor_id": doctor_id,
                "user_id": user_id,
                "start_time": start_time,
                "patient_name": patient_name,
                "patient_phone": patient_phone,
                "patient_email": booking.get("patient_email")
            })
        except Exception as e:
            print("BOOKING ERROR:", e)
            lang = session.get("language", "en")
            if lang == "ar":
                reply = "❌ فشل إنشاء الحجز"
            else:
                reply = "❌ Failed to create booking"
            return {"reply": reply}

        SessionService.reset(user_id)
        lang = session.get("language", "en")
        if lang == "ar":
            reply = "🎉 تم تأكيد الحجز"
        else:
            reply = "🎉 Booking confirmed"
        return {"reply": reply}

    SessionService.reset(user_id)
    lang = session.get("language", "en")
    if lang == "ar":
        reply = "❌ تم إلغاء الحجز"
    else:
        reply = "❌ Booking cancelled"
    return {"reply": reply}


# ======================================================
# ROUTER
# ======================================================

STATE_HANDLERS = {
    "start": handle_start,
    "confirm_specialization": handle_confirm_specialization,
    "choose_doctor": handle_choose_doctor,
    "choose_date": handle_choose_date,
    "choose_slot": handle_choose_slot,
    "collect_name": handle_collect_name,
    "collect_phone": handle_collect_phone,
    "collect_email": handle_collect_email,
    "confirm": handle_confirm
}


# ======================================================
# MAIN SERVICE
# ======================================================

class ChatbotService:

    @staticmethod
    def is_new_request(message) -> bool:
        if not isinstance(message, str):
            return False

        message = message.lower()

        triggers = [
            "احجز",
            "عايز احجز",
            "book",
            "appointment",
            "دكتور",
            "doctor",
            "عيادة",
            "clinic"
        ]

        return any(t in message for t in triggers)


    @staticmethod
    def handle_chat(db, user_id: str, message: str):

        session = SessionService.get(user_id)

        if not session:
            session = SessionService.init()

        session = ensure_session_structure(session)
        SessionService.update(user_id, session)

        state = session.get("state") or "start"
        session.setdefault("data", {})

        # ✅ FIXED CALL + SAFE RESET LOGIC
        if state != "start" and ChatbotService.is_new_request(message):

            session = {
                "state": "start",
                "data": {}
            }

            SessionService.update(user_id, session)
            state = "start"

        handler = STATE_HANDLERS.get(state, handle_start)

        return handler(db, user_id, message, session)