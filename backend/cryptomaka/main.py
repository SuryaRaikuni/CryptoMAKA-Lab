"""
CryptoMAKA Lab — FastAPI application entry point.
"""

from __future__ import annotations

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from cryptomaka.config import get_settings
from cryptomaka.database import create_tables, check_db_connection
from cryptomaka.api import (
    routes_health,
    routes_protocols,
    routes_security,
    routes_benchmarks,
    routes_experiments,
    routes_quantum,
)

settings = get_settings()

logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO),
    format="%(asctime)s %(name)s %(levelname)s %(message)s",
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(application: FastAPI):
    logger.info("CryptoMAKA Lab starting (env=%s)", settings.APP_ENV)
    try:
        create_tables()
        logger.info("Database tables verified/created.")
    except Exception as exc:
        logger.error("Database initialization failed: %s", exc)
    yield
    logger.info("CryptoMAKA Lab shutting down.")


app = FastAPI(
    title="CryptoMAKA Lab API",
    description=(
        "Cybersecurity research platform for cloud-IoT mutual authentication and key agreement. "
        "Implements the Ju-Park (Sensors 2023) MAKA protocol alongside an ECC/ECDH counterpart "
        "and a proposed reduced-round-trip extension."
    ),
    version=settings.APP_VERSION,
    lifespan=lifespan,
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json",
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list if settings.is_production else ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Global exception handler (never expose stack traces in production)
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error("Unhandled exception on %s: %s", request.url.path, exc, exc_info=True)
    if settings.is_production:
        return JSONResponse(
            status_code=500,
            content={"detail": "Internal server error. Please try again."},
        )
    return JSONResponse(
        status_code=500,
        content={"detail": str(exc)},
    )


# Mount all routers under /api/v1
PREFIX = "/api/v1"

app.include_router(routes_health.router, prefix=PREFIX)
app.include_router(routes_protocols.router, prefix=PREFIX)
app.include_router(routes_security.router, prefix=PREFIX)
app.include_router(routes_benchmarks.router, prefix=PREFIX)
app.include_router(routes_experiments.router, prefix=PREFIX)
app.include_router(routes_quantum.router, prefix=PREFIX)
