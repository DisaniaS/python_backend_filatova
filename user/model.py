from sqlalchemy import Column, String, Integer, Boolean, Enum
from sqlalchemy.orm import relationship

from core.config.database import Model
import enum

class UserRole(str, enum.Enum):
    ADMIN = "Администратор"
    ENG_1 = "Инженер 1 категории"
    ENG_2 = "Инженер 2 категории"
    ENG_3 = "Инженер 3 категории"
    ENG_TEST_3 = "Инженер - испытатель 3 категории"
    LEAD_ENG = "Ведущий инженер"
    USER = "Пользователь"

class User(Model):
   __tablename__ = "users"
   id = Column(Integer, primary_key=True, autoincrement=True)
   login = Column(String, unique=True, index=True)
   fname = Column(String)
   lname = Column(String)
   sname = Column(String, nullable=True)
   password = Column(String)
   role = Column(Enum(UserRole), default=UserRole.USER, nullable=False)

   reports = relationship("Report", back_populates="user")

   @property
   def is_admin(self):
       return self.role == UserRole.ADMIN