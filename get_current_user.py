from fastapi import Request
def get_current_user(request: Request):
    print(request)
