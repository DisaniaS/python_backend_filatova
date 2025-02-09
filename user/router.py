from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import parse_obj_as
from typing import List
from uuid import UUID

from user.schema import User, UserCreate
from user.repository import UserRepository


router = APIRouter(prefix="/users", tags=["users"])


@router.get("/", response_model=List[User])
def list_users(skip: int = 0, max: int = 10, users: UserRepository = Depends()):
    db_users = users.all(skip=skip, max=max)
    return parse_obj_as(List[User], db_users)


@router.post("/", response_model=User, status_code=status.HTTP_201_CREATED)
def store_user(user: UserCreate, users: UserRepository = Depends()):
    db_user = users.find_by_login(login=user.login)

    if db_user:
        raise HTTPException(
            status_code=400,
            detail="Логин занят"
        )

    db_user = users.create(user)
    return User.from_orm(db_user)


@router.get("/{user_id}", response_model=User)
def get_speedster(user_id: int, users: UserRepository = Depends()):
    db_user = users.find(user_id)

    if db_user is None:
        raise HTTPException(
            status_code=404,
            detail="Пользователь не найден"
        )

    return User.from_orm(db_user)