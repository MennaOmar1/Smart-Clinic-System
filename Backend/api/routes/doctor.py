from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from core.database import get_db
from services.appointment_service import AppointmentService
from schemas.appointment import (
    AppointmentStatusUpdate,
    AppointmentNotes,
    AppointmentResponse
)
from api.deps import require_roles
from models.db_models import Appointment, Doctor

router = APIRouter(tags=["Doctor"])


def get_doctor_id(user):
    return int(user.get("id") or user.get("sub"))


@router.get("/appointments", response_model=list[AppointmentResponse])
def get_my_appointments(
    db: Session = Depends(get_db),
    user=Depends(require_roles(["doctor"]))
):
    user_id = int(user.get("sub"))

    doctor = db.query(Doctor).filter(
        Doctor.user_id == user_id
    ).first()

    if not doctor:
        raise HTTPException(404, "Doctor not found")

    appointments = db.query(Appointment).filter(
        Appointment.doctor_id == doctor.id
    ).all()

    return appointments


@router.patch("/appointments/{appointment_id}/status", response_model=AppointmentResponse)
def update_status(
    appointment_id: int,
    data: AppointmentStatusUpdate,
    db: Session = Depends(get_db),
    user=Depends(require_roles(["doctor"]))
):
    doctor_id = get_doctor_id(user)

    try:
        return AppointmentService.update_status(
            db,
            appointment_id,
            data.status
        )
    except Exception as e:
        raise HTTPException(400, str(e))


@router.patch("/appointments/{appointment_id}/notes", response_model=AppointmentResponse)
def add_notes(
    appointment_id: int,
    data: AppointmentNotes,
    db: Session = Depends(get_db),
    user=Depends(require_roles(["doctor"]))
):
    doctor_id = get_doctor_id(user)

    try:
        return AppointmentService.add_notes(
            db,
            appointment_id,
            data.notes
        )
    except Exception as e:
        raise HTTPException(400, str(e))