from sqlalchemy.orm import sessionmaker
from sqlmodel.ext.asyncio.session import AsyncSession

from app.config import Config
from sqlalchemy.ext.asyncio import create_async_engine
import psycopg
from pgvector.psycopg import register_vector

database_url = Config.DATABASE_URL_ASYNCPG_DRIVER

engine = create_async_engine(database_url, future=True)

AsyncSessionLocal = sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


async def get_session() -> AsyncSession:
    async with AsyncSessionLocal() as session:
        yield session

        await session.rollback()


def get_conn():
    conn = psycopg.connect(dbname=database_url, autocommit=True)
    register_vector(conn)
    return conn
