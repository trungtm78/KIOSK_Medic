from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .routers.v1.chat import router as chat_router
from .routers.v1.debug import router as debug_router


def create_app() -> FastAPI:
    app = FastAPI(
        title="Chat Service",
        version="0.1.0",
        docs_url="/v1/chat/docs",
        openapi_url="/v1/chat/openapi.json",
    )
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.include_router(chat_router, prefix="/v1")
    app.include_router(debug_router, prefix="/v1")
    return app


app = create_app()
