from models.db_models import Doctor
from models.db_models import Appointment
from datetime import datetime

def get_doctors_by_specialization(db, specialization):
    return db.query(Doctor).filter(
        Doctor.specialization == specialization
    ).all()


def create_booking(db, data):

    doctor_id = data.get("doctor_id")
    patient_id = data.get("user_id")
    start_time = data.get("start_time")

    if not doctor_id or not patient_id or not start_time:
        raise ValueError("Missing booking data")

    appointment = Appointment(
        doctor_id=doctor_id,
        patient_id=patient_id,
        start_time=start_time,
        status="SCHEDULED"
    )

    db.add(appointment)
    db.commit()
    db.refresh(appointment)

    return appointment


def set_doctor(session, doctor_id):
    session["booking"]["doctor_id"] = doctor_id
    return session


def set_date(session, date):
    session["booking"]["date"] = date
    return session


def set_slot(session, slot):
    session["booking"]["slot"] = slot
    return session