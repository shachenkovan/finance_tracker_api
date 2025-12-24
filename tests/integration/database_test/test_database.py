import pytest
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy import text


@pytest.mark.asyncio
async def test_database_connection():
    """
    Тест базового подключения к БД.
    """
    engine = create_async_engine(
        "sqlite+aiosqlite:///:memory:",
        echo=False
    )

    try:
        async with engine.connect() as conn:
            result = await conn.execute(text("SELECT 1"))
            value = result.scalar()

            assert value == 1

        async with AsyncSession(engine) as session:
            assert session.is_active

            result = await session.execute(text("SELECT 2"))
            value = result.scalar()

            assert value == 2
    finally:
        await engine.dispose()


@pytest.mark.asyncio
async def test_database_schema_creation():
    """
    Тест создания схемы БД.
    """
    from database.database import Base

    engine = create_async_engine(
        "sqlite+aiosqlite:///:memory:",
        echo=False
    )

    try:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

        async with engine.connect() as conn:
            result = await conn.execute(
                text("SELECT name FROM sqlite_master WHERE type='table'")
            )
            tables = [row[0] for row in result.fetchall()]

            expected_tables = [
                'users', 'categories', 'budgets',
                'goals', 'wallets', 'transactions'
            ]

            for table in expected_tables:
                assert table in tables
    finally:
        await engine.dispose()