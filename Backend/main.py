from dotenv import load_dotenv
load_dotenv()

import os
from fastapi import FastAPI
from starlette.middleware.sessions import SessionMiddleware

from api.routes import (
    auth, google_auth, admin, appointments,
    protected, doctor, auth_refresh, chatbot
)

from core.database import Base, engine
from core.scheduler import send_reminders
from apscheduler.schedulers.background import BackgroundScheduler

# (اختياري - لتفادي crash لو DB مش شغال)
import logging

app = FastAPI()

# Middleware
app.add_middleware(
    SessionMiddleware,
    secret_key="supersecretkey123456"
)

# =========================
# DATABASE INIT (SAFE)
# =========================
@app.on_event("startup")
def startup_db():
    try:
        Base.metadata.create_all(bind=engine)
        print("✅ Database connected & tables created")
    except Exception as e:
        print("❌ Database connection failed:", e)

# =========================
# ROUTERS
# =========================
app.include_router(auth.router, prefix="/auth", tags=["Auth"])
app.include_router(google_auth.router, prefix="/auth", tags=["Google Auth"])
app.include_router(appointments.router, prefix="/appointments", tags=["Appointments"])
app.include_router(admin.router, prefix="/admin", tags=["Admin"])
app.include_router(protected.router)
app.include_router(doctor.router, prefix="/doctor")
app.include_router(auth_refresh.router)
app.include_router(chatbot.router, prefix="/chatbot")

# =========================
# HOME
# =========================
@app.get("/")
def home():
    return {"message": "API running"}

# =========================
# SCHEDULER (SAFE START)
# =========================
scheduler = BackgroundScheduler()

@app.on_event("startup")
def start_scheduler():
    try:
        scheduler.add_job(send_reminders, "interval", minutes=5)
        scheduler.start()
        print("✅ Scheduler started")
    except Exception as e:
        print("❌ Scheduler failed:", e)

# =========================
# ENV VARS
# =========================
API_KEY = os.getenv("GEMINI_API_KEY")

if os.getenv("ENV") == "dev":
    print("Gemini key loaded (dev mode)")