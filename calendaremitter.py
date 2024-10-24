import datetime
import os
from typing import Any, Dict
from scraper import Scraper
from googlecalendar import GoogleCalendarClient

class CalendarEmitter():
    """Emits calendar time blocks to the Asphalt Green Google Calendar"""

    def __init__(self, google_calendar_client=None):
        """Constructor for CalendarEmitter

        Raises:
            RuntimeError: If the ASPHALT_GREEN_CALENDAR_ID environment variable is not set
        """
        self.google_calendar_client = google_calendar_client
        if not google_calendar_client:
            self.google_calendar_client = self._get_google_calendar_client()

    def emit_calendar_tuples(self, calendar_tuples: list[tuple[datetime, datetime]]) -> list[Dict]:
        """Creates the given time blocks in Google Calendar.

        Args:
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
            response = self.google_calendar_client.create_event(event)
            created_events.append(response)
        return created_events

    def clear_calendar(self) -> None:
        """Clears all events from the Google Calendar

        Raises:
            HttpError: If an error occurs with the Google Calendar API request
            ValueError: If a time block is invalid e.g. end time before start time
        """
        self.google_calendar_client.clear_calendar()

    def _get_google_calendar_client(self) -> Any:
        asphalt_green_calendar_id = os.getenv('ASPHALT_GREEN_CALENDAR_ID')
        if not asphalt_green_calendar_id:
            raise RuntimeError('ASPHALT_GREEN_CALENDAR_ID environment variable is not set')
        return GoogleCalendarClient(asphalt_green_calendar_id)

def main():
    scraper = Scraper()
    calendar_emitter = CalendarEmitter()

    calendar_emitter.clear_calendar()
    calendar_emitter.emit_calendar_tuples(scraper.get_field_hours())

if __name__ == "__main__":
    main()
