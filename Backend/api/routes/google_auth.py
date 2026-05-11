import logging
import os
from fastapi import APIRouter, Request, HTTPException, Depends
from authlib.integrations.base_client.errors import OAuthError
from core.oauth import oauth
from core.security import create_access_token
from sqlalchemy.orm import Session
from core.database import get_db
from models.db_models import User

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/google", tags=["Google Auth"])


@router.get("/login")
async def login(request: Request):
    redirect_uri = os.getenv("GOOGLE_CALLBACK_URL", "http://127.0.0.1:8000/auth/google/callback")
    return await oauth.google.authorize_redirect(request, redirect_uri, access_type="offline", prompt="consent")


@router.get("/callback")
async def auth_callback(request: Request, db: Session = Depends(get_db)):
    try:
        token = await oauth.google.authorize_access_token(request)
    except OAuthError as err:
        error_code = getattr(err, 'error', 'oauth_error')
        error_description = getattr(err, 'description', str(err))
        error_uri = getattr(err, 'error_uri', None)
        logger.error(
            "Google OAuth callback failed: %s %s %s",
            error_code,
            error_description,
            error_uri
        )
        detail = f"Google OAuth error: {error_code} - {error_description}"
        if error_uri:
            detail += f" (see {error_uri})"
        raise HTTPException(status_code=400, detail=detail)
    except Exception as err:
        logger.exception("Unexpected error in Google OAuth callback")
        raise HTTPException(status_code=500, detail="Unexpected Google OAuth callback error")

    user_info = token.get("userinfo")

    if not user_info:
        raise HTTPException(400, "Google auth failed")

    email = user_info["email"]

    user = db.query(User).filter(User.email == email).first()

    # 🔥 FIX: default role = receptionist BUT controlled
    if not user:
        user = User(
            email=email,
            name=user_info.get("name"),
            role="receptionist",  # later we control this via admin
            is_active=True
        )
        db.add(user)
        db.commit()
        db.refresh(user)

    import json
    from models.db_models import Doctor
    if user.role == "doctor":
        doctor = db.query(Doctor).filter(Doctor.user_id == user.id).first()
        if doctor:
            doctor.google_token = json.dumps(token)
            db.commit()

    access_token = create_access_token({
        "sub": str(user.id),
        "role": user.role,
        "email": user.email
    })

    return {
        "access_token": access_token,
        "role": user.role
    }