"""Composite valuation — merge multiple resolver results into one appraisal."""

from datetime import UTC, datetime

from hoard.price_engine.protocols import ResolverResult


def weighted_median(values_weights: list[tuple[float, float]]) -> float:
    """Weighted median, robust against outlier listings."""
    if not values_weights:
        return 0.0
    if len(values_weights) == 1:
        return values_weights[0][0]

    sorted_vw = sorted(values_weights, key=lambda vw: vw[0])
    total_weight = sum(w for _, w in sorted_vw)
    if total_weight == 0:
        return sorted_vw[len(sorted_vw) // 2][0]

    cumulative = 0.0
    for value, weight in sorted_vw:
        cumulative += weight
        if cumulative >= total_weight / 2:
            return value
    return sorted_vw[-1][0]


def composite_value(
    results: list[ResolverResult],
    source_trust: dict[str, float],
    decay_days: int = 90,
) -> tuple[float, float] | None:
    """Compute composite price and confidence from multiple resolver results.

    Returns (price, confidence) or None if no results.
    """
    if not results:
        return None

    now = datetime.now(UTC)
    weighted: list[tuple[float, float]] = []

    for r in results:
        age_days = (now - r.timestamp).total_seconds() / 86400
        recency = max(0.0, 1.0 - (age_days / decay_days))
        trust = source_trust.get(r.source, 0.5)
        grade_bonus = 1.3 if r.grade_specific else 1.0
        weight = recency * trust * grade_bonus
        if weight > 0:
            weighted.append((r.price, weight))

    if not weighted:
        return None

    price = weighted_median(weighted)
    confidence = max(w for _, w in weighted)

    return price, min(confidence, 1.0)
