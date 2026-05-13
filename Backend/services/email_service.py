import os
import json
import base64

from email.mime.text import MIMEText

from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build


def send_email(
    doctor,
    to_email: str,
    subject: str,
    body: str
):

    if not doctor.google_token:
        raise ValueError("Doctor has no Google token")

    google_token = json.loads(doctor.google_token)

    credentials = Credentials(
        token=google_token["access_token"],
        refresh_token=google_token["refresh_token"],
        token_uri="https://oauth2.googleapis.com/token",
        client_id=os.getenv("GOOGLE_CLIENT_ID"),
        client_secret=os.getenv("GOOGLE_CLIENT_SECRET"),
        scopes=[
            "https://www.googleapis.com/auth/gmail.send"
        ]
    )

    service = build(
        "gmail",
        "v1",
        credentials=credentials
    )

    message = MIMEText(body)

    message["to"] = to_email
    message["subject"] = subject

    raw_message = base64.urlsafe_b64encode(
        message.as_bytes()
    ).decode()

    send_message = (
        service.users()
        .messages()
        .send(
            userId="me",
            body={"raw": raw_message}
        )
        .execute()
    )

    return send_message