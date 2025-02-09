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

    class Config:
        from_attributes = True

    @classmethod
    def from_attributes(cls, **kwargs):
        return cls(**kwargs)