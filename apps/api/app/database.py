"""
Database connection and session management.
إعداد محرك SQLAlchemy، وإدارة الجلسات، وتفعيل امتداد pgvector.
"""

import os
from typing import AsyncGenerator
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.models.base import Base

# الحصول على DATABASE_URL من متغيرات البيئة مع قيمة افتراضية للتطوير
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql+asyncpg://postgres:postgres_password@localhost:5432/career_copilot",
)

# التأكد من استخدام asyncpg درايفر عند الاتصال غير المتزامن
if DATABASE_URL.startswith("postgresql://"):
    DATABASE_URL = DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://", 1)

# إنشاء المحرك غير المتزامن (Async Engine)
engine = create_async_engine(
    DATABASE_URL,
    echo=os.getenv("SQL_ECHO", "False").lower() in ("true", "1"),
    future=True,
    pool_size=10,
    max_overflow=20,
    pool_pre_ping=True,
)

# مصنع جلسات قاعدة البيانات (AsyncSession Maker)
AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)


async def init_pgvector(conn):
    """تفعيل امتداد pgvector في PostgreSQL في حال لم يكن مفعلاً."""
    await conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Dependency injection للحصول على جلسة قاعدة بيانات في FastAPI routes."""
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


__all__ = ["engine", "AsyncSessionLocal", "get_db", "init_pgvector", "Base"]
