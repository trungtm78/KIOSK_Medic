from fastapi import FastAPI

from .routers.v1.chat import router as chat_router


def create_app() -> FastAPI:
    app = FastAPI(title="BFF Service", version="0.1.0")
    app.include_router(chat_router, prefix="/v1")
    return app


app = create_app()

