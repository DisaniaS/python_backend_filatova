from datetime import timedelta
from http.client import responses

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import parse_obj_as
from typing import List

from user.schema import User, UserCreate, UserLogin, UserLoginResponse
from user.repository import UserRepository

from utils.jwt_auth import create_access_token, decode_token, ACCESS_TOKEN_EXPIRE_MINUTES
from fastapi.security import OAuth2PasswordBearer

import bcrypt

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/", response_model=List[User])
def list_users(token: str = Depends(oauth2_scheme), skip: int = 0, max: int = 10, users: UserRepository = Depends()):
    payload = decode_token(token)
    if payload is None:
        raise HTTPException(status_code=401, detail="Неверный токен или срок действия истёк")

    db_users = users.all(skip=skip, max=max)
    return parse_obj_as(List[User], db_users)

@router.get("/{user_id}", response_model=User)
def get_user(user_id: int, users: UserRepository = Depends()):
    db_user = users.find(user_id)

    if db_user is None:
        raise HTTPException(
            status_code=404,
            detail="Пользователь не найден"
        )

    return User.model_validate(db_user)

@router.post("/registration", response_model=UserLoginResponse, status_code=status.HTTP_201_CREATED)
def registration(user: UserCreate, users: UserRepository = Depends()):
    db_user = users.find_by_login(login=user.login)
    if db_user:
        raise HTTPException(
            status_code=409,
            detail="Логин занят"
        )
    token_data = {"sub": user.login}
    access_token = create_access_token(data=token_data, expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))

    db_user = users.registration(user)

    response = UserLoginResponse(
        id=db_user.id,
        login=user.login,
        fname=user.fname,
        lname=user.lname,
        sname=user.sname,
        token=access_token
    )
    users.registration(user)
    return response

@router.post("/login", response_model=UserLoginResponse, status_code=status.HTTP_200_OK)
def login(user: UserLogin, users: UserRepository = Depends()):
    db_user = users.find_by_login(user.login)

    if db_user is None or not bcrypt.checkpw(user.password.encode(), db_user.password.encode()):
        raise HTTPException(
            status_code=401,
            detail="Неверный логин или пароль"
        )

    token_data = {"sub": user.login}
    access_token = create_access_token(data=token_data, expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))

    response = UserLoginResponse(
        id=db_user.id,
        login=db_user.login,
        fname=db_user.fname,
        lname=db_user.lname,
        sname=db_user.sname,
        token=access_token
    )

    return response

@router.get("/check_auth", response_model=UserLoginResponse, status_code=status.HTTP_200_OK)
def check_auth(token: str = Depends(oauth2_scheme), users: UserRepository = Depends()):
    payload = decode_token(token)
    if payload is None:
        raise HTTPException(status_code=401, detail="Вы не авторизованы")
    login = payload.get("sub")
    db_user = users.find_by_login(login)

    return User.model_validate(db_user)