import uuid
import uuid
from models.db_models import Doctor, Patient, Appointment
from services.appointment_service import AppointmentService
from datetime import datetime, timedelta

def get_doctors_by_specialization(db, specialization):
    return db.query(Doctor).filter(
        Doctor.specialization == specialization
    ).all()


def create_booking(db, data):

    doctor_id = data.get("doctor_id")
    start_time = data.get("start_time")
    patient_name = data.get("patient_name", "Chat User")
    patient_email = data.get("patient_email")
    patient_phone = data.get("patient_phone")

    if not doctor_id or not start_time:
        raise ValueError("Missing booking data")

    if isinstance(start_time, str):
        try:
            start_time = datetime.fromisoformat(start_time)
        except Exception:
            raise ValueError("Invalid start_time format")

    if not patient_phone:
        patient_phone = f"chat-{uuid.uuid4()}"

    return AppointmentService.book_appointment(
        db=db,
        doctor_id=doctor_id,
        start_time=start_time,
        patient_name=patient_name,
        patient_phone=patient_phone,
        patient_email=patient_email,
        notes=data.get("notes")
    )


def set_doctor(session, doctor_id):
    session["booking"]["doctor_id"] = doctor_id
    return session


def set_date(session, date):
    session["booking"]["date"] = date
    return session


def set_slot(session, slot):
    session["booking"]["slot"] = slot
    return session