"""Tests for sunsynk.utils.stats."""

import math

import pytest

from sunsynk.utils.stats import percentile


@pytest.mark.parametrize(
    ("bad_p",),
    [(-1,), (101,)],
)
def test_percentile_invalid_range(bad_p: int) -> None:
    """Percentile must be 0..100 inclusive."""
    with pytest.raises(ValueError, match="between 0 and 100"):
        percentile([1.0, 2.0, 3.0], bad_p)


def test_percentile_endpoints() -> None:
    """0 and 100 return min and max."""
    data = [3.0, 1.0, 2.0]
    assert percentile(data, 0) == 1.0
    assert percentile(data, 100) == 3.0


def test_percentile_single_element() -> None:
    """One value: any valid percentile returns that value."""
    assert percentile([42.0], 0) == 42.0
    assert percentile([42.0], 50) == 42.0
    assert percentile([42.0], 100) == 42.0


def test_percentile_two_elements_median() -> None:
    """Linear interpolation between two ranks."""
    assert percentile([10.0, 20.0], 50) == pytest.approx(15.0)


def test_percentile_sorted_order_irrelevant() -> None:
    """Input order does not matter (data is sorted internally)."""
    assert percentile([4.0, 1.0, 3.0, 2.0], 50) == percentile([1.0, 2.0, 3.0, 4.0], 50)


def test_percentile_known_quartiles() -> None:
    """Spot-check interpolation on a short sequence."""
    data = [0.0, 10.0, 20.0, 30.0, 40.0]
    assert percentile(data, 25) == pytest.approx(10.0)
    assert percentile(data, 50) == pytest.approx(20.0)
    assert percentile(data, 75) == pytest.approx(30.0)


def test_percentile_accepts_non_list_iterable() -> None:
    """Iterable does not need to be a list."""
    assert percentile((1.0, 2.0, 3.0), 50) == 2.0
    assert percentile(range(5), 50) == 2.0


def test_percentile_quarter_between_two_values() -> None:
    """25th percentile between 0 and 100 is 25."""
    assert math.isclose(percentile([0.0, 100.0], 25), 25.0)
