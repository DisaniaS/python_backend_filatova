from pydantic import BaseModel
from .model import UserRole


class UserBase(BaseModel):
    login: str
    fname: str
    lname: str
    sname: str


class UserCreate(UserBase):
    password: str
    role: UserRole = UserRole.USER


class User(UserBase):
    id: int
    role: UserRole

    class Config:
        from_attributes = True

    @classmethod
    def from_attributes(cls, **kwargs):
        return cls(**kwargs)

    @property
    def is_admin(self):
        return self.role == UserRole.ADMIN


class UserLogin(BaseModel):
    login: str
    password: str


class UserLoginResponse(User):
    token: str
    role: str

    class Config:
        from_attributes = True


class UpdateUserRole(BaseModel):
    role: UserRole