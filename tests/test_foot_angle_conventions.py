"""Tests for clinically interpretable foot angle conventions."""

from __future__ import annotations

from pathlib import Path

import cv2
import numpy as np

from biomechanics.foot_metrics import (
    _largest_contours,
    _principal_axis_angle,
    _skin_mask,
    analyze_calcaneal_image,
    analyze_foot_progression_image,
)

_FRONT_IMAGE = Path("data/images/evaluations/feet/frontal/frontal-lower-3.jpeg")
_BACK_IMAGE = Path("data/images/evaluations/feet/posterior/posterior-feet-5.jpeg")


def _load_image(path: Path):
    image = cv2.imread(str(path))
    assert image is not None
    return image


def _raw_front_axis_angles(image) -> tuple[float, float]:
    mask = _skin_mask(image)
    roi = mask[mask.shape[0] // 2 :, :]
    contours = _largest_contours(roi, count=2)
    shifted = []
    for contour in contours:
        shifted_contour = contour.copy()
        shifted_contour[:, 0, 1] += mask.shape[0] // 2
        shifted.append((cv2.boundingRect(shifted_contour)[0], shifted_contour))
    shifted.sort(key=lambda item: item[0])
    return _principal_axis_angle(shifted[0][1]), _principal_axis_angle(shifted[1][1])


def _raw_back_axis_angles(image) -> tuple[float, float]:
    mask = _skin_mask(image)
    roi = mask[mask.shape[0] // 3 :, :]
    contours = _largest_contours(roi, count=2)
    processed = []
    for contour in contours:
        shifted = contour.copy()
        shifted[:, 0, 1] += mask.shape[0] // 3
        x, y, _, height_box = cv2.boundingRect(shifted)
        y_threshold = y + int(height_box * 0.45)
        heel_points = shifted[shifted[:, 0, 1] >= y_threshold]
        heel_contour = heel_points.reshape(-1, 1, 2) if heel_points.size else shifted
        processed.append((x, heel_contour))
    processed.sort(key=lambda item: item[0])
    return _principal_axis_angle(processed[0][1]), _principal_axis_angle(processed[1][1])


def test_foot_progression_angles_are_clinical_deviations_not_absolute_axes() -> None:
    image = _load_image(_FRONT_IMAGE)
    analysis = analyze_foot_progression_image(image)
    raw_left, raw_right = _raw_front_axis_angles(image)

    left_value = analysis["metrics"]["foot_progression_angle_left"]
    right_value = analysis["metrics"]["foot_progression_angle_right"]

    assert abs(left_value) < 25.0
    assert abs(right_value) < 25.0
    assert not np.isclose(left_value, abs(raw_left), atol=1.0)
    assert not np.isclose(right_value, abs(raw_right), atol=1.0)


def test_calcaneal_angles_are_clinical_deviations_not_absolute_axes() -> None:
    image = _load_image(_BACK_IMAGE)
    analysis = analyze_calcaneal_image(image)
    raw_left, raw_right = _raw_back_axis_angles(image)

    left_value = analysis["metrics"]["calcaneal_angle_left"]
    right_value = analysis["metrics"]["calcaneal_angle_right"]

    assert abs(left_value) < 20.0
    assert abs(right_value) < 20.0
    assert not np.isclose(left_value, abs(raw_left), atol=1.0)
    assert not np.isclose(right_value, abs(raw_right), atol=1.0)


def test_angle_debug_payloads_include_neutral_reference_lines() -> None:
    front_debug = analyze_foot_progression_image(_load_image(_FRONT_IMAGE))["debug"]
    back_debug = analyze_calcaneal_image(_load_image(_BACK_IMAGE))["debug"]

    front_labels = {line["label"] for line in front_debug["reference_lines"]}
    back_labels = {line["label"] for line in back_debug["reference_lines"]}

    assert {"left_foot_axis", "left_foot_neutral", "right_foot_axis", "right_foot_neutral"} <= front_labels
    assert {"left_calcaneal_axis", "left_calcaneal_neutral", "right_calcaneal_axis", "right_calcaneal_neutral"} <= back_labels
