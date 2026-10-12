from fastapi import HTTPException
from sqlalchemy.exc import IntegrityError

from app.core.security import hash_password
from app.crud.user import create_user, get_user_by_email, get_user_by_phone


def register_user(db, data):
    if get_user_by_email(db, data.email):
        raise HTTPException(status_code=409, detail="Email is already registered.")
    if data.phone and get_user_by_phone(db, data.phone):
        raise HTTPException(status_code=409, detail="Phone is already registered.")

    password_hash = hash_password(data.password)
    try:
        return create_user(db, data, password_hash)
    except IntegrityError as error:
        db.rollback()
        # MySQL error 1062 means another request inserted the same unique value.
        if error.orig.args[0] == 1062:
            raise HTTPException(status_code=409, detail="Email or phone is already registered.") from error
        raise
