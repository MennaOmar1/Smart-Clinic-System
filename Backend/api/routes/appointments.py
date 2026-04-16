from fastapi import APIRouter, Depends, HTTPException, Request
from api.deps import require_roles
from schemas.appointment import (
    AppointmentCreate,
    AppointmentResponse,
    AppointmentReschedule
)
from core.google_calendar import (
    get_calendar_service,
    create_event,
    update_event,
    delete_event
)
from datetime import datetime, timedelta

router = APIRouter()

appointments = []
appointment_id_counter = 1



# Create Appointment
@router.post("/", response_model=AppointmentResponse)
def create_appointment(
    request: Request,
    data: AppointmentCreate,
    user=Depends(require_roles(["receptionist", "admin"]))
):
    global appointment_id_counter

    #GET REAL GOOGLE TOKEN
    google_token = request.session.get("google_token")
    if not google_token:
        raise HTTPException(status_code=401, detail="Google not connected")

    # Prevent double booking
    for appt in appointments:
        if appt["doctor_id"] == data.doctor_id and appt["time"] == data.time:
            raise HTTPException(status_code=400, detail="Time already booked")

    # Google Calendar
    try:
        service = get_calendar_service(google_token)

        event_id = create_event(
            service,
            summary=f"Appointment: {data.patient_name}",
            start_time=data.time
        )

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Google Calendar error: {str(e)}"
        )

    new_appointment = {
        "id": appointment_id_counter,
        "doctor_id": data.doctor_id,
        "patient_name": data.patient_name,
        "time": data.time,
        "status": "Scheduled",
        "reason": data.reason or "",
        "notes": "",
        "created_by": user.get("sub"),
        "google_event_id": event_id
    }

    appointments.append(new_appointment)
    appointment_id_counter += 1

    return new_appointment



# Cancel Appointment
@router.patch("/{appointment_id}/cancel", response_model=AppointmentResponse)
def cancel_appointment(
    appointment_id: int,
    request: Request,
    user=Depends(require_roles(["receptionist", "admin"]))
):
    google_token = request.session.get("google_token")
    if not google_token:
        raise HTTPException(status_code=401, detail="Google not connected")

    service = get_calendar_service(google_token)

    for appt in appointments:
        if appt["id"] == appointment_id:

            try:
                if appt.get("google_event_id"):
                    delete_event(service, appt["google_event_id"])
            except:
                pass

            appt["status"] = "Cancelled"
            return appt

    raise HTTPException(status_code=404, detail="Not found")



# Reschedule Appointment
@router.patch("/{appointment_id}/reschedule", response_model=AppointmentResponse)
def reschedule_appointment(
    appointment_id: int,
    data: AppointmentReschedule,
    request: Request,
    user=Depends(require_roles(["receptionist", "admin"]))
):
    google_token = request.session.get("google_token")
    if not google_token:
        raise HTTPException(status_code=401, detail="Google not connected")

    service = get_calendar_service(google_token)

    for appt in appointments:
        if appt["id"] == appointment_id:

            # Prevent double booking
            for other in appointments:
                if (
                    other["doctor_id"] == appt["doctor_id"]
                    and other["time"] == data.time
                ):
                    raise HTTPException(status_code=400, detail="Time already booked")

            try:
                if appt.get("google_event_id"):
                    update_event(
                        service,
                        appt["google_event_id"],
                        data.time
                    )
            except Exception as e:
                raise HTTPException(
                    status_code=500,
                    detail=f"Calendar update failed: {str(e)}"
                )

            appt["time"] = data.time
            return appt

    raise HTTPException(status_code=404, detail="Appointment not found")



# Get All Appointments
@router.get("/", response_model=list[AppointmentResponse])
def get_all_appointments(
    user=Depends(require_roles(["admin", "receptionist"]))
):
    return appointments



# Calendar Endpoint
def add_30_min(time_str: str):
    dt = datetime.fromisoformat(time_str)
    return (dt + timedelta(minutes=30)).isoformat()


@router.get("/calendar")
def get_calendar_events(
    user=Depends(require_roles(["admin", "receptionist"]))
):
    events = []

    for appt in appointments:
        events.append({
            "id": appt["id"],
            "title": appt["patient_name"],
            "start": appt["time"],
            "end": add_30_min(appt["time"]),
        })

    return events