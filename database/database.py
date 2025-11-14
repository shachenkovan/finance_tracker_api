from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from config import DB_URL

async_engine = create_async_engine(url=DB_URL)
async_session = async_sessionmaker(bind=async_engine, expire_on_commit=False)


class Base(DeclarativeBase):
    pass


async def get_db():
    db = async_session()
    try:
        yield db
    finally:
        await db.close()
