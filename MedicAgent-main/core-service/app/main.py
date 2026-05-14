from pathlib import Path

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware

from app.directory.router import router as directory_router
from app.infolookup.router import router as info_router
from app.queue.router import router as queue_router
from app.maps.router import router as maps_router

app = FastAPI(
    title="Core Service",
    version="0.1.0",
    docs_url="/v1/core/docs",
    openapi_url="/v1/core/openapi.json",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(directory_router, prefix="/v1/directory", tags=["Directory"])

app.include_router(queue_router, prefix="/v1/queue", tags=["Queue"])

app.include_router(info_router, prefix="/v1/info", tags=["Info Lookup"])

app.include_router(maps_router, prefix="/v1/maps", tags=["Maps"])

knowledge_assets_dir = Path(__file__).resolve().parent / "knowledgebases"
app.mount(
    "/knowledge-assets",
    StaticFiles(directory=knowledge_assets_dir, html=False),
    name="knowledge-assets",
)


@app.get("/")
def read_root() -> dict[str, str]:
    return {"message": "Welcome to the Medic Core service!"}
