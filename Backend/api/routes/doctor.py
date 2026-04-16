from fastapi import APIRouter, Depends, HTTPException
from api.deps import require_roles
from api.routes.appointments import appointments
from schemas.appointment import (
    AppointmentStatusUpdate,
    AppointmentNotes,
    AppointmentResponse
)
from models.user import users
from datetime import datetime, timedelta

router = APIRouter()


#Helper: get current doctor ID
def get_current_doctor_id(user):
    email = user.get("sub")

    doctor = next((u for u in users if u["email"] == email), None)

    if not doctor:
        raise HTTPException(status_code=404, detail="Doctor not found")

    return doctor["id"]


#Get doctor's own appointments
@router.get("/appointments")
def get_doctor_appointments(user=Depends(require_roles(["doctor"]))):

    doctor_id = get_current_doctor_id(user)

    doctor_appointments = [
        appt for appt in appointments if appt["doctor_id"] == doctor_id
    ]

    return {"appointments": doctor_appointments}


#Update appointment status
@router.patch("/appointments/{appointment_id}/status", response_model=AppointmentResponse)
def update_status(
    appointment_id: int,
    data: AppointmentStatusUpdate,
    user=Depends(require_roles(["doctor"]))
):
    doctor_id = get_current_doctor_id(user)
    new_status = data.status

    allowed = ["Scheduled", "Completed", "Cancelled", "No Show"]

    if new_status not in allowed:
        raise HTTPException(status_code=400, detail="Invalid status")

    for appt in appointments:
        if appt["id"] == appointment_id:

            if appt["doctor_id"] != doctor_id:
                raise HTTPException(status_code=403, detail="Not allowed")

            appt["status"] = new_status
            return appt

    raise HTTPException(status_code=404, detail="Not found")


#Add notes
@router.patch("/appointments/{appointment_id}/notes", response_model=AppointmentResponse)
def add_notes(
    appointment_id: int,
    data: AppointmentNotes,
    user=Depends(require_roles(["doctor"]))
):
    doctor_id = get_current_doctor_id(user)

    for appt in appointments:
        if appt["id"] == appointment_id:

            if appt["doctor_id"] != doctor_id:
                raise HTTPException(status_code=403, detail="Not allowed")

            appt["notes"] = data.notes
            return appt

    raise HTTPException(status_code=404, detail="Not found")


#Doctor calendar
def add_30_min(time_str: str):
    dt = datetime.fromisoformat(time_str)
    return (dt + timedelta(minutes=30)).isoformat()


@router.get("/calendar")
def get_doctor_calendar(
    user=Depends(require_roles(["doctor"]))
):
    doctor_id = get_current_doctor_id(user)

    events = []

    for appt in appointments:
        if appt["doctor_id"] == doctor_id:
            events.append({
                "id": appt["id"],
                "title": appt["patient_name"],
                "start": appt["time"],
                "end": add_30_min(appt["time"]),
            })

    return events