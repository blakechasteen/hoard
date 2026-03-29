"""Test fixtures — in-memory SQLite, test client, auth helpers."""

import secrets

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from hoard.models import Base, InviteCode, User
from hoard.auth import create_token, hash_password
from hoard.database import get_db
from hoard.main import app


@pytest_asyncio.fixture
async def db_session(tmp_path):
    """Create a fresh in-memory SQLite database for each test."""
    db_path = tmp_path / "test.db"
    url = f"sqlite+aiosqlite:///{db_path}"
    engine = create_async_engine(url, connect_args={"check_same_thread": False})

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    session_factory = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async with session_factory() as session:
        yield session

    await engine.dispose()


@pytest_asyncio.fixture
async def client(db_session):
    """Test client with DB override."""
    async def _override_db():
        yield db_session

    app.dependency_overrides[get_db] = _override_db

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as c:
        yield c

    app.dependency_overrides.clear()


@pytest_asyncio.fixture
async def test_user(db_session) -> User:
    """Create a test user."""
    user = User(
        username="testuser",
        display_name="Test User",
        password_hash=hash_password("testpass123"),
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return user


@pytest_asyncio.fixture
async def auth_headers(test_user) -> dict:
    """Auth headers for the test user."""
    token = create_token(test_user.id)
    return {"Authorization": f"Bearer {token}"}


@pytest_asyncio.fixture
async def invite_code(db_session) -> str:
    """Create an unused invite code."""
    code = secrets.token_urlsafe(8)
    db_session.add(InviteCode(code=code))
    await db_session.commit()
    return code
