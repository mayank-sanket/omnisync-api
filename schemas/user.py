from pydantic import BaseModel, EmailStr

class User(BaseModel):
    email: EmailStr
    full_name: str


class UserInDB(User):
    hashed_access_token: str
    