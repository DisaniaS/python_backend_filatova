from typing import List, Type
from fastapi.params import Depends
from sqlalchemy.orm import Session
from core.config.dependencies import get_db
from .model import Message

class MessageRepository:
    def __init__(self, db: Session = Depends(get_db)):
        self.db = db

    def create(self, content: str, user_id: int) -> Message:
        db_message = Message(
            content=content,
            user_id=user_id
        )
        self.db.add(db_message)
        self.db.commit()
        self.db.refresh(db_message)
        return db_message

    def get_all_messages(self) -> List[Type[Message]]:
        return self.db.query(Message).order_by(Message.ts).all()