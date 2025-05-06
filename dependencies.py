import httpx
from fastapi import FastAPI, HTTPException, Security
from fastapi.security import APIKeyHeader
from starlette import status

api_key_header = APIKeyHeader(name="Authorization", auto_error=True)



GOOGLE_USERINFO_URL = "https://www.googleapis.com/oauth2/v3/userinfo"

async def get_current_user(authorization: str = Security(api_key_header)):
    async with httpx.AsyncClient() as client:
        response = await client.get(
            GOOGLE_USERINFO_URL,
            headers={"Authorization": f"Bearer {authorization}"}
        )

    if response.status_code != 200:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid Google access token"
        )
    
    user_info = response.json()
    return user_info