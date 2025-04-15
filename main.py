from fastapi import FastAPI
from routers import auth, drive, calendar
from fastapi.middleware.cors import CORSMiddleware
# from starlette.middleware.sessions import SessionMiddleware
import models
import json
from passlib.context import CryptContext
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")




# from routers.auth import google_callback
# from database import get_db
# conn = get_db()

app = FastAPI()
app.include_router(auth.auth_router)
app.include_router(drive.drive_router)
app.include_router(calendar.calendar_router)


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





