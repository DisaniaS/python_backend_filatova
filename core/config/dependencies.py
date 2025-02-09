from functools import lru_cache

from sqlalchemy.orm import Session

from core.config.config import settings
from . import database

def get_db() -> Session:
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()

@lru_cache
def get_db_settings() -> settings.db:
    return settings.db