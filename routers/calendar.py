import requests
from fastapi import HTTPException, APIRouter, Depends
from utils.fernet import encrypt_data, decrypt_data
from database import get_db, psycopg2
from models import cursor

from dependencies import get_current_user

from schemas.calendar import AddEventRequest

from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials

def get_service(access_token: str):
    credentials = Credentials(token=access_token)
    return build('calendar', 'v3', credentials=credentials)

calendar_router = APIRouter(prefix="/calendar",
                            tags=["Google"])




@calendar_router.get("/")
def calendar_test():
    return {"data": "testing"}

@calendar_router.get("/calendar_info")
def get_calendar_events(access_token: str):
    headers = {
        "Authorization": f"Bearer {access_token}"
    }

    response = requests.get(
        "https://www.googleapis.com/calendar/v3/calendars/primary/events",
        headers=headers,
        # params={
        #     "maxResults": 10,
        #     "orderBy": "startTime",
        #     "singleEvents": "true",
        #     "timeMin": "2025-01-01T00:00:00Z",  
        # }
    )

    if response.status_code == 200:
        return response.json()["items"]
    else:
        raise Exception(f"Failed to fetch events: {response.text}")


@calendar_router.post("/create-event")

def create_event( request_body: AddEventRequest, user = Depends(get_current_user) ):
    # cursor.execute("""SELECT access_token FROM account_session LIMIT 1""")
    user_email = str(user.get('email'))
    print(user_email)
    cursor.execute("""SELECT access_token FROM account_session WHERE email = %s """, (user_email,))
    access_token = decrypt_data(cursor.fetchone()[0])
    service = get_service(access_token)

    # event = {
    #     'summary': 'Test meeting 2',
    #     'location': 'Bhopal, Madhya Pradesh',
    #     'description': 'Test meeting 2 description',
    #     'start': {
    #         'dateTime': '2025-05-28T09:00:00-07:00',
    #         'timeZone': 'America/Los_Angeles',
    #     },
    #     'end': {
    #         'dateTime': '2025-05-28T17:00:00-07:00',
    #         'timeZone': 'America/Los_Angeles',
    #     },
    #     'recurrence': [
    #         'RRULE:FREQ=DAILY;COUNT=2'
    #     ],
    #     'attendees': [
    #         {'email': 'mayanksanket@gmail.com'},
    #         {'email': 'mayanksanket7@gmail.com'},
    #     ],
    #     'reminders': {
    #         'useDefault': False,
    #         'overrides': [
    #             {'method': 'email', 'minutes': 24 * 60},
    #             {'method': 'popup', 'minutes': 10},
    #         ],
    #     },
    # }

    created_event = service.events().insert(calendarId='primary', body=request_body.model_dump()).execute()
    return {'message': 'Event created', 'link': created_event.get('htmlLink')}


@calendar_router.delete("/events/")
def delete_event(event_id: str, calendar_id: str):
    cursor.execute("""SELECT access_token FROM account_session LIMIT 1""")
    access_token = decrypt_data(cursor.fetchone()[0])
    service = get_service(access_token)
    service.events().delete(calendarId=calendar_id, eventId=event_id).execute()
