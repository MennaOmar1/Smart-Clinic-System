import json
from apscheduler.schedulers.background import BackgroundScheduler
from services.email_service import send_email
from core.google_gmail import send_gmail_message
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
        if not appt.patient or not appt.patient.email:
            continue

        subject = "Appointment Reminder"
        body = f"""
Hi {appt.patient.name},

This is a reminder for your appointment at {appt.start_time}.

Thank you,
Clinic Team
"""

        sent_via_gmail = False
        if appt.doctor and appt.doctor.google_token:
            try:
                token = json.loads(appt.doctor.google_token)
                send_gmail_message(
                    token,
                    to_email=appt.patient.email,
                    subject=subject,
                    body=body,
                    from_email=getattr(appt.doctor.user, "email", None)
                )
                sent_via_gmail = True
            except Exception as e:
                print("Gmail reminder failed:", e)

        if not sent_via_gmail:
            send_email(
                to=appt.patient.email,
                subject=subject,
                body=body
            )

        appt.reminder_sent = True

    db.commit()
    db.close()