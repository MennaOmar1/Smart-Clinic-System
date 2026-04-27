from core.google_calendar import (
    get_calendar_service,
    create_event,
    update_event,
    delete_event
)


class CalendarSyncService:

    @staticmethod
    def create(appointment, google_token):

        if not google_token:
            return None

        try:
            service = get_calendar_service(google_token)

            event_id = create_event(
                service,
                summary=f"Appointment - Dr {appointment.doctor_id}",
                start_time=appointment.start_time.isoformat()
            )

            return event_id

        except Exception as e:
            print("Google create failed:", e)
            return None


    @staticmethod
    def update(appointment, new_time, google_token):

        if not google_token or not appointment.google_event_id:
            return

        try:
            service = get_calendar_service(google_token)

            update_event(
                service,
                appointment.google_event_id,
                new_time.isoformat()
            )

        except Exception as e:
            print("Google update failed:", e)


    @staticmethod
    def delete(appointment, google_token):

        if not google_token or not appointment.google_event_id:
            return

        try:
            service = get_calendar_service(google_token)

            delete_event(service, appointment.google_event_id)

        except Exception as e:
            print("Google delete failed:", e)