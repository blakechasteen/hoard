"""Price engine — orchestrates resolvers and produces composite appraisals."""

import logging

from hoard.config import PriceEngineConfig
from hoard.models import Item
from hoard.price_engine.composite import composite_value
from hoard.price_engine.protocols import PriceResolver, ResolverResult

logger = logging.getLogger(__name__)


class PriceEngine:
    def __init__(self, config: PriceEngineConfig):
        self.config = config
        self.resolvers: list[PriceResolver] = []

    def register(self, resolver: PriceResolver) -> None:
        rc = self.config.resolvers.get(resolver.name)
        if rc and rc.enabled:
            self.resolvers.append(resolver)
            logger.info(f"Registered resolver: {resolver.name}")
        else:
            logger.debug(f"Resolver {resolver.name} not enabled, skipping")

    async def appraise(self, item: Item) -> list[ResolverResult]:
        """Run all applicable resolvers against an item."""
        # Pinned value skips the engine
        if item.pinned_value is not None:
            return [ResolverResult(
                price=item.pinned_value,
                source="pinned",
                confidence=1.0,
                grade_specific=True,
            )]

        results: list[ResolverResult] = []
        for resolver in self.resolvers:
            if item.category not in resolver.categories:
                continue
            try:
                result = await resolver.resolve(item)
                if result:
                    results.append(result)
            except Exception as e:
                logger.warning(f"{resolver.name} failed for {item.name}: {e}")

        return results

    def composite(self, results: list[ResolverResult]) -> tuple[float, float] | None:
        """Compute composite valuation from resolver results."""
        return composite_value(
            results,
            source_trust=self.config.source_trust,
            decay_days=self.config.decay_days,
        )
