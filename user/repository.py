from typing import List, Type

from fastapi.params import Depends
from sqlalchemy.orm import Session

from core.config.dependencies import get_db
from user.schema import UserCreate
from user.model import User

import bcrypt


class UserRepository:
    def __init__(self, db: Session = Depends(get_db)):
        self.db = db

    def find(self, id: int):
        query = self.db.query(User)
        return query.filter(User.id == id).first()

    def find_by_login(self, login: str):
        query = self.db.query(User)
        return query.filter(User.login == login).first()

    def all(self, skip: int = 0, max: int = 100) -> List[Type[User]]:
        query = self.db.query(User)
        return query.offset(skip).limit(max).all()

    def registration(self, user: UserCreate) -> User:
        hashed_password = bcrypt.hashpw(user.password.encode(), bcrypt.gensalt())

        db_user = User(
            login=user.login,
            fname=user.fname,
            lname=user.lname,
            sname=user.sname,
            password=hashed_password.decode()
        )

        self.db.add(db_user)
        self.db.commit()
        self.db.refresh(db_user)

        return db_user