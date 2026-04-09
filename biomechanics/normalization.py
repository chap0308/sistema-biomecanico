"""Normalization helpers for body-size and camera-scale compensation."""


def normalize_by_reference(value: float, reference: float) -> float:
    """Normalize a scalar by a positive reference value."""
    if reference <= 0:
        raise ValueError("reference must be greater than 0")
    return value / reference

