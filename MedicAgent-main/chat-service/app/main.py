import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .routers.v1.chat import router as chat_router
from .routers.v1.debug import router as debug_router

_DEV_DEFAULT_ORIGINS = ["http://localhost:3000", "http://127.0.0.1:3000"]


def _parse_cors_origins() -> list[str]:
    raw = os.getenv("CORS_ORIGINS", "").strip()
    if not raw:
        return _DEV_DEFAULT_ORIGINS
    return [o.strip() for o in raw.split(",") if o.strip()]


def create_app() -> FastAPI:
    app = FastAPI(
        title="Chat Service",
        version="0.1.0",
        docs_url="/v1/chat/docs",
        openapi_url="/v1/chat/openapi.json",
    )
    app.add_middleware(
        CORSMiddleware,
        allow_origins=_parse_cors_origins(),
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.include_router(chat_router, prefix="/v1")
    app.include_router(debug_router, prefix="/v1")
    return app


app = create_app()
