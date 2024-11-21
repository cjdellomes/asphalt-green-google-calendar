# Asphalt Green Google Calendar

Scrapes the Asphalt Green open field hours and puts them in a Google Calendar.

## Context

Asphalt Green is a nonprofit organization that provides high-quality sports, swim, and fitness instruction and programs to New York City children and adults.
Their campus in the Upper East Side neighborhood of New York City includes a full size football pitch (soccer field).
The field is booked most of the time for organized events, but is free for public use for a few hours most days.
[The Asphalt Green website posts these free hours on their website in the form of a calendar for the current month](https://www.asphaltgreen.org/ues/schedules/field-schedule).
This project scrapes that website and enters the time blocks in a Google Calendar I can view.

## Deployment

The container is hosted in AWS Elastic Container Registry and deployed to AWS Lambda, scheduled to run every day via AWS EventBridge. New commits trigger a CircleCI test run
followed by a new container build and deploy.

## Local Running and Development

Assuming pip is installed, install required packages via `pip install -r requirements.txt`. Run tests via `pytest` at the topmost level of the project directory.
AWS CLI needs to be installed and AWS account credentials need to be set via `aws configure`.
