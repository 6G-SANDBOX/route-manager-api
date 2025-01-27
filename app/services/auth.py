# app/auth.py
import logging
from fastapi import HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from app.core.config import settings

logger = logging.getLogger(__name__)
security = HTTPBearer()

def bearer_token(credentials: HTTPAuthorizationCredentials = Depends(security)) -> None:
    """
    Validates the Bearer token received in the HTTP Authorization header.

    Args:
        credentials (HTTPAuthorizationCredentials): Contains the authentication scheme ("Bearer") 
                                                     and the token sent by the client.

    Returns:
        Dict[str, Any]: A dictionary containing token metadata if the token is valid.

    Raises:
        HTTPException: If the token is missing, not provided, or invalid.
    """
    if credentials.credentials != settings.APITOKEN:
        logger.warning("Invalid or expired token")
        raise HTTPException(status_code=401, detail="Invalid or expired token")
