"""Price resolver protocol — the contract all resolvers implement."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime
from typing import Protocol, runtime_checkable

from hoard.models import Item


@dataclass(frozen=True)
class ResolverResult:
    price: float
    currency: str
    source: str
    url: str | None = None
    timestamp: datetime = None
    confidence: float = 0.5
    grade_specific: bool = False

    def __post_init__(self):
        if self.timestamp is None:
            object.__setattr__(self, "timestamp", datetime.now(UTC))


@runtime_checkable
class PriceResolver(Protocol):
    name: str
    categories: list[str]

    async def resolve(self, item: Item) -> ResolverResult | None:
        """Return a price for the item, or None if unable to resolve."""
        ...

    async def health(self) -> bool:
        """Check if the resolver is operational."""
        ...
