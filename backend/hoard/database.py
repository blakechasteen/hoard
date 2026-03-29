"""Database connection and session management."""

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from hoard.config import load_config

_config = load_config()

_connect_args = {}
if _config.db.url.startswith("sqlite"):
    _connect_args["check_same_thread"] = False

engine = create_async_engine(_config.db.url, echo=False, connect_args=_connect_args)
async_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


async def get_db() -> AsyncSession:
    async with async_session() as session:
        yield session
