import backoff
from typing import Dict
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

def _is_retryable_http_error(exception):
    if not isinstance(exception, HttpError):
        return False
    return exception.resp.status in [429, 500, 502, 503, 504]

class GoogleCalendarClient:
    """Client for interacting with the Google Calendar API."""

    def __init__(self, credentials: Credentials):
        """Constructor for the GoogleCalendarClient"""
        self.service = build('calendar', 'v3', credentials=credentials)

    @backoff.on_exception(backoff.expo,
                          HttpError,
                          max_tries=5,
                          giveup=lambda e: not _is_retryable_http_error(e))
    def create_event(self, calendar_id: str, event: Dict) -> Dict:
        """Create an event on the specified calendar.

        Args:
            calendar_id (str): The ID of the Google Calendar to interact with.
            event (Dict): The event to create. Must follow the structure expected by the Google Calendar API.

        Returns:
            Dict: The created event details from Google Calendar API

        Raises:
            HttpError: If an error occurs with the Google Calendar API request.
        """
        created_event = self.service.events().insert(calendarId=calendar_id, body=event).execute()
        return created_event

    @backoff.on_exception(backoff.expo,
                          HttpError,
                          max_tries=5,
                          giveup=lambda e: not _is_retryable_http_error(e))
    def clear_calendar(self, calendar_id: str) -> None:
        """Clear all events from the specified calendar.

        Args:
            calendar_id (str): The ID of the Google Calendar to interact with.

        Raises:
            HttpError: If an error occurs with the Google Calendar API request.
        """

        # The Google Calendar API has a clear() endpoint for calendars, but it
        # currently only works for primary calendars, not secondary ones.
        # (https://issuetracker.google.com/issues/218397050)
        # As a workaround, this client method uses the events list() endpoint
        # to iterate all existing events in the calendar and delete them one by one.
        page_token = None
        while True:
            events = self.service.events().list(calendarId=calendar_id, pageToken=page_token).execute()
            for event in events.get('items', []):
                self.service.events().delete(calendarId=calendar_id, eventId=event['id']).execute()
            page_token = events.get('nextPageToken')
            if not page_token:
                break
