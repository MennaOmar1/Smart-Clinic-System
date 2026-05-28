from sqlalchemy import Boolean, Column, Integer, String, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from core.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    email = Column(String)
    password = Column(String)
    role = Column(String)  # doctor, receptionist, admin
    is_active = Column(Boolean, default=True)

class Doctor(Base):
    __tablename__ = "doctors"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    specialization = Column(String)
    google_token = Column(String, nullable=True)  # Stored as JSON string
    bio = Column(Text, nullable=True)
    phone = Column(String, nullable=True)
    experience = Column(String, nullable=True)
    image_url = Column(String, nullable=True)
    user = relationship("User")


class Patient(Base):
    __tablename__ = "patients"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    phone = Column(String, unique=True)
    email = Column(String)


class Appointment(Base):
    __tablename__ = "appointments"

    id = Column(Integer, primary_key=True, index=True)
    doctor_id = Column(Integer, ForeignKey("doctors.id"))
    patient_id = Column(Integer, ForeignKey("patients.id"))

    start_time = Column(DateTime)
    end_time = Column(DateTime)

    status = Column(String)
    notes = Column(String)
    google_event_id = Column(String, nullable=True)
    reminder_sent = Column(Boolean, default=False)
    reminder_time = Column(DateTime, nullable=True)

    doctor = relationship("Doctor")
    patient = relationship("Patient")

class WorkingHours(Base):
    __tablename__ = "working_hours"

    id = Column(Integer, primary_key=True, index=True)
    doctor_id = Column(Integer, ForeignKey("doctors.id"))

    day_of_week = Column(Integer)  # 0=Monday
    start_time = Column(String)    # "09:00"
    end_time = Column(String)      # "17:00"