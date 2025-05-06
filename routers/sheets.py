from fastapi import APIRouter, HTTPException, Depends
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from datetime import datetime
from database import get_db, psycopg2
from utils.fernet import decrypt_data
from models import cursor
from dependencies import get_current_user

sheets_router = APIRouter(
    prefix="/sheets", 
    tags=["Sheets"]
)

@sheets_router.get("/")
async def sheet_home():
    
    return {"message": "Welcome to Sheets"}

@sheets_router.post("/create-sheets")
async def create_sheet(title: str, user = Depends(get_current_user)):

    try:
        # Get user's access token from database
        user_email = user.get('email')
        if not user_email:
            raise HTTPException(
                status_code=401, 
                detail="User email not found"
            )

        # Fetch and decrypt access token
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
        
        access_token = decrypt_data(result[0])
        

        credentials = Credentials(token=access_token)
        service = build("sheets", "v4", credentials=credentials)
        
        # Create new spreadsheet
        spreadsheet = {
            "properties": {
                "title": title
            }
        }
        
        response = service.spreadsheets().create(
            body=spreadsheet,
            fields="spreadsheetId"
        ).execute()
        
        return {
            "message": "Spreadsheet created successfully", 
            "spreadsheetId": response.get('spreadsheetId')
        }
                
    except HttpError as error:
        raise HTTPException(
            status_code=400, 
            detail=f"Google Sheets API error: {str(error)}"
        )
    except Exception as error:
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(error)}"
        )



@sheets_router.get("/read-sheets")
async def read_sheet_data(spreadsheet_id: str, range_name, user = Depends(get_current_user)):
    try:
        # Get user's access token from database
        user_email = user.get('email')
        if not user_email:
            raise HTTPException(
                status_code=401, 
                detail="User email not found"
            )

        cursor.execute("""
                SELECT expires_at FROM account_session
                WHERE email = %s
                        """, (user_email,))
        


        expires_at = cursor.fetchone()[0]
        

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
        
        access_token = decrypt_data(result[0])
        

        credentials = Credentials(token=access_token)
        service = build("sheets", "v4", credentials=credentials)

        result = (
            service.spreadsheets()
            .values()
            .get(spreadsheetId = spreadsheet_id, range = range_name)
            .execute()
        )
        rows = result.get("values", [])
        print(f"{len(rows)} rows retrieved")
        return result
    except HttpError as error:
        print(f"An error occurred: {error}")
        return error



@sheets_router.put("/update-sheets")
async def sheets_batch_update(spreadsheet_id: str, title: str, find: str, replacement: str,  user = Depends(get_current_user)):
    try:
        
        user_email = user.get('email')
        if not user_email:
            raise HTTPException(
                status_code=401, 
                detail="User email not found"
            )

        
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
        
        access_token = decrypt_data(result[0])
        

        credentials = Credentials(token=access_token)
        service = build("sheets", "v4", credentials=credentials)
        requests = []

        requests.append(
        {
            "updateSpreadsheetProperties": {
                "properties": {"title": title},
                "fields": "title",
            }
        }
          )
        requests.append(
        {
            "findReplace": {
                "find": find,
                "replacement": replacement,
                "allSheets": True,
            }
        }
         )
        body = {"requests": requests}
        response = (
        service.spreadsheets()
        .batchUpdate(spreadsheetId=spreadsheet_id, body=body)
        .execute()
    )
        find_replace_response = response.get("replies")[1].get("findReplace")
        print(
        f"{find_replace_response.get('occurrencesChanged')} replacements made."
    )
        return response

    except HttpError as error:
        print(f"An error occurred: {error}")
        return error