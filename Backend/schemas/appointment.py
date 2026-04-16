from pydantic import BaseModel

# Create appointment
class AppointmentCreate(BaseModel):
    doctor_id: int
    patient_name: str
    time: str
    reason: str | None = ""

# Reschedule
class AppointmentReschedule(BaseModel):
    time: str

# Doctor
class AppointmentStatusUpdate(BaseModel):
    status: str

# Add notes
class AppointmentNotes(BaseModel):
    notes: str

# Response model
class AppointmentResponse(BaseModel):
    id: int
    doctor_id: int
    patient_name: str
    time: str
    status: str
    reason: str
    notes: str


class AdminUpdateAppointment(BaseModel):
    time: str | None = None
    status: str | None = None
    notes: str | None = None