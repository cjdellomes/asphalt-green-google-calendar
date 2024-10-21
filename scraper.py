from bs4 import BeautifulSoup
from datetime import datetime
import requests

url = 'https://www.asphaltgreen.org/ues/schedules/field-schedule?show=1'
response = requests.get(url)

soup = BeautifulSoup(response.text, 'lxml')

schedule_table_div = 'schedule-zoom'
div_content = soup.find('div', class_=schedule_table_div)
table = div_content.find('table')

data = []

for row in table.find_all('tr')[1:]:  # skip the header row
    columns = row.find_all('td')
    row_data = [col.get_text(' ', strip=True) for col in columns]
    data.append(row_data)

# flatten list of lists down into a single list and remove empty strings
data = [item for sublist in data for item in sublist if item]

for item in data:
    if 'No Public Field Hours' in item:
        continue
    tokens = item.split()
    tokens = [token for token in tokens if '(' not in token and ')' not in token]
    month = tokens[0]
    day = tokens[1]
    for time_range in tokens[2:]:
        start_time, end_time = time_range.split('-')
        formats = ['%B %d %I%p %Y', '%B %d %I:%M%p %Y']  # Hour only and Hour:Minute formats

        start_datetime_str = f'{month} {day} {start_time} {datetime.now().year}'
        start_iso = None
        for fmt in formats:
            try:
                start_iso = datetime.strptime(start_datetime_str, fmt).isoformat() + '-07:00'
            except ValueError:
                pass

        end_datetime_str = f'{month} {day} {end_time} {datetime.now().year}'
        end_iso = None
        for fmt in formats:
            try:
                end_iso = datetime.strptime(end_datetime_str, fmt).isoformat() + '-07:00'
            except ValueError:
                pass
        print(start_iso + ' ' + end_iso)
