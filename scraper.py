from bs4 import BeautifulSoup
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

