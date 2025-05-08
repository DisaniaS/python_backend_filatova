from fastapi import APIRouter, Depends, status
from typing import List
from .service import UserService
from user.schema import User, UserCreate, UserLogin, UserLoginResponse, UpdateUserRole
from fastapi.security import OAuth2PasswordBearer
from utils.authenticate import check_authenticate, check_admin

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

router = APIRouter(prefix="/users", tags=["users"])


@router.get(
    "",
    response_model=List[User]
)
def list_users(
    token: dict = Depends(check_admin),
    skip: int = 0,
    max: int = 10,
    user_service: UserService = Depends()
):
    return user_service.list_users(skip=skip, max=max)

# Сначала определяем конкретные маршруты
@router.post(
    "/registration",
    response_model=UserLoginResponse,
    status_code=status.HTTP_201_CREATED
)
def registration(
    user: UserCreate,
    user_service: UserService = Depends()
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

# Затем определяем маршруты с параметрами
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

@router.put(
    "/{user_id}/role",
    response_model=User,
    status_code=status.HTTP_200_OK
)
def update_user_role(
    user_id: int,
    update_data: UpdateUserRole,
    user_service: UserService = Depends(),
    token: dict = Depends(check_admin)  # Только админ может менять роли
):
    return user_service.update_user_role(user_id, update_data)