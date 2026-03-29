"""Auth router — register (with invite code) and login."""

from datetime import UTC, datetime

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from hoard.auth import create_token, get_current_user, hash_password, verify_password
from hoard.database import get_db
from hoard.models import InviteCode, User
from hoard.schemas import LoginRequest, RegisterRequest, TokenResponse, UserResponse

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
async def register(req: RegisterRequest, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(InviteCode).where(InviteCode.code == req.invite_code, InviteCode.used_by.is_(None))
    )
    invite = result.scalar_one_or_none()
    if not invite:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid or used invite code")

    existing = await db.execute(select(User).where(User.username == req.username))
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Username taken")

    user = User(
        username=req.username,
        display_name=req.display_name,
        password_hash=hash_password(req.password),
    )
    db.add(user)
    await db.flush()

    invite.used_by = user.id
    invite.used_at = datetime.now(UTC)

    await db.commit()
    await db.refresh(user)

    return TokenResponse(access_token=create_token(user.id))


@router.post("/login", response_model=TokenResponse)
async def login(req: LoginRequest, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).where(User.username == req.username))
    user = result.scalar_one_or_none()
    if not user or not verify_password(req.password, user.password_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Bad credentials")

    return TokenResponse(access_token=create_token(user.id))


@router.get("/me", response_model=UserResponse)
async def me(user: User = Depends(get_current_user)):
    return user
