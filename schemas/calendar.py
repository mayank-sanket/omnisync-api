from pydantic import BaseModel
from typing import List
from datetime import datetime, timezone, timedelta

class AddEventRequest(BaseModel):
    summary: str
    location: str
    description: str
    start: dict
    end: dict
    recurrence: List[str]
    attendees: List[dict]
    reminders: dict

    model_config = {
        'json_schema_extra': {
            'example': {
                'summary': 'Test meeting 2',
                'location': 'Bhopal, Madhya Pradesh',
                'description': 'Test meeting 2 description',
                'start': {
                    'dateTime': '2025-05-28T09:00:00-07:00',
                    'timeZone': 'UTC+05:30',               # IST 
                },
                'end': {
                    'dateTime': '2025-05-28T17:00:00-07:00',
                    'timeZone': 'UTC+05:30',  #  IST
                },
                'recurrence': [
                    'RRULE:FREQ=DAILY;COUNT=2'
                ],
                'attendees': [
                    {'email': 'mayanksanket@gmail.com'},
                    {'email': 'mayanksanket7@gmail.com'},
                ],
                'reminders': {
                    'useDefault': False,
                    'overrides': [
                        {'method': 'email', 'minutes': 24 * 60},
                        {'method': 'popup', 'minutes': 10},
                    ],
                },
            }
        }
    }