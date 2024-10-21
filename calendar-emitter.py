from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
import datetime
import os

SCOPES = ['https://www.googleapis.com/auth/calendar']

creds = None
flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
creds = flow.run_local_server(port=0)

service = build('calendar', 'v3', credentials=creds)

event = {
    'summary': 'Open Field',
    'location': '555 E 90th St, New York, NY 10128',
    'description': 'Field is open to the public',
    'start': {
        'dateTime': '2024-10-21T09:00:00-07:00',
        'timeZone': 'America/New_York',
    },
    'end': {
        'dateTime': '2024-10-21T17:00:00-07:00',
        'timeZone': 'America/New_York',
    },
}

asphalt_green_calendar_id = os.getenv('ASPHALT_GREEN_CALENDAR_ID')

# Call the Calendar API to create the event
event_result = service.events().insert(calendarId=asphalt_green_calendar_id, body=event).execute()
print(f"Event created: {event_result.get('htmlLink')}")
