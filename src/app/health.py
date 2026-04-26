from fastapi import APIRouter, HTTPException, status
from sqlalchemy import text

from app.dependencies import engine, redis_client

router = APIRouter()


@router.get("/health", tags=["system"])
async def health():
    return {"status": "alive"}


@router.get("/ready", status_code=status.HTTP_200_OK, tags=["system"])
async def readiness():
    try:
        async with engine.connect() as conn:
            await conn.execute(text("SELECT 1"))
        await redis_client.ping()
        return {"status": "ready", "database": "ok", "redis": "ok"}
    except Exception as e:
        raise HTTPException(  # noqa: B904
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail={"status": "not_ready", "error": str(e)},
        )
