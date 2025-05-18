from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class MessageBase(BaseModel):
    content: str


class MessageCreate(MessageBase):
    pass


class MessageUpdate(MessageBase):
    pass


class Message(MessageBase):
    id: int
    ts: str
    user_id: int

    class Config:
        from_attributes = True


class MessageResponse(MessageBase):
    id: int
    user_id: int
    ts: str
    user_name: str
    user_role: str
    is_edited: bool = False
    edited_at: Optional[str] = None
    file_url: Optional[str] = None
    file_name: Optional[str] = None
    is_deleted: bool = False

    class Config:
        from_attributes = True