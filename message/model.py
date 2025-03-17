from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from core.config.database import Model
from datetime import datetime


class Message(Model):
    __tablename__ = "messages"
    id = Column(Integer, primary_key=True, autoincrement=True)
    ts = Column(DateTime, default=datetime.now())
    content = Column(String)
    user_id = Column(Integer, ForeignKey("users.id"))

    user = relationship("User", foreign_keys=[user_id])