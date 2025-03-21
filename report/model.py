from datetime import datetime
from sqlalchemy import Column, String, Integer, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from core.config.database import Model


class Report(Model):
   __tablename__ = "reports"
   id = Column(Integer, primary_key=True, autoincrement=True)
   ts = Column(DateTime, nullable=False, default=datetime.now())
   user_id = Column(Integer, ForeignKey("users.id"))
   number = Column(Integer, unique=True)
   path = Column(String)

   user = relationship("User", back_populates="reports")