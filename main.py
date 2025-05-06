
from routers import auth, drive, calendar,gmail, forms, sheets
from fastapi.middleware.cors import CORSMiddleware
from fastapi.templating import Jinja2Templates
from fastapi import Request

# from flask import Flask,render_template    # import Blueprint also if you want to use thing like API Router
# from asgiref.wsgi import WsgiToAsgi

# flask_app = Flask(__name__, template_folder = "templates")


# @flask_app.route("/home")
# def flask_hello():
#     return render_template("index.html")

# asgi_flask_app = WsgiToAsgi(flask_app)

# from starlette.middleware.sessions import SessionMiddleware
from fastapi import Depends, FastAPI
from dependencies import get_current_user


# fastapi template

templates = Jinja2Templates(directory="templates")

import httpx

from dotenv import load_dotenv
import os
load_dotenv()

app = FastAPI()

app.include_router(auth.auth_router)
app.include_router(drive.drive_router)
app.include_router(calendar.calendar_router)
app.include_router(gmail.gmail_router)
app.include_router(forms.forms_router)
app.include_router(sheets.sheets_router)

# app.mount("/flask-app", asgi_flask_app)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  
    allow_credentials=True,
    allow_methods=["*"],  
    allow_headers=["*"],  
)

@app.get("/")
def root():
    return {"message": "Welcome to OmniSync!"}


@app.get("/protected")
async def protected_route(user=Depends(get_current_user)):
    return {"message": "Welcome!", "user": user}


@app.post("/token", include_in_schema=False)
def dummy_token():
    pass  


# @app.get("/flask/mayanktest")
# def show_flasktest(request: Request):
#     return templates.TemplateResponse("index.html", {"request": request})