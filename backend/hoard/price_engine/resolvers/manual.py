"""Manual resolver — always available, uses user-provided appraisals."""

from hoard.models import Item
from hoard.price_engine.protocols import ResolverResult


class ManualResolver:
    name = "manual"
    categories = ["pokemon", "sports", "mtg", "coins", "sealed", "apparel", "other"]

    async def resolve(self, item: Item) -> ResolverResult | None:
        # Manual resolver doesn't auto-fetch — it's populated by user input
        # through the appraisals endpoint. Returns None from the engine side.
        return None

    async def health(self) -> bool:
        return True
