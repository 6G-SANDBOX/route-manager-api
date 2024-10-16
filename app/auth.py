# app/auth.py
from fastapi import HTTPException, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import logging
from app.config import get_variable

logger = logging.getLogger(__name__)

APITOKEN = get_variable('APITOKEN')

class TokenAuth(HTTPBearer):
    def __init__(self, auto_error: bool = True):
        super(TokenAuth, self).__init__(auto_error=auto_error)

    async def __call__(self, request: Request):
        credentials: HTTPAuthorizationCredentials = await super(TokenAuth, self).__call__(request)
        if credentials:
            if credentials.credentials != APITOKEN:
                logger.warning("Invalid or expired token")
                raise HTTPException(status_code=403, detail="Invalid or expired token")
            return credentials.credentials
        else:
            logger.warning("Missing token")
            raise HTTPException(status_code=403, detail="Invalid or expired token")

auth = TokenAuth()
