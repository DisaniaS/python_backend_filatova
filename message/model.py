from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from core.config.database import Model
from datetime import datetime


class Message(Model):
    __tablename__ = "messages"
    id = Column(Integer, primary_key=True, autoincrement=True)
    ts = Column(DateTime, default=datetime.now())
    content = Column(String)
    user_id = Column(Integer, ForeignKey("users.id"))
    is_edited = Column(Boolean, default=False)
    edited_at = Column(DateTime, nullable=True)
    file_url = Column(String, nullable=True)
    file_name = Column(String, nullable=True)
    is_deleted = Column(Boolean, default=False)

    user = relationship("User", foreign_keys=[user_id])