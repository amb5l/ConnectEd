"""
This module contains utility classes and functions for testing.
"""

from typing import Self


class MinMax:
    def __init__(self : Self, min_val : int | float, max_val : int | float):
        if not isinstance(min_val, (int, float)) \
        or not isinstance(max_val, (int, float)):
            raise TypeError("Min and max must be integers or floats")
        if min_val > max_val:
            raise ValueError("Min must be <= max")
        self._min = min_val
        self._max = max_val

    @property
    def min(self : Self):
        return self._min

    @property
    def max(self : Self):
        return self._max

    def __repr__(self : Self):
        return f"MinMax(min={self._min}, max={self._max})"

    def __eq__(self : Self, other):
        if not isinstance(other, MinMax):
            return False
        return self._min == other._min and self._max == other._max
