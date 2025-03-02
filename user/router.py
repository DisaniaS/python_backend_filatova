from fastapi import APIRouter, Depends, status
from typing import List
from .service import UserService
from user.schema import User, UserCreate, UserLogin, UserLoginResponse
from fastapi.security import OAuth2PasswordBearer
from utils.authenticate import check_authenticate

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

router = APIRouter(prefix="/users", tags=["users"])


@router.get(
    "/",
    response_model=List[User]
)
def list_users(
    token: str = Depends(oauth2_scheme),
    skip: int = 0,
    max: int = 10,
    user_service: UserService = Depends()
):
    return user_service.list_users(token, skip=skip, max=max)

@router.get(
    "/{user_id}",
    response_model=User
)
def get_user(
    user_id: int,
    user_service: UserService = Depends(),
    token: dict = Depends(check_authenticate)
):
    return user_service.get_user(user_id)

@router.post(
    "/registration",
    response_model=UserLoginResponse,
    status_code=status.HTTP_201_CREATED
)
def registration(
    user: UserCreate,
    user_service: UserService = Depends(),
    token: dict = Depends(check_authenticate)
):
    return user_service.registration(user)

@router.post(
    "/login",
    response_model=UserLoginResponse,
    status_code=status.HTTP_200_OK
)
def login(
    user: UserLogin,
    user_service: UserService = Depends()
):
    return user_service.login(user)

@router.get(
    "/check_auth",
    response_model=UserLoginResponse,
    status_code=status.HTTP_200_OK
)
def check_auth(
    token: str = Depends(oauth2_scheme),
    user_service: UserService = Depends()
):
    return user_service.check_auth(token)