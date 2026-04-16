from fastapi import APIRouter, Request, HTTPException
from core.oauth import oauth
from core.security import create_access_token, create_refresh_token
from models.user import users

router = APIRouter(prefix="/google")


# LOGIN
@router.get("/login")
async def login(request: Request):
    redirect_uri = "http://127.0.0.1:8000/auth/google/callback"
    return await oauth.google.authorize_redirect(request, redirect_uri)


# CALLBACK
@router.get("/callback")
async def auth_callback(request: Request):
    token = await oauth.google.authorize_access_token(request)
    user_info = token.get("userinfo")

    if not user_info:
        raise HTTPException(status_code=400, detail="Google auth failed")

    email = user_info["email"]

    # Check if user exists
    user = next((u for u in users if u["email"] == email), None)

    if not user:
        user = {
            "id": len(users) + 1,
            "email": email,
            "role": "receptionist",  # default role
            "is_active": True,
            "google_token": token
        }
        users.append(user)
    else:
        user["google_token"] = token

    #Create tokens
    payload = {
        "sub": email,
        "role": user["role"]
    }

    access_token = create_access_token(payload)
    refresh_token = create_refresh_token(payload)

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "role": user["role"],
        "email": email
    }