"""Geometric helpers for angles, vectors and distances."""

from math import acos, atan2, degrees, sqrt

from biomechanics.models import Point2D


def euclidean_distance_2d(point_a: tuple[float, float], point_b: tuple[float, float]) -> float:
    """Compute 2D Euclidean distance between two points."""
    ax, ay = point_a
    bx, by = point_b
    return sqrt((bx - ax) ** 2 + (by - ay) ** 2)


def safe_acos(value: float) -> float:
    """Clamp values to valid acos range to avoid numeric errors."""
    return acos(max(-1.0, min(1.0, value)))


def midpoint(point_a: Point2D, point_b: Point2D) -> Point2D:
    """Return midpoint between two points."""
    return Point2D(x=(point_a.x + point_b.x) / 2.0, y=(point_a.y + point_b.y) / 2.0)


def vector(point_a: Point2D, point_b: Point2D) -> tuple[float, float]:
    """Return vector from `point_a` to `point_b`."""
    return (point_b.x - point_a.x, point_b.y - point_a.y)


def vector_norm(vec: tuple[float, float]) -> float:
    """Return Euclidean norm of a 2D vector."""
    vx, vy = vec
    return sqrt(vx * vx + vy * vy)


def angle_between_vectors_deg(vec_a: tuple[float, float], vec_b: tuple[float, float]) -> float:
    """Return angle in degrees between vectors in range [0, 180]."""
    norm_a = vector_norm(vec_a)
    norm_b = vector_norm(vec_b)
    if norm_a == 0 or norm_b == 0:
        return 0.0

    dot = vec_a[0] * vec_b[0] + vec_a[1] * vec_b[1]
    return degrees(safe_acos(dot / (norm_a * norm_b)))


def angle_3p_deg(point_a: Point2D, point_b: Point2D, point_c: Point2D) -> float:
    """Return angle ABC (at point_b) in degrees."""
    vec_ba = vector(point_b, point_a)
    vec_bc = vector(point_b, point_c)
    return angle_between_vectors_deg(vec_ba, vec_bc)


def line_angle_to_horizontal_deg(point_a: Point2D, point_b: Point2D) -> float:
    """Return absolute line angle to horizontal axis in degrees."""
    dx, dy = vector(point_a, point_b)
    return abs(degrees(atan2(dy, dx)))


def line_angle_to_vertical_deg(point_a: Point2D, point_b: Point2D) -> float:
    """Return absolute line angle to vertical axis in degrees."""
    dx, dy = vector(point_a, point_b)
    return abs(degrees(atan2(dx, dy)))
