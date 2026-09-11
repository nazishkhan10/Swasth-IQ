import os
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import sqlalchemy

from app.core.config import settings
from app.database.session import engine
from app.database.base import Base

# Import router modules
from app.api.v1 import auth, users, upload, files, ocr, parser, health, validation, analysis, chat

from app.logs.logger import logger


# Base uploads path
UPLOADS_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "uploads"))
os.makedirs(UPLOADS_ROOT, exist_ok=True)


def _migrate_validated_medical_values():
    """
    Idempotent ALTER TABLE migration for new Phase 5 hardening columns.
    SQLite does not support ADD COLUMN IF NOT EXISTS, so we check PRAGMA first.
    """
    new_columns = [
        ("is_converted",      "BOOLEAN NOT NULL DEFAULT 0"),
        ("converted_value",   "FLOAT"),
        ("canonical_unit",    "VARCHAR(100)"),
        ("conversion_factor", "FLOAT"),
        ("ocr_confidence",    "FLOAT"),
        ("validation_trace",  "TEXT"),
    ]
    with engine.connect() as conn:
        result = conn.execute(sqlalchemy.text("PRAGMA table_info(validated_medical_values)"))
        existing = {row[1] for row in result.fetchall()}

        for col_name, col_def in new_columns:
            if col_name not in existing:
                try:
                    conn.execute(
                        sqlalchemy.text(
                            f"ALTER TABLE validated_medical_values ADD COLUMN {col_name} {col_def}"
                        )
                    )
                    conn.commit()
                    logger.info(f"Migration: added column '{col_name}' to validated_medical_values")
                except Exception as e:
                    logger.warning(f"Migration skipped for '{col_name}': {e}")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    FastAPI Lifespan Context Manager.
    Initializes database tables and verifies storage directories on startup.
    """
    logger.info("🚀 Starting Medical Report Analyzer backend application...")

    # Initialize SQLite tables automatically
    Base.metadata.create_all(bind=engine)

    # Phase 5 Hardening — add new columns to existing table if absent
    _migrate_validated_medical_values()

    # Ensure uploads directory structure exists
    os.makedirs(UPLOADS_ROOT, exist_ok=True)

    logger.info(f"✅ Database tables verified | Uploads dir: {UPLOADS_ROOT}")

    yield

    logger.info("🛑 Application shutting down...")


app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    lifespan=lifespan,
)

# ── CORS ─────────────────────────────────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Static file serving for uploads ──────────────────────────────────────────
app.mount("/uploads", StaticFiles(directory=str(UPLOADS_ROOT)), name="uploads")

# ── Routers ──────────────────────────────────────────────────────────────────
app.include_router(health.router, prefix="")
app.include_router(health.router, prefix=settings.API_V1_STR)
app.include_router(auth.router, prefix=settings.API_V1_STR)
app.include_router(users.router, prefix=settings.API_V1_STR)
app.include_router(upload.router, prefix=settings.API_V1_STR)
app.include_router(files.router, prefix=settings.API_V1_STR)
app.include_router(ocr.router, prefix=settings.API_V1_STR)
app.include_router(parser.router, prefix=settings.API_V1_STR)
app.include_router(validation.router, prefix=settings.API_V1_STR)
app.include_router(analysis.router, prefix=settings.API_V1_STR)
app.include_router(chat.router, prefix=settings.API_V1_STR)




@app.get("/")
def root():
    return {
        "message": "Welcome to Medical Report Analyzer API",
        "health": "/health",
        "docs": "/docs",
        "version": settings.VERSION,
        "phase": "5 — Medical Validation Engine",
    }
