from sqlalchemy import Column, String, Integer, Boolean
from sqlalchemy.orm import relationship

from core.config.database import Model


class User(Model):
   __tablename__ = "users"
   id = Column(Integer, primary_key=True, autoincrement=True)
   login = Column(String, unique=True, index=True)
   fname = Column(String)
   lname = Column(String)
   sname = Column(String, nullable=True)
   password = Column(String)
   is_admin = Column(Boolean, default=False, nullable=False)

   reports = relationship("Report", back_populates="user")