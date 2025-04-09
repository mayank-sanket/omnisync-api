from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
import requests
import config
from typing import Optional
from pydantic import BaseModel
import config
import psycopg2

from dotenv import load_dotenv
import os
load_dotenv()

from cryptography.fernet import Fernet

# database mein values ko encrypt karne ke liye


GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET")


ENCRYPTION_KEY = os.getenv("ENCRYPTION_KEY")
fernet = Fernet(ENCRYPTION_KEY.encode())

def encrypt_data(data: str) -> str:
    return fernet.encrypt(data.encode()).decode()

def decrypt_data(token: str) -> str:
    return fernet.decrypt(token.encode()).decode()




# database values encrypt karne ka end

conn = psycopg2.connect(config.DATABASE_URL)
cursor = conn.cursor()

auth_router = APIRouter(
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
    # print("\n")
    print(f"TOKEN DATA: {token_data}")

    if "error" in token_data:
        return {"error": token_data["error"]}
    
    refresh_token = token_data.get("refresh_token") # plain refresh token 
    def refresh_access(refresh_token):
        token_url ="https://oauth2.googleapis.com/token"
        payload = {
        "client_id": GOOGLE_CLIENT_ID,
        "client_secret": GOOGLE_CLIENT_SECRET,
        "refresh_token": refresh_token,
        "grant_type": "refresh_token"
        }

        response = requests.post(token_url, data=payload)

        if response.status_code != 200:
            raise Exception("Failed to refresh access token")
        return response.json()["access_token"]
    
    refresh_token = encrypt_data(refresh_token) # encrypted refresh token

    # is line ko fix karna hai (jaise ki access token hamesha hi refresh token se generate hoga)
    # access_token = token_data.get("access_token")
    access_token = refresh_access(decrypt_data(refresh_token))
    access_token  = encrypt_data(access_token)
    # print(access_token)
    print("\n")
    print(decrypt_data(access_token))


    user_info = requests.get("https://www.googleapis.com/oauth2/v2/userinfo",
                         headers={"Authorization": f"Bearer {decrypt_data(access_token)}"}).json()

    user_sessions[request.client.host] = user_info

    print(f"user sessions: {user_sessions}")
    print(f"user_info {user_info}")

    cursor.execute("""
    INSERT INTO accounts (id, email)
    VALUES (%s, %s)
    ON CONFLICT (id) DO NOTHING
    """, (user_info["id"], user_info["email"]))


    cursor.execute("""
    SELECT 1 FROM account_session WHERE email = %s LIMIT 1
    """, (user_info["email"],))
    exists = cursor.fetchone()

    if exists: 
        return user_info
    
    else:
        cursor.execute("""
        INSERT INTO account_session (id, email, access_token, refresh_token)
        VALUES (%s, %s, %s, %s)
        """, (user_info["id"], user_info["email"], access_token, refresh_token))
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


