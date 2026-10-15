from fastapi import APIRouter, Depends, Request, Response
from sqlalchemy.orm import Session

from app.core.deps import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.schemas.auth import (
    ForgotPasswordRequest,
    MessageResponse,
    RefreshRequest,
    ResetPasswordRequest,
    TokenResponse,
    UserLogin,
)
from app.schemas.user import UserRegister, UserResponse
from app.schemas.problem import problem_responses
from app.services.auth import (
    forgot_password,
    login_user,
    logout_user,
    refresh_user_tokens,
    register_user,
    reset_password,
)


router = APIRouter(
    prefix="/auth",
    tags=["Authentication"],
    responses=problem_responses(429, 500),
)


@router.post("/register", response_model=UserResponse, status_code=201,
             responses=problem_responses(409, 422))
def register(data: UserRegister, request: Request, db: Session = Depends(get_db)):
    ip_address = request.client.host if request.client else None
    return register_user(db, data, ip_address)


@router.post("/login", response_model=TokenResponse, responses=problem_responses(401, 403, 422))
def login(data: UserLogin, request: Request, db: Session = Depends(get_db)):
    ip_address = request.client.host if request.client else None
    return login_user(db, data, ip_address, request.headers.get("user-agent"))


@router.post("/refresh", response_model=TokenResponse, responses=problem_responses(401, 403, 422))
def refresh(data: RefreshRequest, request: Request, db: Session = Depends(get_db)):
    ip_address = request.client.host if request.client else None
    return refresh_user_tokens(db, data, ip_address, request.headers.get("user-agent"))


@router.post("/logout", status_code=204, responses=problem_responses(401, 422))
def logout(data: RefreshRequest, request: Request, db: Session = Depends(get_db)):
    ip_address = request.client.host if request.client else None
    logout_user(db, data, ip_address)
    return Response(status_code=204)


@router.get("/me", response_model=UserResponse, responses=problem_responses(401, 403))
def me(current_user: User = Depends(get_current_user)):
    return current_user


@router.post("/forgot-password", response_model=MessageResponse, responses=problem_responses(422, 503))
def forgot(data: ForgotPasswordRequest, request: Request, db: Session = Depends(get_db)):
    ip_address = request.client.host if request.client else None
    return forgot_password(db, data, ip_address)


@router.post("/reset-password", response_model=MessageResponse, responses=problem_responses(400, 422))
def reset(data: ResetPasswordRequest, request: Request, db: Session = Depends(get_db)):
    ip_address = request.client.host if request.client else None
    return reset_password(db, data, ip_address)
