from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from datetime import datetime, timedelta



# Create Calendar Service
def get_calendar_service(token: dict):
    creds = Credentials(token=token["access_token"])
    return build("calendar", "v3", credentials=creds)



# Helper: calculate end time
def calculate_end_time(start_time: str, duration_minutes: int = 30):
    start_dt = datetime.fromisoformat(start_time)
    end_dt = start_dt + timedelta(minutes=duration_minutes)
    return end_dt.isoformat()



# Create Event
def create_event(service, summary, start_time, duration=30):
    end_time = calculate_end_time(start_time, duration)

    event = {
        "summary": summary,
        "description": "Clinic appointment",
        "start": {
            "dateTime": start_time,
            "timeZone": "UTC"
        },
        "end": {
            "dateTime": end_time,
            "timeZone": "UTC"
        },
    }

    created_event = service.events().insert(
        calendarId="primary",
        body=event
    ).execute()

    return created_event["id"]



# Update Event
def update_event(service, event_id, new_start_time, duration=30):
    end_time = calculate_end_time(new_start_time, duration)

    event = service.events().get(
        calendarId="primary",
        eventId=event_id
    ).execute()

    event["start"]["dateTime"] = new_start_time
    event["end"]["dateTime"] = end_time

    updated_event = service.events().update(
        calendarId="primary",
        eventId=event_id,
        body=event
    ).execute()

    return updated_event



# Delete Event
def delete_event(service, event_id):
    service.events().delete(
        calendarId="primary",
        eventId=event_id
    ).execute()