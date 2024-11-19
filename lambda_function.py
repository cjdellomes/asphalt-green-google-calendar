import json
from google.oauth2.service_account import Credentials
from source.secretsmanager import SecretsManagerClient
from source.googlecalendar import GoogleCalendarClient
from source.calendaremitter import CalendarEmitter
from source.scraper import Scraper

def handler(event, context):
    secrets_manager_client = SecretsManagerClient('us-east-1')
    service_account_info = json.loads(secrets_manager_client.get_secret('asphalt-green-google-calendar'))
    credentials = Credentials.from_service_account_info(service_account_info,
                                                        scopes=['https://www.googleapis.com/auth/calendar'])

    calendar_emitter = CalendarEmitter(GoogleCalendarClient(credentials))
    calendar_id = secrets_manager_client.get_secret('asphalt-green-google-calendar-id')

    calendar_emitter.clear_calendar(calendar_id)
    created_events = calendar_emitter.emit_calendar_tuples(calendar_id, Scraper().get_field_hours())

    return {
        'statusCode': 200,
        'body': created_events
    }

if __name__ == '__main__':
    handler(None, None)
