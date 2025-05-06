from fastapi import APIRouter, Depends, HTTPException
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from email.message import EmailMessage
import base64
from pydantic import BaseModel
from dependencies import get_current_user
from models import cursor
from utils.fernet import decrypt_data

gmail_router = APIRouter(
    prefix="/gmail",
    tags=["Google"]
)

class EmailSchema(BaseModel):
    to: str
    subject: str
    content: str

@gmail_router.post("/send")
async def gmail_send_message(user = Depends(get_current_user)):
    try:
        # Get user's email and access token
        user_email = user.get('email')
        if not user_email:
            raise HTTPException(
                status_code=401, 
                detail="User email not found"
            )
        
        

        # Fetch access token from database
        cursor.execute(
            """
            SELECT access_token 
            FROM account_session 
            WHERE email = %s
            """, 
            (user_email,)
        )
        result = cursor.fetchone()
        if not result:
            raise HTTPException(
                status_code=401,
                detail="Access token not found"
            )

        # Initialize Gmail API with user's credentials
        access_token = decrypt_data(result[0])
        credentials = Credentials(token=access_token)
        service = build("gmail", "v1", credentials=credentials)
        
        # Create email message
        message = EmailMessage()
        message.set_content("This is automated draft mail")
        message["To"] = "mayanksanket@gmail.com"
        message["From"] = user_email  # Use authenticated user's email
        message["Subject"] = "Automated draft"

        # Encode and send message
        encoded_message = base64.urlsafe_b64encode(message.as_bytes()).decode()
        create_message = {"raw": encoded_message}
        
        send_message = (
            service.users()
            .messages()
            .send(userId="me", body=create_message)
            .execute()
        )

        return {
            "status": "success",
            "messageId": send_message["id"]
        }

    except HttpError as error:
        raise HTTPException(
            status_code=400, 
            detail=f"Gmail API error: {str(error)}"
        )
    except Exception as error:
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(error)}"
        )
