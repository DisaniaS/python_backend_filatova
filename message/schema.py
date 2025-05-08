from pydantic import BaseModel
from datetime import datetime


class MessageBase(BaseModel):
    content: str


class MessageCreate(MessageBase):
    pass


class Message(MessageBase):
    id: int
    ts: str
    user_id: int

    class Config:
        from_attributes = True


class MessageResponse(Message):
    user_name: str
    user_role: str