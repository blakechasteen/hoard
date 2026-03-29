"""PriceCharting resolver — covers trading cards, sealed product, games."""

import logging

import httpx

from hoard.models import Item
from hoard.price_engine.protocols import ResolverResult

logger = logging.getLogger(__name__)

PRICECHARTING_BASE = "https://www.pricecharting.com/api"


class PriceChartingResolver:
    name = "pricecharting"
    categories = ["pokemon", "sports", "mtg", "sealed", "other"]

    def __init__(self, api_key: str):
        self.api_key = api_key

    def _search_query(self, item: Item) -> str:
        if item.search_override:
            return item.search_override
        parts = [item.name]
        if item.grade and item.grade != "raw":
            parts.append(item.grade)
        return " ".join(parts)

    async def resolve(self, item: Item) -> ResolverResult | None:
        query = self._search_query(item)
        try:
            async with httpx.AsyncClient(timeout=15) as client:
                resp = await client.get(
                    f"{PRICECHARTING_BASE}/products",
                    params={"t": self.api_key, "q": query, "type": "prices"},
                )
                resp.raise_for_status()
                data = resp.json()

            if not data or "products" not in data:
                return None

            products = data["products"]
            if not products:
                return None

            # Take the first match — PriceCharting ranks by relevance
            product = products[0]
            price_key = self._price_key(item)
            price = product.get(price_key) or product.get("price")
            if not price:
                return None

            # PriceCharting returns prices in cents
            price_dollars = price / 100.0

            return ResolverResult(
                price=price_dollars,
                currency="USD",
                source=self.name,
                url=product.get("url"),
                confidence=0.85,
                grade_specific=bool(item.grade and item.grade != "raw"),
            )
        except httpx.HTTPError as e:
            logger.warning(f"PriceCharting API error: {e}")
            return None

    def _price_key(self, item: Item) -> str:
        """Map grade to PriceCharting's price field names."""
        if not item.grade or item.grade == "raw":
            return "loose-price"
        grade = item.grade.upper()
        if "PSA 10" in grade or "GEM" in grade:
            return "graded-price"
        if "PSA 9" in grade:
            return "psa-9-price"
        return "graded-price"

    async def health(self) -> bool:
        try:
            async with httpx.AsyncClient(timeout=5) as client:
                resp = await client.get(
                    f"{PRICECHARTING_BASE}/products",
                    params={"t": self.api_key, "q": "test"},
                )
                return resp.status_code == 200
        except Exception:
            return False
