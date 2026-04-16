from fastapi import APIRouter, HTTPException
from core.security import verify_token, create_access_token

router = APIRouter(prefix="/auth")


@router.post("/refresh")
def refresh_token(refresh_token: str):
    payload = verify_token(refresh_token)

    if not payload or payload.get("type") != "refresh":
        raise HTTPException(status_code=401, detail="Invalid refresh token")

    new_access_token = create_access_token({
        "sub": payload["sub"],
        "role": payload["role"]
    })

    return {
        "access_token": new_access_token
    }