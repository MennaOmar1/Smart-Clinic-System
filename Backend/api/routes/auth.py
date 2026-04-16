from fastapi import APIRouter, HTTPException
from schemas.auth import LoginRequest
from models.user import users
from core.security import verify_password, create_access_token

router = APIRouter()

@router.post("/login")
def login(data: LoginRequest):

    for user in users:
        if user["email"] == data.email and verify_password(data.password, user["password"]):
            
            token = create_access_token({
                "sub": user["email"],
                "role": user["role"]
            })

            return {
                "access_token": token,
                "token_type": "bearer"
            }

    raise HTTPException(status_code=401, detail="Invalid credentials")