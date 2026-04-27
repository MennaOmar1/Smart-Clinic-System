from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import func
from services.calendar_sync_service import CalendarSyncService
from models.db_models import Appointment, Patient, Doctor, WorkingHours


class AppointmentService:

    SLOT_MINUTES = 30

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

        # appointments for this doctor ONLY for that day
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

        #  Google sync 
        google_event_id = None

        if credentials:
            google_event_id = CalendarSyncService.create(
                appointment,
                credentials
            )

            if google_event_id:
                appointment.google_event_id = google_event_id
                db.commit()

        return appointment


    # =========================
    # GET ALL
    # =========================
    @staticmethod
    def get_all(db: Session):
        return db.query(Appointment).all()


    # =========================
    # GET ONE
    # =========================
    @staticmethod
    def get_by_id(db: Session, appointment_id: int):
        return db.query(Appointment).filter(
            Appointment.id == appointment_id
        ).first()


    # =========================
    # CANCEL
    # =========================
    @staticmethod
    def cancel(db: Session, appointment_id: int, credentials=None):

        appt = AppointmentService.get_by_id(db, appointment_id)

        if not appt:
            raise Exception("Appointment not found")

        appt.status = "CANCELLED"

        #  Google sync
        CalendarSyncService.delete(appt, credentials)

        db.commit()
        return appt


    # =========================
    # RESCHEDULE
    # =========================
    @staticmethod
    def reschedule(db: Session, appointment_id: int, new_time: datetime, credentials=None):

        appt = AppointmentService.get_by_id(db, appointment_id)

        if not appt:
            raise Exception("Appointment not found")

        new_time = new_time.replace(second=0, microsecond=0)

        if not AppointmentService.is_available(db, appt.doctor_id, new_time):
            raise Exception("Time slot already booked")

        appt.start_time = new_time
        appt.end_time = new_time + timedelta(minutes=30)
        appt.status = "RESCHEDULED"

        #  Google sync
        CalendarSyncService.update(appt, new_time, credentials)

        db.commit()
        return appt
    


    @staticmethod
    def book_from_chatbot(db, doctor_id, start_time, patient_name, patient_phone):

        start_time = datetime.fromisoformat(start_time)

        if not AppointmentService.is_available(db, doctor_id, start_time):
            raise Exception("Slot not available")

        patient = AppointmentService.get_or_create_patient(db, patient_name, patient_phone)

        appointment = Appointment(
            doctor_id=doctor_id,
            patient_id=patient.id,
            start_time=start_time,
            end_time=start_time + timedelta(minutes=30),
            status="SCHEDULED"
        )

        db.add(appointment)
        db.commit()
        db.refresh(appointment)

        return appointment
    



    @staticmethod
    def update_status(db: Session, appointment_id: int, status: str):

        appt = AppointmentService.get_by_id(db, appointment_id)

        if not appt:
            raise Exception("Appointment not found")

        allowed = ["SCHEDULED", "COMPLETED", "CANCELLED", "NO_SHOW"]

        if status not in allowed:
            raise Exception("Invalid status")

        appt.status = status
        db.commit()
        db.refresh(appt)

        return appt
    

    # add notes
    @staticmethod
    def add_notes(db: Session, appointment_id: int, notes: str):

        appt = AppointmentService.get_by_id(db, appointment_id)

        if not appt:
            raise Exception("Appointment not found")

        appt.notes = notes
        db.commit()
        db.refresh(appt)

        return appt