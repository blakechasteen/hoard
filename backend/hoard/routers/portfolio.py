"""Portfolio router — aggregate views and time series for charts."""

from datetime import UTC, datetime, timedelta

from fastapi import APIRouter, Depends, Query
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from hoard.auth import get_current_user
from hoard.database import get_db
from hoard.models import Appraisal, Item, User
from hoard.schemas import PortfolioSnapshot, PortfolioSummary

router = APIRouter(prefix="/portfolio", tags=["portfolio"])


@router.get("/summary", response_model=PortfolioSummary)
async def portfolio_summary(
    days: int = Query(default=365, ge=1, le=3650),
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    # Get all items with their latest appraisals
    items_result = await db.execute(
        select(Item).where(Item.owner_id == user.id)
    )
    items = items_result.scalars().all()

    total_value = 0.0
    total_cost = 0.0
    high_confidence_count = 0
    valued_items = 0

    for item in items:
        if item.purchase_price:
            total_cost += item.purchase_price

        if item.pinned_value is not None:
            total_value += item.pinned_value
            high_confidence_count += 1
            valued_items += 1
            continue

        # Get latest appraisal
        latest_result = await db.execute(
            select(Appraisal)
            .where(Appraisal.item_id == item.id)
            .order_by(Appraisal.timestamp.desc())
            .limit(1)
        )
        latest = latest_result.scalar_one_or_none()
        if latest:
            value = latest.composite_price or latest.price
            total_value += value
            valued_items += 1
            confidence = latest.composite_confidence or latest.confidence
            if confidence >= 0.7:
                high_confidence_count += 1

    total_gain = total_value - total_cost if total_cost > 0 else None
    gain_pct = (total_gain / total_cost * 100) if total_gain is not None and total_cost > 0 else None

    # Build history — daily snapshots of total portfolio value
    since = datetime.now(UTC) - timedelta(days=days)
    history = await _build_history(db, user.id, since)

    return PortfolioSummary(
        total_value=total_value if valued_items > 0 else None,
        total_cost=total_cost if total_cost > 0 else None,
        total_gain=total_gain,
        gain_pct=gain_pct,
        item_count=len(items),
        high_confidence_count=high_confidence_count,
        history=history,
    )


async def _build_history(
    db: AsyncSession, user_id, since: datetime
) -> list[PortfolioSnapshot]:
    """Build daily portfolio value snapshots from appraisal history.

    Groups appraisals by day, takes the latest per item per day,
    sums across all items to get daily portfolio value.
    """
    # Get all appraisals for user's items since the date
    result = await db.execute(
        select(Appraisal)
        .join(Item, Item.id == Appraisal.item_id)
        .where(Item.owner_id == user_id, Appraisal.timestamp >= since)
        .order_by(Appraisal.timestamp.asc())
    )
    appraisals = result.scalars().all()

    if not appraisals:
        return []

    # Build running state: latest value per item, snapshot daily
    item_values: dict[str, tuple[float, float]] = {}  # item_id -> (value, confidence)
    snapshots: list[PortfolioSnapshot] = []
    current_day = None

    for a in appraisals:
        day = a.timestamp.date()
        if current_day and day != current_day:
            # Emit snapshot for previous day
            if item_values:
                values = list(item_values.values())
                total = sum(v for v, _ in values)
                avg_conf = sum(c for _, c in values) / len(values)
                snapshots.append(PortfolioSnapshot(
                    timestamp=datetime.combine(current_day, datetime.min.time()),
                    total_value=total,
                    item_count=len(values),
                    confidence=avg_conf,
                ))

        current_day = day
        value = a.composite_price or a.price
        confidence = a.composite_confidence or a.confidence
        item_values[str(a.item_id)] = (value, confidence)

    # Final day
    if current_day and item_values:
        values = list(item_values.values())
        total = sum(v for v, _ in values)
        avg_conf = sum(c for _, c in values) / len(values)
        snapshots.append(PortfolioSnapshot(
            timestamp=datetime.combine(current_day, datetime.min.time()),
            total_value=total,
            item_count=len(values),
            confidence=avg_conf,
        ))

    return snapshots
