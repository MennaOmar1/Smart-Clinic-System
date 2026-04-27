from dotenv import load_dotenv
load_dotenv()
from fastapi import FastAPI
from starlette.middleware.sessions import SessionMiddleware
from api.routes import auth, google_auth, admin, appointments, protected, doctor, auth_refresh, chatbot
from core.database import Base, engine
from models import db_models  
from core.scheduler import send_reminders
from apscheduler.schedulers.background import BackgroundScheduler
import os

app = FastAPI()

app.add_middleware(
    SessionMiddleware,
    secret_key="supersecretkey123456"
)

#create tables
Base.metadata.create_all(bind=engine)

# routers
app.include_router(auth.router, prefix="/auth", tags=["Auth"])
app.include_router(google_auth.router, prefix="/auth", tags=["Google Auth"])
app.include_router(appointments.router, prefix="/appointments", tags=["Appointments"])
app.include_router(admin.router, prefix="/admin", tags=["Admin"])
app.include_router(protected.router)
app.include_router(doctor.router, prefix="/doctor")
app.include_router(auth_refresh.router)
app.include_router(chatbot.router, prefix="/chatbot")

@app.get("/")
def home():
    return {"message": "API running"}

scheduler = BackgroundScheduler()
scheduler.add_job(send_reminders, "interval", minutes=5)
scheduler.start()

API_KEY = os.getenv("GEMINI_API_KEY")
print("KEY:", os.getenv("GEMINI_API_KEY"))