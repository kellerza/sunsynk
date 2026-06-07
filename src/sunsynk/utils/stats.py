"""Statistics utilities."""

from collections.abc import Iterable


def percentile(data: Iterable[float], percentile: int) -> float:
    """Calculate the given percentile of the data."""
    if not (0 <= percentile <= 100):
        raise ValueError("Percentile must be between 0 and 100.")

    # Sort the data
    sorted_data = sorted(data)
    n = len(sorted_data)

    # Special cases
    if percentile == 0:
        return sorted_data[0]
    if percentile == 100:
        return sorted_data[-1]

    # Nearest-rank method
    rank = (percentile / 100) * (n - 1)
    lower_index = int(rank)
    upper_index = lower_index + 1

    # Linear interpolation between closest ranks
    if upper_index >= n:
        return sorted_data[lower_index]
    lower_value = sorted_data[lower_index]
    upper_value = sorted_data[upper_index]
    fraction = rank - lower_index
    return lower_value + (upper_value - lower_value) * fraction
