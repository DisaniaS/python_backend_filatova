import uvicorn
from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware

from core.config.database import Model, engine
from core.config.config import settings
from user.router import router as user_router


Model.metadata.create_all(bind=engine)

main_app = FastAPI()

main_app.include_router(user_router, prefix=settings.api.prefix)

main_app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

if __name__ == "__main__":
    uvicorn.run(
        "main:main_app",
        host=settings.run.host,
        port=settings.run.port,
        reload=True
    )
