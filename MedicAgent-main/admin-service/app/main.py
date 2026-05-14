from fastapi import FastAPI, Request, Depends
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlmodel import SQLModel, Session, select
from pathlib import Path

from .models import Tenant, TenantFeature, TenantQuota, Role, Permission, RolePermission
from .seed import seed_initial_data
from .routers import api_v1
from .core.db import engine, get_session


TEMPLATES_DIR = Path(__file__).resolve().parent / "templates"
templates = Jinja2Templates(directory=str(TEMPLATES_DIR))


def create_app() -> FastAPI:
    app = FastAPI(title="Admin Service", version="0.1.0")

    @app.on_event("startup")
    def _on_startup() -> None:
        SQLModel.metadata.create_all(engine)
        with Session(engine) as s:
            seed_initial_data(s)

    # API routers
    app.include_router(api_v1.router, prefix="/v1", tags=["v1"]) 

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
