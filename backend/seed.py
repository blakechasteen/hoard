"""Seed script — creates initial invite codes and optionally a test user."""

import asyncio
import secrets
import sys

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from hoard.database import async_session, engine
from hoard.models import Base, InviteCode


async def seed(count: int = 5):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with async_session() as db:
        codes = []
        for _ in range(count):
            code = secrets.token_urlsafe(8)
            db.add(InviteCode(code=code))
            codes.append(code)

        await db.commit()

    print(f"Created {count} invite codes:")
    for code in codes:
        print(f"  {code}")


if __name__ == "__main__":
    count = int(sys.argv[1]) if len(sys.argv) > 1 else 5
    asyncio.run(seed(count))
