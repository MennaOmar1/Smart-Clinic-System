import os
from base64 import urlsafe_b64encode
from email.mime.text import MIMEText
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build


def build_google_credentials(token: dict):
    if not token:
        raise ValueError("Google credentials token is required")

    return Credentials(
        token=token.get("access_token"),
        refresh_token=token.get("refresh_token"),
        token_uri=token.get("token_uri", "https://oauth2.googleapis.com/token"),
        client_id=token.get("client_id", os.getenv("GOOGLE_CLIENT_ID")),
        client_secret=token.get("client_secret", os.getenv("GOOGLE_CLIENT_SECRET"))
    )


def get_gmail_service(token: dict):
    creds = build_google_credentials(token)
    return build("gmail", "v1", credentials=creds)


def send_gmail_message(token: dict, to_email: str, subject: str, body: str, from_email: str | None = None):
    service = get_gmail_service(token)
    from_address = from_email or token.get("email") or os.getenv("EMAIL_ADDRESS")

    message = MIMEText(body, "plain")
    message["To"] = to_email
    message["From"] = from_address
    message["Subject"] = subject

    raw = urlsafe_b64encode(message.as_bytes()).decode()
    gmail_message = {"raw": raw}

    return service.users().messages().send(userId="me", body=gmail_message).execute()
