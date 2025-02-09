from sqlalchemy import Column, String, Integer

from core.config.database import Model


class User(Model):
   __tablename__ = "users"
   id = Column(Integer, primary_key=True, autoincrement=True)
   login = Column(String, unique=True, index=True)
   fname = Column(String)
   lname = Column(String)
   sname = Column(String)
   password = Column(String)
