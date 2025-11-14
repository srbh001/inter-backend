from __future__ import annotations

import os
import logging
from typing import AsyncGenerator, Optional

from sqlmodel import SQLModel, select
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import event
from sqlalchemy.engine import Connection

from utils.models import User  # ensure this imports all models or import the module

logger = logging.getLogger(__name__)

ENV = os.getenv("ENV", "dev").lower()

if ENV == "dev":
    DATABASE_URL = os.getenv("DATABASE_URL", "sqlite+aiosqlite:///./dev.db")
else:
    DATABASE_URL = os.getenv(
        "DATABASE_URL",
        "postgresql+asyncpg://postgres:password@localhost:5432/mydb",
    )

engine_kwargs = {
    "echo": True if ENV == "dev" else False,
    "pool_pre_ping": True if not ENV == "dev" else False,
}

connect_args = {}
if DATABASE_URL.startswith("sqlite"):
    connect_args = {"connect_args": {"check_same_thread": False}}
    engine_kwargs.update(connect_args)

engine = create_async_engine(DATABASE_URL, **engine_kwargs)

# after engine = create_async_engine(...)
logger.info("DATABASE_URL resolved to: %s", str(engine.url))

if DATABASE_URL.startswith("sqlite"):

    @event.listens_for(engine.sync_engine, "connect")
    def _sqlite_enable_foreign_keys(dbapi_connection, connection_record):
        try:
            cursor = dbapi_connection.cursor()
            cursor.execute("PRAGMA foreign_keys=ON")
            cursor.close()
        except Exception:
            logger.exception("Could not enable SQLite foreign keys PRAGMA")


# Async session factory
AsyncSessionLocal = sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False,
)


async def async_session() -> AsyncGenerator[AsyncSession, None]:
    """
    Use in routes:

        async with async_session() as session:
            ...

    or

        def route(session: AsyncSession = Depends(async_session)):
            ...
    """
    session: AsyncSession = AsyncSessionLocal()
    try:
        yield session
    finally:
        await session.close()


async def init_db() -> None:
    """
    Call at FastAPI startup (for development OR first deployment).
    For real production use Alembic migrations.
    """
    # Ensure all model modules imported before calling create_all()
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)
    logger.info("Database initialized (tables created if missing).")


# Convenience helpers
async def get_user_by_firebase_uid(
    session: AsyncSession, firebase_uid: str
) -> Optional[User]:
    stmt = select(User).where(User.firebase_uid == firebase_uid)
    result = await session.exec(stmt)
    return result.scalar_one_or_none()


async def get_user_by_id(session: AsyncSession, user_id: str) -> Optional[User]:
    stmt = select(User).where(User.id == user_id)
    result = await session.exec(stmt)
    return result.scalar_one_or_none()
