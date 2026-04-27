from apscheduler.schedulers.background import BackgroundScheduler
from services.email_service import send_email
from datetime import datetime
from core.database import SessionLocal
from models.db_models import Appointment

scheduler = BackgroundScheduler()
scheduler.start()

def send_reminders():
    db = SessionLocal()

    now = datetime.utcnow()

    appointments = db.query(Appointment).filter(
        Appointment.reminder_time <= now,
        Appointment.reminder_sent == False,
        Appointment.status == "SCHEDULED"
    ).all()

    for appt in appointments:

        send_email.send_email(
            to=appt.patient.email,
            subject="Appointment Reminder",
            body=f"""
Hi {appt.patient.name},

This is a reminder for your appointment at {appt.start_time}.

Thank you,
Clinic Team
"""
        )

        appt.reminder_sent = True

    db.commit()
    db.close()