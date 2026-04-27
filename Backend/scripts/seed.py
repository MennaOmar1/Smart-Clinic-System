from sqlalchemy.orm import Session
from core.database import SessionLocal
from models.db_models import User, Doctor, Patient, Appointment, WorkingHours
from datetime import datetime, timedelta
from core.security import hash_password
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

def seed():
    db: Session = SessionLocal()

    # =========================
    # CLEAN DATABASE (optional but recommended)
    # =========================
    print("Cleaning database...")
    db.query(Appointment).delete()
    db.query(WorkingHours).delete()
    db.query(Doctor).delete()
    db.query(Patient).delete()
    db.query(User).delete()
    db.commit()

    # =========================
    # USERS
    # =========================
    print("Creating users...")

    admin = User(
        email="drmagdyfahmi9@gmail.com",
        password=hash_password("admin123"),
        role="admin",
        is_active=True
    )

    doctor_user1 = User(
        email="mennaeb743@gmail.com",
        password=hash_password("doctor1"),
        role="doctor",
        name="Dr. Ahmed Hassan",
        is_active=True
    )

    doctor_user2 = User(
        email="omarmenna041@gmail.com",
        password=hash_password("doctor2"),
        role="doctor",
        name="Dr. Sara Ali",
        is_active=True
    )

    receptionist = User(
        email="mennaomardevops@gmail.com",
        password=hash_password("receptionist123"),
        role="receptionist",
        is_active=True
    )

    db.add_all([admin, doctor_user1, doctor_user2, receptionist])
    db.commit()

    # =========================
    # DOCTORS
    # =========================
    print("Creating doctors...")

    doctor1 = Doctor(
        user_id=doctor_user1.id,
        specialization="Cardiology"
    )

    doctor2 = Doctor(
        user_id=doctor_user2.id,
        specialization="Dermatology"
    )

    db.add_all([doctor1, doctor2])
    db.commit()

    # =========================
    # WORKING HOURS
    # =========================
    print("Creating working hours...")

    working_hours = []

    for doctor in [doctor1, doctor2]:
        for day in range(0, 5):  # Monday → Friday
            working_hours.append(
                WorkingHours(
                    doctor_id=doctor.id,
                    day_of_week=day,
                    start_time="09:00",
                    end_time="17:00"
                )
            )

    db.add_all(working_hours)
    db.commit()

    # =========================
    # PATIENTS
    # =========================
    print("Creating patients...")

    patient1 = Patient(
        name="Ahmed Ali",
        phone="01000000001",
        email="ahmed@test.com"
    )

    patient2 = Patient(
        name="Sara Mohamed",
        phone="01000000002",
        email="sara@test.com"
    )

    db.add_all([patient1, patient2])
    db.commit()

    # =========================
    # APPOINTMENTS
    # =========================
    print("Creating appointments...")

    now = datetime.now()

    appt1 = Appointment(
        doctor_id=doctor1.id,
        patient_id=patient1.id,
        start_time=now + timedelta(days=1, hours=1),
        end_time=now + timedelta(days=1, hours=1, minutes=30),
        status="SCHEDULED"
    )

    appt2 = Appointment(
        doctor_id=doctor2.id,
        patient_id=patient2.id,
        start_time=now + timedelta(days=2, hours=2),
        end_time=now + timedelta(days=2, hours=2, minutes=30),
        status="SCHEDULED"
    )

    db.add_all([appt1, appt2])
    db.commit()

    print("SEED COMPLETED SUCCESSFULLY")


if __name__ == "__main__":
    seed()