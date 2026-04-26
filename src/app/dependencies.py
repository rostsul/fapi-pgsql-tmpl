from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

import redis.asyncio as redis
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.config import settings

engine = create_async_engine(
    settings.DATABASE_URL,
    echo=settings.APP_ENV != "production",
    pool_size=5,
    max_overflow=10,
)
async_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
redis_client = redis.from_url(settings.REDIS_URL, decode_responses=True)


@asynccontextmanager
async def get_db() -> AsyncGenerator[AsyncSession]:
    session = async_session()
    try:
        yield session
        await session.commit()
    except Exception:
        await session.rollback()
        raise
    finally:
        await session.close()
