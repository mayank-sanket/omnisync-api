import config
from fastapi import requests, Request
from datetime import timezone, datetime
from routers.auth import encrypt_data, decrypt_data, user_sessions
from fastapi import HTTPException
from starlette import status

import psycopg2
conn = psycopg2.connect(config.DATABASE_URL)
cursor = conn.cursor()

from routers.auth import google_callback

def refresh_access(refresh_token:str):
    token_url ="https://oauth2.googleapis.com/token"
    payload = {
    "client_id": config.GOOGLE_CLIENT_ID,
    "client_secret": config.GOOGLE_CLIENT_SECRET,
    "refresh_token": refresh_token,
    "grant_type": "refresh_token"
        }

    response = requests.post(token_url, data=payload)

    if response.status_code != 200:
        raise Exception("Failed to refresh access token")
    
    cursor.execute("SELECT expires_at FROM account_session where email = %s", (user_sessions['key_host_port'].get('email')))
    expires_at = cursor.fetchone()[0]
    if expires_at > datetime.now(timezone.utc):
        print("hey")
