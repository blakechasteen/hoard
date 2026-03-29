"""Appraisals router — manual valuations and price history."""

from datetime import UTC, datetime, timedelta

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from hoard.auth import get_current_user
from hoard.database import get_db
from hoard.models import Appraisal, Item, User
from hoard.schemas import AppraisalCreate, AppraisalResponse

router = APIRouter(prefix="/items/{item_id}/appraisals", tags=["appraisals"])


@router.get("", response_model=list[AppraisalResponse])
async def list_appraisals(
    item_id: str,
    days: int = Query(default=365, ge=1, le=3650),
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    item_result = await db.execute(
        select(Item).where(Item.id == item_id, Item.owner_id == user.id)
    )
    if not item_result.scalar_one_or_none():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Item not found")

    since = datetime.now(UTC) - timedelta(days=days)
    result = await db.execute(
        select(Appraisal)
        .where(Appraisal.item_id == item_id, Appraisal.timestamp >= since)
        .order_by(Appraisal.timestamp.asc())
    )
    return result.scalars().all()


@router.post("", response_model=AppraisalResponse, status_code=status.HTTP_201_CREATED)
async def create_appraisal(
    item_id: str,
    req: AppraisalCreate,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    item_result = await db.execute(
        select(Item).where(Item.id == item_id, Item.owner_id == user.id)
    )
    if not item_result.scalar_one_or_none():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Item not found")

    appraisal = Appraisal(
        item_id=item_id,
        price=req.price,
        source=req.source,
        source_url=req.source_url,
        confidence=req.confidence,
        grade_specific=req.grade_specific,
    )
    db.add(appraisal)
    await db.commit()
    await db.refresh(appraisal)
    return appraisal
