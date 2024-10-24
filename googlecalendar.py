import backoff
from typing import Any, Dict
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from google.auth.transport.requests import Request

CREDENTIALS_PATH = 'credentials.json'
TOKEN_PATH = 'token.json'
CALENDAR_SCOPE = 'https://www.googleapis.com/auth/calendar'

def _is_retryable_http_error(exception):
    if not isinstance(exception, HttpError):
        return False
    return exception.resp.status in [429, 500, 502, 503, 504]

class GoogleCalendarClient:
    """Client for interacting with the Google Calendar API."""

    def __init__(self, calendar_id: str):
        """Constructor for the GoogleCalendarClient"""
        self.scopes = [CALENDAR_SCOPE]
        self.service = self._authenticate_google_calendar()
        self.calendar_id = calendar_id

    @backoff.on_exception(backoff.expo,
                          HttpError,
                          max_tries=5,
                          giveup=lambda e: not _is_retryable_http_error(e))
    def create_event(self, event: Dict) -> Dict:
        """Create an event on the specified calendar.

        Args:
            event (dict): The event to create. Must follow the structure expected by the Google Calendar API.

        Returns:
            Dict: The created event details from Google Calendar API

        Raises:
            HttpError: If an error occurs with the Google Calendar API request.
        """
        created_event = self.service.events().insert(calendarId=self.calendar_id, body=event).execute()
        return created_event

    @backoff.on_exception(backoff.expo,
                          HttpError,
                          max_tries=5,
                          giveup=lambda e: not _is_retryable_http_error(e))
    def clear_calendar(self) -> None:
        """Clear all events from the specified calendar.

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
            events = self.service.events().list(calendarId=self.calendar_id, pageToken=page_token).execute()
            for event in events.get('items', []):
                self.service.events().delete(calendarId=self.calendar_id, eventId=event['id']).execute()
            page_token = events.get('nextPageToken')
            if not page_token:
                break

    def _authenticate_google_calendar(self) -> Any:
        creds = None

        # The file token.json stores the user's access and refresh tokens, and is
        # created automatically when the authorization flow completes for the first time.
        try:
            creds = Credentials.from_authorized_user_file(TOKEN_PATH, self.scopes)
        except OSError:
            pass  # If token.json does not exist or is invalid, we will need to log in again.

        # If there are no (valid) credentials available, let the user log in.
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(CREDENTIALS_PATH, self.scopes)
                creds = flow.run_local_server(port=0)

            # Save the credentials for the next run
            with open(TOKEN_PATH, 'w') as token:
                token.write(creds.to_json())

        return build('calendar', 'v3', credentials=creds)

