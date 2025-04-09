import io
import requests
from fastapi.responses import StreamingResponse
from tqdm import tqdm
# from fastapi.templating import Jinja2Templates


from fastapi import HTTPException, APIRouter
# mport user_sessions  # isko bhi dekhna hai
# from .auth import token_data
from .auth import TokenPayload


drive_router = APIRouter(
    prefix="/drive", tags=["Google"]
)
# templates = Jinja2Templates(directory="templates")

@drive_router.get("/")
def show_home():
    # print(token_data)
    return {"message": "Google Drive Section"}


@drive_router.get("/drive_info")
def show_drive_data(access_token: str):
    headers = {"Authorization": f"Bearer {access_token}"}
    response = requests.get("https://www.googleapis.com/drive/v3/files", headers=headers)

    if response.status_code != 200:
        raise HTTPException(status_code=400, detail="Could not fetch files")
    
    

    return response.json()

    # return templates.TemplateResponse("files.html", {"access_token": access_token, "files": response.json()})




@drive_router.get("/drive/download/{file_id}")
def download_google_file(file_id: str, access_token: str):

    # user = user_sessions[requests.client.host]

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
