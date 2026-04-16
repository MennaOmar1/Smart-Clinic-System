from fastapi import APIRouter, Depends, HTTPException
from api.deps import require_roles
from schemas.user import UserCreate, UserResponse, UserUpdateRole
from models.user import users
from api.routes.appointments import appointments   # 🔥 important

router = APIRouter()



#  USER MANAGEMENT

# Create User
@router.post("/create-user", response_model=UserResponse)
def create_user(
    data: UserCreate,
    user=Depends(require_roles(["admin"]))
):
    for u in users:
        if u["email"] == data.email:
            raise HTTPException(status_code=400, detail="Email already exists")

    new_user = {
        "id": len(users) + 1,
        "email": data.email,
        "role": data.role,
        "is_active": True
    }

    users.append(new_user)
    return new_user


# Get all users
@router.get("/users", response_model=list[UserResponse])
def get_users(user=Depends(require_roles(["admin"]))):
    return users


# Delete user
@router.delete("/users/{user_id}")
def delete_user(
    user_id: int,
    user=Depends(require_roles(["admin"]))
):
    for i, u in enumerate(users):
        if u["id"] == user_id:
            users.pop(i)
            return {"message": "User deleted successfully"}

    raise HTTPException(status_code=404, detail="User not found")


# Update role
@router.patch("/users/{user_id}/role", response_model=UserResponse)
def update_role(
    user_id: int,
    data: UserUpdateRole,
    user=Depends(require_roles(["admin"]))
):
    for u in users:
        if u["id"] == user_id:
            u["role"] = data.role
            return u

    raise HTTPException(status_code=404, detail="User not found")


# Activate / Deactivate user
@router.patch("/users/{user_id}/toggle-active", response_model=UserResponse)
def toggle_active(
    user_id: int,
    user=Depends(require_roles(["admin"]))
):
    for u in users:
        if u["id"] == user_id:
            u["is_active"] = not u["is_active"]
            return u

    raise HTTPException(status_code=404, detail="User not found")



#  APPOINTMENT MANAGEMENT

# Get all appointments
@router.get("/appointments")
def get_all_appointments(user=Depends(require_roles(["admin"]))):
    return {"appointments": appointments}


# Filter appointments
@router.get("/appointments/filter")
def filter_appointments(
    doctor_id: int | None = None,
    status: str | None = None,
    user=Depends(require_roles(["admin"]))
):
    results = appointments

    if doctor_id is not None:
        results = [a for a in results if a["doctor_id"] == doctor_id]

    if status is not None:
        results = [a for a in results if a["status"] == status]

    return {"appointments": results}


# Update appointment (admin full control)
@router.patch("/appointments/{appointment_id}")
def update_appointment(
    appointment_id: int,
    data: dict,
    user=Depends(require_roles(["admin"]))
):
    for appt in appointments:
        if appt["id"] == appointment_id:

            if "time" in data:
                appt["time"] = data["time"]

            if "status" in data:
                appt["status"] = data["status"]

            if "notes" in data:
                appt["notes"] = data["notes"]

            return {"appointment": appt}

    raise HTTPException(status_code=404, detail="Appointment not found")


# Delete appointment
@router.delete("/appointments/{appointment_id}")
def delete_appointment(
    appointment_id: int,
    user=Depends(require_roles(["admin"]))
):
    for i, appt in enumerate(appointments):
        if appt["id"] == appointment_id:
            appointments.pop(i)
            return {"message": "Appointment deleted successfully"}

    raise HTTPException(status_code=404, detail="Appointment not found")