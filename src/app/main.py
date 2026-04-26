import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from prometheus_fastapi_instrumentator import Instrumentator

from app.config import settings
from app.health import router as health_router
from app.middleware.security import security_middleware

# from app.routers.items import router as items_router
from app.utils.logging import setup_logging


@asynccontextmanager
async def lifespan(app: FastAPI):
    setup_logging()
    logger: logging.Logger = logging.getLogger("app")
    logger.info("Application starting up")
    yield
    logger.info("Application shutting down")


app = FastAPI(
    title="FastAPI CRUD Template",
    version="0.1.0",
    lifespan=lifespan,
    docs_url="/docs" if not settings.is_prod else None,
    redoc_url="/redoc" if not settings.is_prod else None,
)

app.add_middleware(
    CORSMiddleware, allow_origins=settings.CORS_ORIGINS, allow_methods=["*"], allow_headers=["*"]
)
app.middleware("http")(security_middleware)

app.include_router(health_router, prefix="")
# app.include_router(items_router, prefix="/api/v1/items", tags=["items"])

Instrumentator().instrument(app).expose(
    app, endpoint="/metrics", include_in_schema=False, tags=["system"]
)
