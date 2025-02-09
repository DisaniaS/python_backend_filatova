import uvicorn
from fastapi import FastAPI

from core.config.database import Model, engine
from core.config.config import settings
from user.router import router as user_router


Model.metadata.create_all(bind=engine)

main_app = FastAPI()

main_app.include_router(user_router)

if __name__ == "__main__":
    uvicorn.run(
        "main:main_app",
        host=settings.run.host,
        port=settings.run.port,
        reload=True
    )
