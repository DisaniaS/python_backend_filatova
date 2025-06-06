import uvicorn
from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware

from core.config.database import Model, engine
from core.config.config import settings
from user.router import router as user_router
from report.router import router as report_router
from message.router import router as message_router
from inaccuracy.router import router as inaccuracy_router
from product.router import router as product_router

Model.metadata.create_all(bind=engine)

main_app = FastAPI()

main_app.include_router(user_router, prefix=settings.api.prefix)
main_app.include_router(report_router, prefix=settings.api.prefix)
main_app.include_router(message_router, prefix=settings.api.prefix)
main_app.include_router(inaccuracy_router, prefix=settings.api.prefix)
main_app.include_router(product_router, prefix=settings.api.prefix)

main_app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
)

if __name__ == "__main__":
    uvicorn.run(
        "main:main_app",
        host=settings.run.host,
        port=settings.run.port,
        reload=True
    )
