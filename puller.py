# todo: 
# - convert hours to decimal 
# - keep pulling if event has no description - 

import datetime
import os.path
import re

from zoneinfo import ZoneInfo
from dotenv import load_dotenv
from google.auth.transport.requests import Request  
from google.oauth2.credentials import Credentials  
from google_auth_oauthlib.flow import InstalledAppFlow  
from googleapiclient.discovery import build  
from googleapiclient.errors import HttpError  

load_dotenv()
CALENDAR_ID = os.getenv('CALENDAR_ID')
NEW_YORK = ZoneInfo("America/New_York")
SCOPES = ["https://www.googleapis.com/auth/calendar.events.readonly", "https://www.googleapis.com/auth/calendar.calendarlist.readonly"] 

currentRoute = "13"
currentHoursWorked = 7.5
currentDate = "2025-10-03"
lastPulledEntry = ""
hasGreenCardTime = "false"
specialRoutesList = ["Amazon", "RCA Academy", "Orientation", "Shadow Day", "Driving Skills Course", "Defensive Driving Course"]

class ParsedEventDescription:
    def __init__(self, route, hours):
        self.route = route
        self.hours = hours

def getGreenCardTime(route):
  for specialRoute in specialRoutesList:
    if route == specialRoute:
      return "true"
      break
    else:
      return "false"

def getRouteFromDescription(description):
  if description:
    if "Route" in description:
        routeIndex = description.index("Route")
        route = description[routeIndex+6:routeIndex+8]
        return route
    else:
      return description
  else:
    return ""

def getHours(startTime, endTime):
  # subtract end time from start time and return that
  try:
    hours = datetime.datetime.strptime(endTime, '%Y-%m-%dT%H:%M:%S%z') - datetime.datetime.strptime(startTime, '%Y-%m-%dT%H:%M:%S%z')
  except ValueError as e:
    print(f'Error: {e}')

  return convertTime(hours)

def convertTime(time):
  units = str(time).split(':')
  minutesToDecimal = int(units[1]) / 60
  convertedTime = f'{round(int(units[0])+minutesToDecimal, 2)}'
  return convertedTime
    
def setLastPulled(time):
    lastPulledEntry = time
    return lastPulledEntry

def createNoteTemplate(route, hours, date):
    return f'''---
Date Worked: {date}
Route: "{route}"
Hours Worked: {hours}
Has Greencard Time: {getGreenCardTime(route)}
aliases:
  - "{route} - {date}"
title: "{route} - {date}"
tags:
  - USPS
---
'''

def createNewMarkdownFile(filename, contents):
    file = open(f'files/{filename}.md', "w")
    file.write(contents)
    file.close()

def main():
  """Shows basic usage of the Google Calendar API.
  Prints the start and name of the next 10 events on the user's calendar.
  """
  creds = None
  # The file token.json stores the user's access and refresh tokens, and is
  # created automatically when the authorization flow completes for the first
  # time.
  if os.path.exists("creds/token.json"):
    creds = Credentials.from_authorized_user_file("creds/token.json", SCOPES)
  # If there are no (valid) credentials available, let the user log in.
  if not creds or not creds.valid:
    if creds and creds.expired and creds.refresh_token:
      creds.refresh(Request())
    else:
      flow = InstalledAppFlow.from_client_secrets_file(
          "creds/credentials.json", SCOPES
      )
      creds = flow.run_local_server(port=0)
    # Save the credentials for the next run
    with open("creds/token.json", "w") as token:
      token.write(creds.to_json())

  try:
    service = build("calendar", "v3", credentials=creds)

    # Call the Calendar API
    now = datetime.datetime.now(tz=NEW_YORK).isoformat()
    print("Getting the upcoming 10 events")
    events_result = (
        service.events()
        .list(
            calendarId=CALENDAR_ID,
            timeMax=now,
            singleEvents=True,
            orderBy="startTime",
        )
        .execute()
    )
    events = events_result.get("items", [])

    if not events:
      print("No events found.")
      return

    # Prints the start and name of the last 10 events
    for event in events:
      start = event["start"].get("dateTime", event["start"].get("date"))
      timezone = event["start"].get(event["start"].get("timeZone"))
      eventDate = start[:10]
      eventTime = start[12:]
      eventDescription = event["description"]
      parsedEventDescription = ParsedEventDescription(getRouteFromDescription(eventDescription), getHours(event["start"].get("dateTime"), event["end"].get("dateTime")))
    #   lastPulledEntry = setLastPulled(now)
    #   print(lastPulledEntry)

      createNewMarkdownFile(f'{eventDate} - {parsedEventDescription.route}', createNoteTemplate(parsedEventDescription.route, parsedEventDescription.hours, eventDate))

  except HttpError as error:
    print(f"An error occurred: {error}")


if __name__ == "__main__":
  main()

print("file created")