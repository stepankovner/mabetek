import hashlib
import json
from uuid import UUID
from fastapi import FastAPI, Header, HTTPException, Request
from fastapi.responses import JSONResponse
from sqlalchemy import create_engine, select, text
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.orm import sessionmaker
from .admin import attach_admin
from .config import Settings
from .models import Lead, Notification, Rental
from .schemas import Kind, LeadInput, RentalOutput
from .security import rate_allowed

def create_app(settings: Settings | None = None, engine=None) -> FastAPI:
    settings = settings or Settings()
    engine = engine or create_engine(settings.database_url, pool_pre_ping=True)
    sessions = sessionmaker(engine, expire_on_commit=False)
    app = FastAPI(title="Мабетэк API", docs_url=None, redoc_url=None, openapi_url=None)

    @app.middleware("http")
    async def security_headers(request: Request, call_next):
        if request.method not in {"GET", "HEAD", "OPTIONS"}:
            origin = request.headers.get("origin")
            if (request.url.path.startswith("/admin") and origin != settings.public_origin) or (origin and origin != settings.public_origin):
                return JSONResponse({"detail": "Origin not allowed"}, status_code=403)
        size = request.headers.get("content-length", "0")
        if not size.isdigit() or int(size) > 65536:
            return JSONResponse({"detail": "Request too large"}, status_code=413)
        response = await call_next(request)
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        if request.url.path.startswith(("/admin", "/api/leads")):
            response.headers["Cache-Control"] = "no-store"
        return response

    @app.get("/api/health/ready")
    def ready():
        try:
            with engine.connect() as connection:
                connection.execute(text("SELECT 1"))
        except SQLAlchemyError:
            raise HTTPException(503, "Database unavailable") from None
        return {"status": "ok"}

    @app.get("/api/config")
    def public_config():
        return {"leads_enabled": settings.leads_enabled, "privacy_version": settings.privacy_version}

    @app.get("/api/rentals", response_model=list[RentalOutput])
    def rentals(kind: Kind | None = None, available: bool | None = None):
        stmt = select(Rental).where(Rental.published.is_(True))
        if kind:
            stmt = stmt.where(Rental.kind == kind)
        if available is not None:
            stmt = stmt.where(Rental.available == available)
        with sessions() as db:
            return db.scalars(stmt.order_by(Rental.id)).all()

    @app.get("/api/rentals/{slug}", response_model=RentalOutput)
    def rental(slug: str):
        with sessions() as db:
            item = db.scalar(select(Rental).where(Rental.slug == slug, Rental.published.is_(True)))
            if not item:
                raise HTTPException(404, "Rental not found")
            return item

    @app.post("/api/leads", status_code=201)
    def create_lead(payload: LeadInput, request: Request, idempotency_key: UUID = Header()):
        if not settings.leads_enabled:
            raise HTTPException(503, "Lead collection is disabled")
        key = str(idempotency_key)
        digest = hashlib.sha256(json.dumps(payload.model_dump(), sort_keys=True, ensure_ascii=False).encode()).hexdigest()
        def existing_result(lead):
            if lead.payload_hash != digest:
                raise HTTPException(409, "Idempotency key already used for a different request")
            return {"id": lead.id}
        with sessions() as db:
            existing = db.scalar(select(Lead).where(Lead.idempotency_key == key))
            if existing:
                return existing_result(existing)
        address = request.client.host if request.client else "unknown"
        if not rate_allowed(sessions, settings.secret_key, "lead", address, settings.lead_limit):
            raise HTTPException(429, "Too many requests", headers={"Retry-After": "3600"})
        with sessions() as db:
            lead = Lead(**payload.model_dump(exclude={"consent"}), idempotency_key=key,
                payload_hash=digest, privacy_version=settings.privacy_version)
            try:
                db.add(lead)
                db.flush()
                db.add(Notification(lead_id=lead.id))
                db.commit()
            except IntegrityError:
                db.rollback()
                existing = db.scalar(select(Lead).where(Lead.idempotency_key == key))
                if existing:
                    return existing_result(existing)
                raise
            return {"id": lead.id}

    attach_admin(app, engine, sessions, settings)
    return app
