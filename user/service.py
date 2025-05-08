from typing import List, Type
from fastapi import Depends, HTTPException
from .repository import UserRepository
from .schema import User, UserCreate, UserLogin, UserLoginResponse, UpdateUserRole
from utils.jwt_auth import create_access_token, decode_token, ACCESS_TOKEN_EXPIRE_MINUTES
from datetime import timedelta
import bcrypt

class UserService:
    def __init__(self, user_repository: UserRepository = Depends()):
        self.user_repository = user_repository

    def list_users(self, skip: int = 0, max: int = 10) -> List[Type[User]]:
        return self.user_repository.all(skip=skip, max=max)

    def get_user(self, user_id: int) -> User:
        db_user = self.user_repository.find(user_id)
        if db_user is None:
            raise HTTPException(status_code=404, detail="Пользователь не найден")
        return db_user

    def registration(self, user: UserCreate) -> UserLoginResponse:
        db_user = self.user_repository.find_by_login(user.login)
        if db_user:
            raise HTTPException(status_code=409, detail="Логин занят")
        token_data = {"sub": user.login}
        access_token = create_access_token(data=token_data, expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
        db_user = self.user_repository.registration(user)
        return UserLoginResponse(
            id=db_user.id,
            login=user.login,
            fname=user.fname,
            lname=user.lname,
            sname=user.sname,
            token=access_token,
            role=db_user.role,
        )

    def login(self, user: UserLogin) -> UserLoginResponse:
        db_user = self.user_repository.find_by_login(user.login)
        if db_user is None or not bcrypt.checkpw(user.password.encode(), db_user.password.encode()):
            raise HTTPException(status_code=401, detail="Неверный логин или пароль")
        token_data = {
            "sub": user.login,
            "role": db_user.role.value
        }
        access_token = create_access_token(data=token_data,
                                           expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
        return UserLoginResponse(
            id=db_user.id,
            login=db_user.login,
            fname=db_user.fname,
            lname=db_user.lname,
            sname=db_user.sname,
            token=access_token,
            role=db_user.role.value
        )

    # Добавим метод для обновления роли пользователя
    def update_user_role(self, user_id: int, update_data: UpdateUserRole) -> User:
        db_user = self.user_repository.find(user_id)
        if db_user is None:
            raise HTTPException(status_code=404, detail="Пользователь не найден")

        # Обновляем роль
        db_user.role = update_data.role
        self.user_repository.db.commit()
        self.user_repository.db.refresh(db_user)

        return db_user

    def check_auth(self, token: str) -> UserLoginResponse:
        payload = decode_token(token)
        if payload is None:
            raise HTTPException(status_code=401, detail="Вы не авторизованы")
        login = payload.get("sub")
        db_user = self.user_repository.find_by_login(login)
        if db_user is None:
            raise HTTPException(status_code=401, detail="Пользователь не найден")
        print(db_user.role)
        return UserLoginResponse(
            id=db_user.id,
            login=db_user.login,
            fname=db_user.fname,
            lname=db_user.lname,
            sname=db_user.sname,
            token=token,
            role=db_user.role.value
        )