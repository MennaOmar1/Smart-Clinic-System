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

            doctor_name = appointment.doctor.user.name
            patient_name = appointment.patient.name

            event_id = create_event(
                service=service,
                summary=f"Appointment - Dr {doctor_name} with {patient_name}",
                start_time=appointment.start_time.isoformat(),
                end_time=appointment.end_time.isoformat(),
                description=f"""
Patient: {patient_name}
Doctor: {doctor_name}
Status: {appointment.status}
""",
                attendee_email=appointment.patient.email
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

            delete_event(
                service,
                appointment.google_event_id
            )

        except Exception as e:
            print("Google delete failed:", e)