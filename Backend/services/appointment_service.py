from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import func
import json

from services.calendar_sync_service import CalendarSyncService
from models.db_models import Appointment, Patient, Doctor, WorkingHours


class AppointmentService:

    SLOT_MINUTES = 30

    # =========================
    # ENRICH RESPONSE (NEW)
    # =========================
    @staticmethod
    def enrich_appointment(appt: Appointment):
        if not appt:
            return None

        return {
            "id": appt.id,
            "doctor_id": appt.doctor_id,
            "doctor_name": appt.doctor.user.name if appt.doctor and appt.doctor.user else None,

            "patient_id": appt.patient_id,
            "patient_name": appt.patient.name if appt.patient else None,

            "start_time": appt.start_time,
            "end_time": appt.end_time,
            "status": appt.status,
            "notes": appt.notes,
            "google_event_id": appt.google_event_id,
            "reminder_time": appt.reminder_time
        }

    # =========================
    # PATIENT
    # =========================
    @staticmethod
    def get_or_create_patient(db: Session, name, phone, email=None):
        patient = db.query(Patient).filter(Patient.phone == phone).first()

        if not patient:
            patient = Patient(name=name, phone=phone, email=email)
            db.add(patient)
            db.commit()
            db.refresh(patient)

        elif email and not patient.email:
            patient.email = email
            db.commit()

        return patient

    # =========================
    # WORKING HOURS
    # =========================
    @staticmethod
    def get_working_hours(db, doctor_id, date):
        return db.query(WorkingHours).filter(
            WorkingHours.doctor_id == doctor_id,
            WorkingHours.day_of_week == date.weekday()
        ).first()

    # =========================
    # GENERATE SLOTS
    # =========================
    @staticmethod
    def generate_slots(db: Session, doctor_id: int, date: datetime):

        working = AppointmentService.get_working_hours(db, doctor_id, date)
        if not working:
            return []

        start = datetime.combine(
            date,
            datetime.strptime(working.start_time, "%H:%M").time()
        )

        end = datetime.combine(
            date,
            datetime.strptime(working.end_time, "%H:%M").time()
        )

        appointments = db.query(Appointment).filter(
            Appointment.doctor_id == doctor_id,
            Appointment.status != "CANCELLED"
        ).all()

        booked = {
            a.start_time.replace(second=0, microsecond=0)
            for a in appointments
            if a.start_time.date() == date
        }

        now = datetime.now().replace(second=0, microsecond=0)

        slots = []
        current = start

        while current < end:

            if date == now.date():
                if current > now and current not in booked:
                    slots.append(current)
            else:
                if current not in booked:
                    slots.append(current)

            current += timedelta(minutes=30)

        return slots

    # =========================
    # AVAILABILITY CHECK
    # =========================
    @staticmethod
    def is_available(db: Session, doctor_id: int, start_time: datetime):

        start_time = start_time.replace(second=0, microsecond=0)

        exists = db.query(Appointment).filter(
            Appointment.doctor_id == doctor_id,
            func.date_trunc('minute', Appointment.start_time) == start_time,
            Appointment.status != "CANCELLED"
        ).first()

        return exists is None

    # =========================
    # BOOK APPOINTMENT
    # =========================
    @staticmethod
    def book_appointment(
        db: Session,
        doctor_id: int,
        start_time: datetime,
        patient_name: str,
        patient_phone: str,
        patient_email: str | None = None,
        notes: str | None = None,
        credentials=None
    ):

        start_time = start_time.replace(second=0, microsecond=0)

        doctor = db.query(Doctor).filter(Doctor.id == doctor_id).first()
        if not doctor:
            raise Exception("Doctor not found")

        if not AppointmentService.is_available(db, doctor_id, start_time):
            raise Exception("Time slot already booked")

        patient = AppointmentService.get_or_create_patient(
            db, patient_name, patient_phone, patient_email
        )

        end_time = start_time + timedelta(minutes=30)
        reminder_time = start_time - timedelta(hours=1)

        appointment = Appointment(
            doctor_id=doctor_id,
            patient_id=patient.id,
            start_time=start_time,
            end_time=end_time,
            status="SCHEDULED",
            notes=notes,
            reminder_time=reminder_time
        )

        db.add(appointment)
        db.commit()
        db.refresh(appointment)

        # =========================
        # GOOGLE SYNC
        # =========================
        google_event_id = None

        google_creds = credentials

        if not google_creds and doctor.google_token:
            try:
                google_creds = json.loads(doctor.google_token)
            except:
                google_creds = None

        if google_creds:
            google_event_id = CalendarSyncService.create(
                appointment,
                google_creds
            )

            if google_event_id:
                appointment.google_event_id = google_event_id
                db.commit()
                db.refresh(appointment)
        print("GOOGLE CREDS RECEIVED:", credentials)
        return appointment

    # =========================
    # GET ALL (ENRICHED)
    # =========================
    @staticmethod
    def get_all(db: Session):
        appointments = db.query(Appointment).all()
        return [AppointmentService.enrich_appointment(a) for a in appointments]

    # =========================
    # GET ONE (ENRICHED)
    # =========================
    @staticmethod
    def get_by_id(db: Session, appointment_id: int):
        appt = db.query(Appointment).filter(
            Appointment.id == appointment_id
        ).first()

        return AppointmentService.enrich_appointment(appt)

    # =========================
    # CANCEL
    # =========================
    @staticmethod
    def cancel(db: Session, appointment_id: int, credentials=None):

        appt = db.query(Appointment).filter(
            Appointment.id == appointment_id
        ).first()

        if not appt:
            raise Exception("Appointment not found")

        appt.status = "CANCELLED"

        CalendarSyncService.delete(appt, credentials)

        db.commit()
        db.refresh(appt)

        return AppointmentService.enrich_appointment(appt)

    # =========================
    # RESCHEDULE
    # =========================
    @staticmethod
    def reschedule(db: Session, appointment_id: int, new_time: datetime, credentials=None):

        appt = db.query(Appointment).filter(
            Appointment.id == appointment_id
        ).first()

        if not appt:
            raise Exception("Appointment not found")

        new_time = new_time.replace(second=0, microsecond=0)

        if not AppointmentService.is_available(db, appt.doctor_id, new_time):
            raise Exception("Time slot already booked")

        appt.start_time = new_time
        appt.end_time = new_time + timedelta(minutes=30)
        appt.status = "RESCHEDULED"

        CalendarSyncService.update(appt, new_time, credentials)

        db.commit()
        db.refresh(appt)

        return AppointmentService.enrich_appointment(appt)

    # =========================
    # CHATBOT BOOKING (FIXED)
    # =========================
    @staticmethod
    def book_from_chatbot(db, doctor_id, start_time, patient_name, patient_phone):

        start_time = datetime.fromisoformat(start_time)

        if not AppointmentService.is_available(db, doctor_id, start_time):
            raise Exception("Slot not available")

        patient = AppointmentService.get_or_create_patient(
            db, patient_name, patient_phone
        )

        appointment = Appointment(
            doctor_id=doctor_id,
            patient_id=patient.id,
            start_time=start_time,
            end_time=start_time + timedelta(minutes=30),
            status="SCHEDULED",
            reminder_time=start_time - timedelta(hours=1)
        )

        db.add(appointment)
        db.commit()
        db.refresh(appointment)

        return AppointmentService.enrich_appointment(appointment)

    # =========================
    # UPDATE STATUS
    # =========================
    @staticmethod
    def update_status(db: Session, appointment_id: int, status: str):

        appt = db.query(Appointment).filter(
            Appointment.id == appointment_id
        ).first()

        if not appt:
            raise Exception("Appointment not found")

        allowed = ["SCHEDULED", "COMPLETED", "CANCELLED", "NO_SHOW"]

        if status not in allowed:
            raise Exception("Invalid status")

        appt.status = status
        db.commit()
        db.refresh(appt)

        return AppointmentService.enrich_appointment(appt)

    # =========================
    # ADD NOTES
    # =========================
    @staticmethod
    def add_notes(db: Session, appointment_id: int, notes: str):

        appt = db.query(Appointment).filter(
            Appointment.id == appointment_id
        ).first()

        if not appt:
            raise Exception("Appointment not found")

        appt.notes = notes
        db.commit()
        db.refresh(appt)

        return AppointmentService.enrich_appointment(appt)