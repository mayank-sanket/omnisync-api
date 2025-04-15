from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
import requests
import config
from typing import Optional
from pydantic import BaseModel
import config
import psycopg2
from datetime import datetime, timezone, timedelta
from utils.fernet import encrypt_data, decrypt_data

from dotenv import load_dotenv
import os
load_dotenv()





# database mein values ko encrypt karne ke liye


GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET")




conn = psycopg2.connect(config.DATABASE_URL)
cursor = conn.cursor()

auth_router = APIRouter(tags=["Auth"]
)

templates = Jinja2Templates(directory="templates")



GOOGLE_AUTH_URL = "https://accounts.google.com/o/oauth2/auth"
GOOGLE_TOKEN_URL = "https://oauth2.googleapis.com/token"
import urllib.parse

# token_data = {} # aise hi daala tha pata nahi kyun

user_sessions = {}

scopes = [
    "https://www.googleapis.com/auth/drive",
    "https://www.googleapis.com/auth/documents",
    "https://www.googleapis.com/auth/calendar",

    "openid",
    "profile",
    "email"
]

scope_str = urllib.parse.quote_plus(" ".join(scopes))



@auth_router.get("/", response_class=HTMLResponse)
async def login_page(request: Request):
    google_login_url = (
    f"{GOOGLE_AUTH_URL}?client_id={config.GOOGLE_CLIENT_ID}"
    f"&redirect_uri={config.REDIRECT_URI}"
    f"&response_type=code"
    f"&scope={scope_str}"
    f"&access_type=offline"
    f"&prompt=consent"
)

    return templates.TemplateResponse("login.html", {"request": request, "google_login_url": google_login_url})



@auth_router.get("/auth/google/callback")
async def google_callback(request: Request):
    code = request.query_params.get("code")
    if not code:
        return {"error": "Authorization code not provided"}

    data = {
        "client_id": config.GOOGLE_CLIENT_ID,
        "client_secret": config.GOOGLE_CLIENT_SECRET,
        "code": code,
        "grant_type": "authorization_code",
        "redirect_uri": config.REDIRECT_URI
    }
    response = requests.post(GOOGLE_TOKEN_URL, data=data)
    # response = requests.post(RedirectResponse)
    token_data = response.json()
    print(f"TOKEN DATA: {token_data}")

    if "error" in token_data:
        return {"error": token_data["error"]}
    
    refresh_token = token_data.get("refresh_token") # plain refresh token 
    refresh_token = encrypt_data(refresh_token) # encrypted refresh token
    access_token  = encrypt_data(token_data.get('access_token')) # encrypted access token
    user_info = requests.get("https://www.googleapis.com/oauth2/v2/userinfo",
                         headers={"Authorization": f"Bearer {decrypt_data(access_token)}"}).json()
    
    client_host = request.client.host
    client_port = request.client.port
    key_host_port = f"{client_host}:{client_port}"
    user_sessions[key_host_port] = user_info
    
    print(user_sessions)

    cursor.execute("""
    INSERT INTO accounts (id, email)
    VALUES (%s, %s)
    ON CONFLICT (id) DO NOTHING
    """, (user_info["id"], user_info["email"]))

    # cursor.execute("""
    # SELECT 1 FROM account_session WHERE email = %s LIMIT 1
    # """, (user_info["email"],))
    # exists = cursor.fetchone()

    cursor.execute("DELETE FROM account_session where email = %s", (user_info['email'], ))

    cursor.execute("""
        INSERT INTO account_session (id, email, access_token, refresh_token, expires_at)
        VALUES (%s, %s, %s, %s, %s)
        """, (user_info["id"], user_info["email"], access_token, refresh_token, datetime.now(timezone.utc) + timedelta(seconds=token_data['expires_in'])))
    conn.commit()
    # return templates.TemplateResponse("profile.html", {"request": request, "user": user_info})
    return user_info

class TokenPayload(BaseModel):
    access_token: str

@auth_router.post("/auth/google/callback")
async def google_callback(payload: TokenPayload):
    access_token = payload.access_token

    user_info = requests.get(
        "https://www.googleapis.com/oauth2/v2/userinfo",
        headers={"Authorization": f"Bearer {access_token}"}
    ).json()

    
    
    drive_data = requests.get(
        "https://www.googleapis.com/drive/v3/files",
        headers={"Authorization": f"Bearer {access_token}"}
    ).json()

    return {
        "user": user_info,
        "drive_files": drive_data,
    }


@auth_router.get("/logout")
async def logout(request: Request):
    user_sessions.pop(request.client.host, None)
    return RedirectResponse(url="/")


