from fastapi import APIRouter, Depends, Request, Response
from sqlalchemy.orm import Session

from app.core.deps import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.schemas.auth import ForgotPasswordRequest, MessageResponse, RefreshRequest, ResetPasswordRequest, TokenResponse, UserLogin
from app.schemas.user import UserRegister, UserResponse
from app.services.auth import forgot_password, login_user, logout_user, refresh_user_tokens, register_user, reset_password


router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/register", response_model=UserResponse, status_code=201)
def register(data: UserRegister, db: Session = Depends(get_db)):
    return register_user(db, data)


@router.post("/login", response_model=TokenResponse)
def login(data: UserLogin, request: Request, db: Session = Depends(get_db)):
    ip_address = request.client.host if request.client else None
    return login_user(db, data, ip_address, request.headers.get("user-agent"))


@router.post("/refresh", response_model=TokenResponse)
def refresh(data: RefreshRequest, request: Request, db: Session = Depends(get_db)):
    ip_address = request.client.host if request.client else None
    return refresh_user_tokens(db, data, ip_address, request.headers.get("user-agent"))


@router.post("/logout", status_code=204)
def logout(data: RefreshRequest, db: Session = Depends(get_db)):
    logout_user(db, data)
    return Response(status_code=204)


@router.get("/me", response_model=UserResponse)
def me(current_user: User = Depends(get_current_user)):
    return current_user


@router.post("/forgot-password", response_model=MessageResponse)
def forgot(data: ForgotPasswordRequest, db: Session = Depends(get_db)):
    return forgot_password(db, data)


@router.post("/reset-password", response_model=MessageResponse)
def reset(data: ResetPasswordRequest, db: Session = Depends(get_db)):
    return reset_password(db, data)
