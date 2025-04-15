
from dotenv import load_dotenv
import os
load_dotenv()
from cryptography.fernet import Fernet
key = Fernet.generate_key()

ENCRYPTION_KEY = os.getenv("ENCRYPTION_KEY")
fernet = Fernet(ENCRYPTION_KEY.encode())


def encrypt_data(data: str) -> str:
    return fernet.encrypt(data.encode()).decode()

def decrypt_data(token: str) -> str:
    return fernet.decrypt(token.encode()).decode()

