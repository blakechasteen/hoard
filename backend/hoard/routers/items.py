"""Items router — CRUD for collection items."""

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from hoard.auth import get_current_user
from hoard.database import get_db
from hoard.models import Appraisal, Item, User
from hoard.schemas import ItemCreate, ItemResponse, ItemUpdate

router = APIRouter(prefix="/items", tags=["items"])


def _enrich_response(item: Item, latest_appraisal: Appraisal | None) -> ItemResponse:
    current_value = None
    current_confidence = None
    value_change_pct = None

    if item.pinned_value is not None:
        current_value = item.pinned_value
        current_confidence = 1.0
    elif latest_appraisal:
        current_value = latest_appraisal.composite_price or latest_appraisal.price
        current_confidence = latest_appraisal.composite_confidence or latest_appraisal.confidence

    if current_value and item.purchase_price and item.purchase_price > 0:
        value_change_pct = ((current_value - item.purchase_price) / item.purchase_price) * 100

    return ItemResponse(
        id=item.id,
        name=item.name,
        category=item.category,
        description=item.description,
        grade=item.grade,
        purchase_price=item.purchase_price,
        purchase_date=item.purchase_date,
        catalog_ref=item.catalog_ref,
        tags=item.tags or [],
        metadata=item.metadata_ or {},
        photos=item.photos or [],
        pinned_value=item.pinned_value,
        search_override=item.search_override,
        created_at=item.created_at,
        current_value=current_value,
        current_confidence=current_confidence,
        value_change_pct=value_change_pct,
    )


@router.get("", response_model=list[ItemResponse])
async def list_items(
    category: str | None = Query(None),
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    query = (
        select(Item)
        .where(Item.owner_id == user.id)
        .options(selectinload(Item.appraisals))
        .order_by(Item.created_at.desc())
    )
    if category:
        query = query.where(Item.category == category)

    result = await db.execute(query)
    items = result.scalars().all()

    responses = []
    for item in items:
        latest = max(item.appraisals, key=lambda a: a.timestamp, default=None) if item.appraisals else None
        responses.append(_enrich_response(item, latest))
    return responses


@router.post("", response_model=ItemResponse, status_code=status.HTTP_201_CREATED)
async def create_item(
    req: ItemCreate,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    item = Item(
        owner_id=user.id,
        name=req.name,
        category=req.category,
        description=req.description,
        grade=req.grade,
        purchase_price=req.purchase_price,
        purchase_date=req.purchase_date,
        catalog_ref=req.catalog_ref,
        tags=req.tags,
        metadata_=req.metadata,
        search_override=req.search_override,
    )
    db.add(item)
    await db.commit()
    await db.refresh(item)
    return _enrich_response(item, None)


@router.get("/{item_id}", response_model=ItemResponse)
async def get_item(
    item_id: str,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    result = await db.execute(
        select(Item)
        .where(Item.id == item_id, Item.owner_id == user.id)
        .options(selectinload(Item.appraisals))
    )
    item = result.scalar_one_or_none()
    if not item:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Item not found")

    latest = max(item.appraisals, key=lambda a: a.timestamp, default=None) if item.appraisals else None
    return _enrich_response(item, latest)


@router.patch("/{item_id}", response_model=ItemResponse)
async def update_item(
    item_id: str,
    req: ItemUpdate,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    result = await db.execute(
        select(Item).where(Item.id == item_id, Item.owner_id == user.id)
    )
    item = result.scalar_one_or_none()
    if not item:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Item not found")

    update_data = req.model_dump(exclude_unset=True)
    if "metadata" in update_data:
        update_data["metadata_"] = update_data.pop("metadata")
    for field, value in update_data.items():
        setattr(item, field, value)

    await db.commit()
    await db.refresh(item)
    return _enrich_response(item, None)


@router.delete("/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_item(
    item_id: str,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    result = await db.execute(
        select(Item).where(Item.id == item_id, Item.owner_id == user.id)
    )
    item = result.scalar_one_or_none()
    if not item:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Item not found")

    await db.delete(item)
    await db.commit()
