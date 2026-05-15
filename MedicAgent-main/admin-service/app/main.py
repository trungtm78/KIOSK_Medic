from fastapi import FastAPI, Request, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlmodel import SQLModel, Session, select
from pathlib import Path

from .core.cors import parse_cors_origins
from .core.db import get_engine, get_session
from .models import (
    KioskToken,
    Permission,
    Role,
    RolePermission,
    Tenant,
    TenantFeature,
    TenantQuota,
)
from .routers import api_v1
from .seed import seed_initial_data


TEMPLATES_DIR = Path(__file__).resolve().parent / "templates"
templates = Jinja2Templates(directory=str(TEMPLATES_DIR))


def create_app() -> FastAPI:
    app = FastAPI(title="Admin Service", version="0.1.0")

    app.add_middleware(
        CORSMiddleware,
        allow_origins=parse_cors_origins(),
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.on_event("startup")
    def _on_startup() -> None:
        # QA Bug #5 fix: use real Engine directly, not _LazyEngineProxy.
        # The proxy's __getattr__ caused QueuePool overflow on MySQL because
        # each attribute access could trigger new pool checkouts in some
        # SQLAlchemy internal paths.
        real_engine = get_engine()
        SQLModel.metadata.create_all(real_engine)
        with Session(real_engine) as s:
            seed_initial_data(s)

    # API routers
    app.include_router(api_v1.router, prefix="/v1", tags=["v1"])

    # W4.7 - Kiosk token management (CSO Finding #2)
    from .routers import kiosks
    app.include_router(kiosks.router, prefix="/v1", tags=["kiosks"])

    # Simple web views
    @app.get("/", response_class=HTMLResponse)
    def home(request: Request, session: Session = Depends(get_session)):
        tenants = session.exec(select(Tenant)).all()
        return templates.TemplateResponse("home.html", {"request": request, "tenants": tenants})

    @app.get("/tenants/{tenant_id}", response_class=HTMLResponse)
    def tenant_detail(tenant_id: int, request: Request, session: Session = Depends(get_session)):
        tenant = session.get(Tenant, tenant_id)
        if not tenant:
            return templates.TemplateResponse("not_found.html", {"request": request}, status_code=404)
        features = session.exec(select(TenantFeature).where(TenantFeature.tenant_id == tenant_id)).all()
        quotas = session.exec(select(TenantQuota).where(TenantQuota.tenant_id == tenant_id)).all()
        return templates.TemplateResponse(
            "tenant_detail.html",
            {"request": request, "tenant": tenant, "features": features, "quotas": quotas},
        )

    return app


app = create_app()
