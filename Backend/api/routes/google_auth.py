from fastapi import APIRouter, Request, HTTPException, Depends
from core.oauth import oauth
from core.security import create_access_token
from sqlalchemy.orm import Session
from core.database import get_db
from models.db_models import User

router = APIRouter(prefix="/google", tags=["Google Auth"])


@router.get("/login")
async def login(request: Request):
    redirect_uri = "http://127.0.0.1:8000/auth/google/callback"
    return await oauth.google.authorize_redirect(request, redirect_uri)


@router.get("/callback")
async def auth_callback(request: Request, db: Session = Depends(get_db)):

    token = await oauth.google.authorize_access_token(request)
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

    access_token = create_access_token({
        "sub": str(user.id),
        "role": user.role,
        "email": user.email
    })

    return {
        "access_token": access_token,
        "role": user.role
    }