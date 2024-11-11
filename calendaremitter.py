import datetime
from typing import Dict
from scraper import Scraper
from googlecalendar import GoogleCalendarClient

class CalendarEmitter():
    """Emits calendar time blocks to Google Calendar"""

    def __init__(self, google_calendar_client: GoogleCalendarClient):
        """Constructor for CalendarEmitter"""
        self.google_calendar_client = google_calendar_client

    def emit_calendar_tuples(self,
                             calendar_id: str,
                             calendar_tuples: list[tuple[datetime, datetime]]) -> list[Dict]:
        """Creates Google Calendar events for the given time blocks in the given calendar.

        Args:
            calendar_id (str): The ID of the Google Calendar to interact with.
            calendar_tuples (list[tuple]): List of tuples representing time blocks of open field time

        Returns:
            list[Dict]: The list of created Google Calendar events

        Raises:
            HttpError: If an error occurs with the Google Calendar API request
            ValueError: If a time block is invalid e.g. end time before start time
        """
        created_events = []
        for start_datetime, end_datetime in calendar_tuples:
            if start_datetime > end_datetime:
                raise ValueError(f'Invalid calendar time block: {start_datetime} is after {end_datetime}')
            event = {
                'summary': 'Open Field',
                'location': '555 E 90th St, New York, NY 10128',
                'description': 'Field is open to the public',
                'start': {
                    'dateTime': start_datetime.isoformat(),
                    'timeZone': 'America/New_York',
                },
                'end': {
                    'dateTime': end_datetime.isoformat(),
                    'timeZone': 'America/New_York',
                },
            }
            response = self.google_calendar_client.create_event(calendar_id, event)
            created_events.append(response)
        return created_events

    def clear_calendar(self, calendar_id: str) -> None:
        """Clears all events from the given Google Calendar.

        Raises:
            HttpError: If an error occurs with the Google Calendar API request
        """
        self.google_calendar_client.clear_calendar(calendar_id)

if __name__ == "__main__":
    main()
