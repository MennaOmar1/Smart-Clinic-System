from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from core.database import get_db
from core.security import hash_password
from models.db_models import User
from schemas.user import UserCreate, UserResponse
from services.appointment_service import AppointmentService
from schemas.appointment import AdminUpdateAppointment, AppointmentResponse
from api.deps import require_roles
from datetime import timedelta
from services.calendar_sync_service import CalendarSyncService
from services.email_service import send_email

router = APIRouter(tags=["Admin"])


@router.get("/appointments", response_model=list[AppointmentResponse])
def get_all_appointments(
    db: Session = Depends(get_db),
    user=Depends(require_roles(["admin"]))
):
    return AppointmentService.get_all(db)


@router.get("/appointments/filter")
def filter_appointments(
    doctor_id: int | None = None,
    status: str | None = None,
    db: Session = Depends(get_db),
    user=Depends(require_roles(["admin"]))
):
    appointments = AppointmentService.get_all(db)

    if doctor_id:
        appointments = [a for a in appointments if a.doctor_id == doctor_id]

    if status:
        appointments = [a for a in appointments if a.status == status]

    return {"appointments": appointments}


@router.patch("/appointments/{appointment_id}", response_model=AppointmentResponse)
def update_appointment(
    appointment_id: int,
    data: AdminUpdateAppointment,
    request: Request,
    db: Session = Depends(get_db),
    user=Depends(require_roles(["admin"]))
):
    appt = AppointmentService.get_by_id(db, appointment_id)

    if not appt:
        raise HTTPException(404, "Not found")

    google_token = request.session.get("google_token")

    # ================= UPDATE STATUS =================
    if data.status:
        appt.status = data.status

    # ================= UPDATE NOTES =================
    if data.notes:
        appt.notes = data.notes

    # ================= RESCHEDULE =================
    if data.time:
        if not AppointmentService.is_available(db, appt.doctor_id, data.time):
            raise HTTPException(400, "Time slot not available")

        appt.start_time = data.time
        appt.end_time = data.time + timedelta(minutes=30)

        # Google sync
        CalendarSyncService.update(appt, data.time, google_token)

    db.commit()
    db.refresh(appt)

    return appt


@router.delete("/appointments/{appointment_id}")
def delete_appointment(
    appointment_id: int,
    request: Request,
    db: Session = Depends(get_db),
    user=Depends(require_roles(["admin"]))
):
    appt = AppointmentService.get_by_id(db, appointment_id)

    if not appt:
        raise HTTPException(404, "Not found")

    google_token = request.session.get("google_token")

    # Google delete
    CalendarSyncService.delete(appt, google_token)

    db.delete(appt)
    db.commit()

    return {"message": "Deleted successfully"}


@router.post("/users", response_model=UserResponse)
def create_user(
    data: UserCreate,
    db: Session = Depends(get_db),
    user=Depends(require_roles(["admin"]))
):
    existing = db.query(User).filter(User.email == data.email).first()

    if existing:
        raise HTTPException(400, "User already exists")

    new_user = User(
        email=data.email,
        role=data.role,
        name=data.email.split("@")[0],
        password=hash_password("123456")  # default password
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return new_user


# ================= GET USERS =================
@router.get("/users", response_model=list[UserResponse])
def get_users(
    db: Session = Depends(get_db),
    user=Depends(require_roles(["admin"]))
):
    return db.query(User).all()


# ================= DELETE USER =================
@router.delete("/users/{user_id}")
def delete_user(
    user_id: int,
    db: Session = Depends(get_db),
    user=Depends(require_roles(["admin"]))
):
    u = db.query(User).filter(User.id == user_id).first()

    if not u:
        raise HTTPException(404, "User not found")

    db.delete(u)
    db.commit()

    return {"message": "User deleted"}











@router.post("/test-email")
def test_email():
    send_email(
        to_email="omarmenna041@gmail.com",
        subject="Test Email",
        body="Hello 👋 this is a test from FastAPI"
    )
    return {"message": "Email sent (check inbox)"}

