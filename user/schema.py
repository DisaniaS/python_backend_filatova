from pydantic import BaseModel

class UserBase(BaseModel):
    login: str
    fname: str
    lname: str
    sname: str



class UserCreate(UserBase):
    password: str

class User(UserBase):
    id: int
    is_admin: bool
    class Config:
        from_attributes = True

    @classmethod
    def from_attributes(cls, **kwargs):
        return cls(**kwargs)

class UserLogin(BaseModel):
    login: str
    password: str

class UserLoginResponse(User):
    token: str
    class Config:
        from_attributes = True