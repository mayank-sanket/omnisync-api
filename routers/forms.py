from fastapi import APIRouter, Depends
from dependencies import get_current_user
from apiclient import discovery
from httplib2 import Http
from oauth2client import client, file, tools
from utils.fernet import encrypt_data, decrypt_data
from .auth import cursor
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build


SCOPES = "https://www.googleapis.com/auth/forms.responses.readonly"
DISCOVERY_DOC = "https://forms.googleapis.com/$discovery/rest?version=v1"

forms_router = APIRouter(
    prefix="/forms",
    tags=["Forms"]
)





@forms_router.get("/")
def show_forms():
    return {"message": "welcome to forms"}


@forms_router.get("/read-forms/{form_id}")
def create_form(form_id: str, user = Depends(get_current_user)):
    user_email = user.get('email')
    cursor.execute("""SELECT access_token FROM account_session WHERE email = %s""", (user_email,))
    access_token = decrypt_data(cursor.fetchone()[0])

    creds = None
    creds = Credentials(access_token)
    service = build('forms', 'v1', credentials=creds)
    print(f"SERVICE: {service}")
    print(f"CREDENTIALS: {creds}")

    result = service.forms().responses().list(formId=form_id).execute()
    if not result or 'responses' not in result:
        return {"message": "No responses found for the given form ID"}
    return result