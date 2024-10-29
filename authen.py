# https://stackoverflow.com/questions/67942766/fastapi-api-key-as-parameter-secure-enough
# https://fastapi.tiangolo.com/tutorial/security/simple-oauth2/
import os

from fastapi import Depends, HTTPException, Request
from fastapi.security import OAuth2PasswordBearer
from starlette import status

# Use token based authentication
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

SECRETKEY = 'gGaQfRuJ80k4JTErVxA5V9NQ8OB9fP'

# Ensure the request is authenticated


def auth_request(token: str = Depends(oauth2_scheme), login: str = Depends(oauth2_scheme)) -> bool:
    authenticated = token == os.getenv("API_KEY", SECRETKEY)
    # print(login)
    if login == "success":
        return authenticated
    if not authenticated:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated")
    return authenticated
