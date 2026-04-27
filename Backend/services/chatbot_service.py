from models.db_models import Doctor
from services.availability_service import AvailabilityService
from services.session_service import SessionService
from services.llm_service import LLMService
from services.chatbot_helpers import create_booking
from datetime import datetime, timedelta

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

    intent = LLMService.extract_intent(message)
    specialization = intent.get("specialization") or "dermatologist"

    specialization = SPECIALIZATION_MAP.get(specialization, specialization)

    doctors = db.query(Doctor).filter(
        Doctor.specialization.ilike(f"%{specialization}%")
    ).all()

    if not doctors:
        return {"reply": "No doctors available"}

    doctors_list = [
        {"option": i + 1, "id": d.id, "name": d.user.name}
        for i, d in enumerate(doctors)
    ]

    session["state"] = "choose_doctor"
    session["booking"]["specialization"] = specialization
    session["doctors"] = doctors_list

    SessionService.update(user_id, session)

    return {
        "reply": "👨‍⚕️ Choose a doctor:",
        "doctors": doctors_list
    }
    
    
# ---------------- DOCTOR ----------------
def handle_choose_doctor(db, user_id, message, session):

    doctors = session.get("doctors")

    if not doctors:
        return {"reply": "❌ Session expired"}

    try:
        choice = int(message.strip())
        doctor = doctors[choice - 1]
    except:
        return {"reply": "❌ Invalid choice"}
    
    ensure_booking(session)
    session["booking"]["doctor_id"] = doctor["id"]   
    session["state"] = "choose_date"

    SessionService.update(user_id, session)

    return {"reply": "📅 Enter date (YYYY-MM-DD or 'tomorrow')"}

# ---------------- DATE ----------------
def handle_choose_date(db, user_id, message, session):

    doctor_id = session.get("booking", {}).get("doctor_id")

    if not doctor_id:
        return {"reply": "❌ Session expired"}

    date = normalize_date(message)

    if not date:
        return {"reply": "❌ Invalid date format"}

    slots = AvailabilityService.get_available_slots(db, doctor_id, date)

    if not slots:
        return {"reply": "❌ No slots available"}
    
    ensure_booking(session)
    session["booking"]["date"] = str(date)
    session["state"] = "choose_slot"

    session["slots"] = slots

    SessionService.update(user_id, session)

    return {
        "reply": "🕒 Choose a slot:",
        "slots": [
            {"option": i + 1, "time": s}
            for i, s in enumerate(slots)
        ]
    }

# ---------------- SLOT ----------------
def handle_choose_slot(db, user_id, message, session):

    slots = session.get("slots", [])

    if not message.isdigit():
        return {"reply": "❌ Enter a number"}

    idx = int(message) - 1

    if idx < 0 or idx >= len(slots):
        return {"reply": "❌ Invalid slot"}

    slot = slots[idx]
    
    ensure_booking(session)
    session["booking"]["slot"] = slot   
    session["state"] = "confirm"

    SessionService.update(user_id, session)

    return {"reply": f"✅ Confirm booking at {slot}? (yes/no)"}

# ---------------- CONFIRM ----------------
def handle_confirm(db, user_id, message, session):

    msg = message.lower().strip()

    ensure_booking(session)
    booking = session["booking"]

    doctor_id = booking.get("doctor_id")
    slot = booking.get("slot")

    # 🔥 DEBUG (optional but powerful)
    print("BOOKING DEBUG:", booking)

    if not doctor_id or not slot:
        SessionService.reset(user_id)
        return {"reply": "❌ Session expired (missing data)"}

    if msg in ["yes", "y", "ok", "confirm", "تمام", "أيوه"]:

        try:
            start_time = datetime.fromisoformat(slot)
        except:
            return {"reply": "❌ Invalid slot format"}

        try:
            create_booking(db, {
                "doctor_id": doctor_id,
                "user_id": user_id,
                "start_time": start_time
            })
        except Exception as e:
            print("BOOKING ERROR:", e)
            return {"reply": "❌ Failed to create booking"}

        SessionService.reset(user_id)
        return {"reply": "🎉 Booking confirmed"}

    SessionService.reset(user_id)
    return {"reply": "❌ Booking cancelled"}


# ======================================================
# ROUTER
# ======================================================

STATE_HANDLERS = {
    "start": handle_start,
    "choose_doctor": handle_choose_doctor,
    "choose_date": handle_choose_date,
    "choose_slot": handle_choose_slot,
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