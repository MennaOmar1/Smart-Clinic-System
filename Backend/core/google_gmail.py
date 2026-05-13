from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from email.mime.text import MIMEText
import base64


def send_gmail_message(token_data, to_email, subject, body, from_email=None):

    creds = Credentials(
        token=token_data["access_token"],
        refresh_token=token_data.get("refresh_token"),
        token_uri="https://oauth2.googleapis.com/token",
        client_id="YOUR_GOOGLE_CLIENT_ID",
        client_secret="YOUR_GOOGLE_CLIENT_SECRET"
    )

    service = build("gmail", "v1", credentials=creds)

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