from fastapi import FastAPI
from routers import auth, drive
from fastapi.middleware.cors import CORSMiddleware
# from starlette.middleware.sessions import SessionMiddleware
import models
import json


# from routers.auth import google_callback
# from database import get_db
# conn = get_db()

app = FastAPI()
app.include_router(auth.auth_router)
app.include_router(drive.drive_router)


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





