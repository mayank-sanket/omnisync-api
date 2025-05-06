import io
import requests
from fastapi import Depends
from typing import Annotated
from fastapi.responses import StreamingResponse
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from dependencies import get_current_user

SECRET_KEY = "MAYANKSANKETTESTING13432321234321234321234321"
ALGORITHM = "HS256"
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

from tqdm import tqdm
# from fastapi.templating import Jinja2Templates


from fastapi import HTTPException, APIRouter 
from .auth import user_sessions  # isko bhi dekhna hai
# from .auth import token_data
from .auth import TokenPayload
from utils.fernet import encrypt_data, decrypt_data
import config, psycopg2

conn = psycopg2.connect(config.DATABASE_URL)
cursor = conn.cursor()


# def authenticate_user(access_token: Annotated[str, Depends(oauth2_scheme)] ):
#     cursor.execute("""SELECT access_token FROM account_session WHERE access_token = %s""", (encrypt_data(access_token)))
#     access_token = decrypt_data(cursor.fetchone()[0])
#     return access_token



drive_router = APIRouter(
    prefix="/drive", tags=["Google"]
)
# templates = Jinja2Templates(directory="templates")

@drive_router.get("/")
def show_home():
    # print(token_data)
    return {"message": "Google Drive Section"}



@drive_router.get("/drive_info")
def show_drive_data(user = Depends(get_current_user) ):
    user_email = user.get('email')
    cursor.execute("""SELECT access_token FROM account_session where email = %s""", (user_email,))

    access_token = decrypt_data(cursor.fetchone()[0])
    headers = {"Authorization": f"Bearer {access_token}"}
    response = requests.get("https://www.googleapis.com/drive/v3/files", headers=headers)

    if response.status_code != 200:
        raise HTTPException(status_code=400, detail="Could not fetch files")
    
    

    return response.json()

    # return templates.TemplateResponse("files.html", {"access_token": access_token, "files": response.json()})




@drive_router.get("/drive/download/{file_id}")
def download_google_file(file_id: str, user = Depends(get_current_user)):

    user_email = user.get('email')
    cursor.execute("""SELECT access_token FROM account_session WHERE email = %s""", (user_email, ))
    access_token = decrypt_data(cursor.fetchone()[0])
    headers = {"Authorization": f"Bearer {access_token}"}
    download_url = f"https://www.googleapis.com/drive/v3/files/{file_id}?alt=media"

    response = requests.get(download_url, headers=headers, stream=True)
    total = int(response.headers.get('content-length', 0))
    chunk_size = 1024 * 1024


    progress_bar = tqdm(total=total, unit='B', unit_scale=True)

    def iterfile():
        for chunk in response.iter_content(chunk_size=chunk_size):
            if chunk:
                progress_bar.update(len(chunk))
                yield chunk
        progress_bar.close()

    if response.status_code != 200:
        raise HTTPException(status_code=400, detail="Failed to download file")

    return StreamingResponse(iterfile(), media_type="application/octet-stream")
