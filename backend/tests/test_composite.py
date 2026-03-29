"""Unit tests for composite valuation — pure functions, no I/O."""

from datetime import UTC, datetime, timedelta

import pytest

from hoard.price_engine.composite import composite_value, weighted_median
from hoard.price_engine.protocols import ResolverResult


SOURCE_TRUST = {
    "tcgplayer": 0.9,
    "pricecharting": 0.85,
    "manual": 0.5,
}


def _result(price, source="tcgplayer", hours_ago=0, grade_specific=False):
    return ResolverResult(
        price=price,
        currency="USD",
        source=source,
        timestamp=datetime.now(UTC) - timedelta(hours=hours_ago),
        confidence=0.8,
        grade_specific=grade_specific,
    )


class TestWeightedMedian:
    def test_single_value(self):
        assert weighted_median([(100.0, 1.0)]) == 100.0

    def test_two_equal_weights(self):
        result = weighted_median([(50.0, 1.0), (150.0, 1.0)])
        assert result in (50.0, 150.0)  # median of 2 values

    def test_weighted_toward_heavier(self):
        result = weighted_median([(10.0, 0.1), (100.0, 10.0)])
        assert result == 100.0  # heavily weighted toward 100

    def test_empty(self):
        assert weighted_median([]) == 0.0

    def test_outlier_resistance(self):
        # One outlier shouldn't dominate
        result = weighted_median([
            (50.0, 1.0),
            (55.0, 1.0),
            (52.0, 1.0),
            (500.0, 0.5),  # outlier with lower weight
        ])
        assert result < 100  # median should resist the outlier


class TestCompositeValue:
    def test_single_result(self):
        results = [_result(100.0)]
        price, confidence = composite_value(results, SOURCE_TRUST)
        assert price == 100.0
        assert confidence > 0

    def test_multiple_sources(self):
        results = [
            _result(95.0, "tcgplayer"),
            _result(100.0, "pricecharting"),
            _result(90.0, "manual"),
        ]
        price, confidence = composite_value(results, SOURCE_TRUST)
        assert 85 < price < 105  # reasonable range

    def test_recency_decay(self):
        # Fresh result should have more weight than stale
        fresh = _result(100.0, "tcgplayer", hours_ago=1)
        stale = _result(50.0, "tcgplayer", hours_ago=24 * 80)  # 80 days old
        price, _ = composite_value([fresh, stale], SOURCE_TRUST, decay_days=90)
        assert price > 60  # should be closer to fresh value

    def test_grade_specific_bonus(self):
        generic = _result(80.0, "tcgplayer", grade_specific=False)
        specific = _result(120.0, "tcgplayer", grade_specific=True)
        price, _ = composite_value([generic, specific], SOURCE_TRUST)
        # Grade-specific gets 1.3x weight, so composite should lean toward 120
        assert price > 90

    def test_empty_results(self):
        assert composite_value([], SOURCE_TRUST) is None

    def test_all_stale_returns_none(self):
        # Results older than decay_days get 0 weight
        stale = _result(100.0, "tcgplayer", hours_ago=24 * 100)
        result = composite_value([stale], SOURCE_TRUST, decay_days=90)
        assert result is None

    def test_confidence_capped_at_one(self):
        results = [_result(100.0, "tcgplayer", grade_specific=True)]
        _, confidence = composite_value(results, SOURCE_TRUST)
        assert confidence <= 1.0
