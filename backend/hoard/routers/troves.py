"""Troves router — user-defined groupings for portfolio slicing."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from hoard.auth import get_current_user
from hoard.database import get_db
from hoard.models import Item, Trove, TroveMembership, User
from hoard.schemas import TroveCreate, TroveResponse

router = APIRouter(prefix="/troves", tags=["troves"])


@router.get("", response_model=list[TroveResponse])
async def list_troves(
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    result = await db.execute(
        select(Trove)
        .where(Trove.owner_id == user.id)
        .options(selectinload(Trove.memberships))
        .order_by(Trove.created_at.desc())
    )
    troves = result.scalars().all()

    return [
        TroveResponse(
            id=t.id,
            name=t.name,
            description=t.description,
            created_at=t.created_at,
            item_count=len(t.memberships),
        )
        for t in troves
    ]


@router.post("", response_model=TroveResponse, status_code=status.HTTP_201_CREATED)
async def create_trove(
    req: TroveCreate,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    trove = Trove(owner_id=user.id, name=req.name, description=req.description)
    db.add(trove)
    await db.flush()

    added = 0
    for item_id in req.item_ids:
        item_result = await db.execute(
            select(Item).where(Item.id == str(item_id), Item.owner_id == user.id)
        )
        if item_result.scalar_one_or_none():
            db.add(TroveMembership(trove_id=trove.id, item_id=str(item_id)))
            added += 1

    await db.commit()
    await db.refresh(trove)

    return TroveResponse(
        id=trove.id,
        name=trove.name,
        description=trove.description,
        created_at=trove.created_at,
        item_count=added,
    )


@router.post("/{trove_id}/items/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
async def add_item_to_trove(
    trove_id: str,
    item_id: str,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    trove_result = await db.execute(select(Trove).where(Trove.id == trove_id, Trove.owner_id == user.id))
    if not trove_result.scalar_one_or_none():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Trove not found")

    item_result = await db.execute(select(Item).where(Item.id == item_id, Item.owner_id == user.id))
    if not item_result.scalar_one_or_none():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Item not found")

    existing = await db.execute(
        select(TroveMembership).where(
            TroveMembership.trove_id == trove_id, TroveMembership.item_id == item_id
        )
    )
    if existing.scalar_one_or_none():
        return

    db.add(TroveMembership(trove_id=trove_id, item_id=item_id))
    await db.commit()


@router.delete("/{trove_id}/items/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_item_from_trove(
    trove_id: str,
    item_id: str,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    result = await db.execute(
        select(TroveMembership).where(
            TroveMembership.trove_id == trove_id, TroveMembership.item_id == item_id
        )
    )
    membership = result.scalar_one_or_none()
    if membership:
        await db.delete(membership)
        await db.commit()
