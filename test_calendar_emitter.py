import os
import unittest
from datetime import datetime
from unittest.mock import patch, Mock
from zoneinfo import ZoneInfo
from googleapiclient.errors import HttpError
from googlecalendar import GoogleCalendarClient
from calendaremitter import CalendarEmitter

class TestCalendarEmitter(unittest.TestCase):
    """Tests for the Calendar Emitter class."""

    @patch.dict('os.environ', {'ASPHALT_GREEN_CALENDAR_ID': 'fake_calendar_id'})
    def test_environment_variable_for_calendar_id(self):
        """Test that environment variable is correctly retrieved"""
        emitter = CalendarEmitter()
        self.assertEqual(emitter.google_calendar_client.calendar_id, 'fake_calendar_id')

    @patch.dict('os.environ', {}, clear=True)
    def test_runtime_error_when_env_var_missing(self):
        """Test that a RuntimeError is raised when the environment variable is missing."""
        with self.assertRaises(RuntimeError) as context:
            CalendarEmitter()
        self.assertEqual(str(context.exception), "ASPHALT_GREEN_CALENDAR_ID environment variable is not set")

    def test_emit_calendar_tuples(self):
        """Test method for the emit_calendar_tuples function"""
        test_tuples = [
            (
                datetime(2024, 1, 1, 6, 0, tzinfo=ZoneInfo("America/New_York")),
                datetime(2024, 1, 1, 7, 0, tzinfo=ZoneInfo("America/New_York")),
            )
        ]
        test_event = {
            'summary': 'Open Field',
            'location': '555 E 90th St, New York, NY 10128',
            'description': 'Field is open to the public',
            'start': {
                'dateTime': '2024-01-01T06:00-05:00',
                'timeZone': 'America/New_York',
            },
            'end': {
                'dateTime': '2024-01-01T07:00-05:00',
                'timeZone': 'America/New_York',
            },
        }
        expected = [test_event]
        mock_google_calendar_client = Mock()
        mock_google_calendar_client.create_event.return_value = test_event

        emitter = CalendarEmitter(mock_google_calendar_client)
        result = emitter.emit_calendar_tuples(test_tuples)

        self.assertTrue(mock_google_calendar_client.create_event.called)
        self.assertEqual(result, expected)

    def test_emit_calendar_tuples_invalid_time_blocks(self):
        """Test method for the emit_calendar_tuples function assuming invalid calendar time blocks"""
        invalid_calendar_tuples = [
            (
                datetime(2024, 1, 10, 6, 0, tzinfo=ZoneInfo("America/New_York")),
                datetime(2024, 1, 5, 6, 0, tzinfo=ZoneInfo("America/New_York")),
            )
        ]

        emitter = CalendarEmitter()

        with self.assertRaises(ValueError) as context:
            emitter.emit_calendar_tuples(invalid_calendar_tuples)
        self.assertEqual(str(context.exception),
                         'Invalid calendar time block: 2024-01-10 06:00:00-05:00 is after 2024-01-05 06:00:00-05:00')

    def test_emit_calendar_tuples_failed_calendar_api_call(self):
        """Test method for the emit_calendar_tuples function assuming a failed Google Calendar API call"""
        test_tuples = [
            (
                datetime(2024, 1, 1, 6, 0, tzinfo=ZoneInfo("America/New_York")),
                datetime(2024, 1, 1, 7, 0, tzinfo=ZoneInfo("America/New_York")),
            )
        ]
        mock_google_calendar_client = Mock()
        mock_google_calendar_client.create_event.side_effect = HttpError(Mock(status=404), b'Event not created')

        emitter = CalendarEmitter(mock_google_calendar_client)

        self.assertRaises(HttpError, emitter.emit_calendar_tuples, test_tuples)

    def test_clear_calendar(self):
        """Test method for the clear_calendar function"""
        mock_google_calendar_client = Mock()
        mock_google_calendar_client.clear_calendar.return_value = None

        emitter = CalendarEmitter(mock_google_calendar_client)
        emitter.clear_calendar()

        self.assertTrue(mock_google_calendar_client.clear_calendar.called)

    def test_clear_calendar_failed_calendar_api_call(self):
        """Test method for the clear_calendar function assuming a failed Google Calendar API call"""
        mock_google_calendar_client = Mock()
        mock_google_calendar_client.clear_calendar.side_effect = HttpError(Mock(status=404), b'Event not created')

        emitter = CalendarEmitter(mock_google_calendar_client)

        self.assertRaises(HttpError, emitter.clear_calendar)

if __name__ == '__main__':
     unittest.main()
