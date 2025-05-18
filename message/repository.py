from typing import List, Type, Optional
from fastapi.params import Depends
from sqlalchemy.orm import Session
from core.config.dependencies import get_db
from .model import Message
from datetime import datetime

class MessageRepository:
    def __init__(self, db: Session = Depends(get_db)):
        self.db = db

    def create(self, content: str, user_id: int, file_url: Optional[str] = None, file_name: Optional[str] = None) -> Message:
        message = Message(
            content=content,
            user_id=user_id,
            file_url=file_url,
            file_name=file_name
        )
        self.db.add(message)
        self.db.commit()
        self.db.refresh(message)
        return message

    def get_all_messages(self) -> List[Type[Message]]:
        return self.db.query(Message).filter(Message.is_deleted == False).order_by(Message.ts).all()

    def get_message(self, message_id: int) -> Optional[Message]:
        return self.db.query(Message).filter(Message.id == message_id).first()

    def update_message(self, message_id: int, content: str, is_edited: bool, edited_at: datetime) -> Message:
        message = self.get_message(message_id)
        if message:
            message.content = content
            message.is_edited = is_edited
            message.edited_at = edited_at
            self.db.commit()
            self.db.refresh(message)
        return message

    def delete_message(self, message_id: int) -> Message:
        message = self.get_message(message_id)
        if message:
            message.is_deleted = True
            self.db.commit()
            self.db.refresh(message)
        return message