"""Auth utilities — JWT tokens and password hashing."""

from datetime import UTC, datetime, timedelta

import bcrypt
import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from hoard.config import load_config
from hoard.database import get_db
from hoard.models import User

_config = load_config()
_security = HTTPBearer()


def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()


def verify_password(password: str, hashed: str) -> bool:
    return bcrypt.checkpw(password.encode(), hashed.encode())


def create_token(user_id: str) -> str:
    expire = datetime.now(UTC) + timedelta(minutes=_config.auth.token_expire_minutes)
    payload = {"sub": user_id, "exp": expire}
    return jwt.encode(payload, _config.auth.secret_key, algorithm=_config.auth.algorithm)


def decode_token(token: str) -> str:
    try:
        payload = jwt.decode(token, _config.auth.secret_key, algorithms=[_config.auth.algorithm])
        return payload["sub"]
    except (jwt.ExpiredSignatureError, jwt.InvalidTokenError, KeyError) as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token") from e


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(_security),
    db: AsyncSession = Depends(get_db),
) -> User:
    user_id = decode_token(credentials.credentials)
    result = await db.execute(select(User).where(User.id == user_id, User.is_active.is_(True)))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")
    return user
