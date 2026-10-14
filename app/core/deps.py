from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError
from sqlalchemy.orm import Session

from app.core.constants import UserStatus
from app.core.security import decode_token
from app.crud.user import get_user_by_uuid
from app.db.session import get_db


bearer_auth = HTTPBearer(auto_error=False)


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_auth),
    db: Session = Depends(get_db),
):
    unauthorized = HTTPException(
        status_code=401,
        detail="A valid access token is required.",
        headers={"WWW-Authenticate": "Bearer"},
    )
    if credentials is None:
        raise unauthorized

    try:
        claims = decode_token(credentials.credentials, "access")
    except JWTError:
        raise unauthorized

    # Read the current role and status from the database, not from the token.
    user = get_user_by_uuid(db, claims["sub"])
    if user is None:
        raise unauthorized
    if user.status != UserStatus.ACTIVE:
        raise HTTPException(status_code=403, detail="Account must be active.")
    return user
