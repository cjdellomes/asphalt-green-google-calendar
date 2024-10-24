import backoff
import requests
from bs4 import BeautifulSoup
from datetime import datetime
from zoneinfo import ZoneInfo

ASPHALT_GREEN_URL = 'https://www.asphaltgreen.org/ues/schedules/field-schedule?show=1'
SCHEDULE_TABLE_DIV_CLASS = 'schedule-zoom'

class Scraper():
    """Scrapes the Asphalt Green field hours website."""

    @backoff.on_exception(backoff.expo,
                          requests.exceptions.Timeout,
                          max_tries=3)
    def get_html(self) -> str:
        """Return the full asphalt green field hours page HTML.

        Returns:
            str: The full HTML string for the asphalt green field hours page

        Raises:
            HTTPError: If the HTTP call to the ashalt green field hours page fails
        """

        response = requests.get(ASPHALT_GREEN_URL, timeout=10)
        response.raise_for_status()
        return response.text

    @backoff.on_exception(backoff.expo,
                          requests.exceptions.Timeout,
                          max_tries=3)
    def get_field_hours(self) -> list[tuple[datetime, datetime]]:
        """Return the open field time blocks from the asphalt green field hours page.

        Returns:
            list[tuple[datetime,datetime]]: List of tuples representing time blocks of open field time

        Raises:
            HTTPError: If the HTTP call to the ashalt green field hours page fails
            RuntimeError: If the schedule table cannot be found in the Asphalt Green website HTML
        """

        html = self.get_html()
        soup = BeautifulSoup(html, 'lxml')

        schedule_table_div_content = soup.find('div', class_=SCHEDULE_TABLE_DIV_CLASS)
        if not schedule_table_div_content:
            raise RuntimeError('failed to find schedule table div')
        table = schedule_table_div_content.find('table')

        calendar_entries = []

        for row in table.find_all('tr')[1:]:  # skip the header row
            columns = row.find_all('td')
            row_data = [col.get_text(' ', strip=True) for col in columns]
            calendar_entries.append(row_data)

        # flatten list of lists down into a single list and remove empty strings
        calendar_entries = [item for sublist in calendar_entries for item in sublist if item]

        calendar_tuples = self._format_calendar_entries(calendar_entries)
        return calendar_tuples

    def _format_calendar_entries(self, calendar_entries) -> list[tuple[datetime, datetime]]:
        calendar_tuples = []

        for entry in calendar_entries:
            if 'No Public Field Hours' in entry:
                continue
            tokens = entry.split()

            # remove the field size descriptions so we are just left with datetime info
            tokens = [token for token in tokens if '(' not in token and ')' not in token]

            month = tokens[0]
            day = tokens[1]

            for time_range in tokens[2:]:
                start_time, end_time = time_range.split('-')

                # Hour only and Hour:Minute formats
                formats = ['%B %d %I%p %Y', '%B %d %I:%M%p %Y']

                start_datetime_str = f'{month} {day} {start_time} {datetime.now().year}'
                start_iso = None
                for fmt in formats:
                    try:
                        start_iso = datetime.strptime(start_datetime_str, fmt)
                        start_iso = start_iso.replace(tzinfo=ZoneInfo('America/New_York'))
                    except ValueError:
                        pass

                end_datetime_str = f'{month} {day} {end_time} {datetime.now().year}'
                end_iso = None
                for fmt in formats:
                    try:
                        end_iso = datetime.strptime(end_datetime_str, fmt)
                        end_iso = end_iso.replace(tzinfo=ZoneInfo('America/New_York'))
                    except ValueError:
                        pass
                if start_iso and end_iso:
                    calendar_tuples.append((start_iso, end_iso))

        return calendar_tuples
