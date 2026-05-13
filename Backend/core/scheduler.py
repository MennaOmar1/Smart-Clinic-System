import json
from datetime import datetime

from apscheduler.schedulers.background import BackgroundScheduler

from services.email_service import send_email
from core.google_gmail import send_gmail_message

from core.database import SessionLocal
from models.db_models import Appointment


scheduler = BackgroundScheduler()
scheduler.start()


def send_reminders():

    db = SessionLocal()

    try:

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

            email_sent = False

            # =========================
            # GOOGLE GMAIL
            # =========================
            if appt.doctor and appt.doctor.google_token:

                try:

                    token = json.loads(
                        appt.doctor.google_token
                    )

                    send_gmail_message(
                        token,
                        to_email=appt.patient.email,
                        subject=subject,
                        body=body,
                        from_email=getattr(
                            appt.doctor.user,
                            "email",
                            None
                        )
                    )

                    print(
                        f"✅ Gmail reminder sent "
                        f"to {appt.patient.email}"
                    )

                    email_sent = True

                except Exception as e:

                    print(
                        "❌ Gmail reminder failed:",
                        str(e)
                    )

            # =========================
            # SMTP FALLBACK
            # =========================
            if not email_sent:

                try:

                    send_email(
                        appt.patient.email,
                        subject,
                        body
                    )

                    print(
                        f"✅ SMTP reminder sent "
                        f"to {appt.patient.email}"
                    )

                    email_sent = True

                except Exception as e:

                    print(
                        "❌ SMTP reminder failed:",
                        str(e)
                    )

            # =========================
            # MARK AS SENT
            # =========================
            if email_sent:

                appt.reminder_sent = True

        db.commit()

    finally:

        db.close()