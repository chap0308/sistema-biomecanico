"""Unit tests for lateral foot arch metrics."""

from __future__ import annotations

from pathlib import Path

import cv2
import numpy as np
import pytest

from biomechanics.foot_metrics import analyze_arch_image

_DATA_ROOT = Path("data/images/evaluations/feet/lateral")


def _load_arch_asset(name: str) -> np.ndarray:
    image = cv2.imread(str(_DATA_ROOT / name))
    assert image is not None
    return image


def test_analyze_arch_image_keeps_measurement_in_midfoot_zone_on_real_assets() -> None:
    for name in ("arch-left-1.jpeg", "arch-right-1.jpeg"):
        analysis = analyze_arch_image(_load_arch_asset(name))
        points = analysis["debug"]["points_used"]

        assert analysis["status"] in {"computed", "low_confidence"}
        assert analysis["confidence"] > 0.0
        assert 0.03 < analysis["metric"] < 0.35
        assert points["arch_top"]["y"] > 0.40
        assert points["arch_base"]["y"] > points["arch_top"]["y"]
        assert points["arch_base"]["y"] < 0.98
        assert points["heel_reference"]["y"] < 0.98
        assert points["toe_reference"]["y"] < 0.98


def test_analyze_arch_image_debug_lines_match_reported_points() -> None:
    analysis = analyze_arch_image(_load_arch_asset("arch-left-1.jpeg"))
    points = analysis["debug"]["points_used"]
    lines = {line["label"]: line for line in analysis["debug"]["reference_lines"]}

    assert lines["arch_height_measure"]["start"] == points["arch_top"]
    assert lines["arch_height_measure"]["end"] == points["arch_base"]
    assert lines["foot_length_reference"]["start"] == points["heel_reference"]
    assert lines["foot_length_reference"]["end"] == points["toe_reference"]


def test_analyze_arch_image_rejects_blank_capture() -> None:
    image = np.full((320, 420, 3), 255, dtype=np.uint8)

    with pytest.raises(ValueError):
        analyze_arch_image(image)
