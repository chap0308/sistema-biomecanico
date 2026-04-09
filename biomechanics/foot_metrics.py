"""Static feet heuristics used by the grouped image endpoint."""

from __future__ import annotations

from math import atan2, degrees
from typing import Any

import cv2
import numpy as np


def _skin_mask(image_bgr: np.ndarray) -> np.ndarray:
    ycrcb = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2YCrCb)
    hsv = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2HSV)
    ycrcb_mask = cv2.inRange(ycrcb, (0, 133, 77), (255, 180, 135))
    hsv_mask = cv2.inRange(hsv, (0, 15, 35), (25, 255, 255))
    mask = cv2.bitwise_and(ycrcb_mask, hsv_mask)
    kernel = np.ones((5, 5), dtype=np.uint8)
    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)
    return mask


def _largest_contours(mask: np.ndarray, *, count: int, min_area_ratio: float = 0.002) -> list[np.ndarray]:
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    min_area = mask.shape[0] * mask.shape[1] * min_area_ratio
    valid = [contour for contour in contours if cv2.contourArea(contour) >= min_area]
    valid.sort(key=cv2.contourArea, reverse=True)
    return valid[:count]


def _principal_axis_angle(contour: np.ndarray) -> float:
    points = contour.reshape(-1, 2).astype(np.float32)
    mean = np.mean(points, axis=0)
    centered = points - mean
    covariance = np.cov(centered.T)
    eigenvalues, eigenvectors = np.linalg.eigh(covariance)
    axis = eigenvectors[:, int(np.argmax(eigenvalues))]
    return degrees(atan2(axis[1], axis[0]))


def _signed_deviation_from_vertical(angle_deg: float) -> float:
    canonical = (angle_deg + 180.0) % 180.0
    signed = canonical - 90.0
    if signed > 90.0:
        signed -= 180.0
    if signed <= -90.0:
        signed += 180.0
    return float(signed)


def _normalize_point(point: tuple[float, float], *, width: int, height: int) -> dict[str, float]:
    return {
        "x": float(point[0]) / max(width, 1),
        "y": float(point[1]) / max(height, 1),
    }


def _normalize_contour(contour: np.ndarray, *, width: int, height: int, max_points: int = 120) -> list[dict[str, float]]:
    points = contour.reshape(-1, 2)
    if len(points) > max_points:
        indices = np.linspace(0, len(points) - 1, num=max_points, dtype=int)
        points = points[indices]
    return [_normalize_point((float(x), float(y)), width=width, height=height) for x, y in points]


def _principal_axis_segment(contour: np.ndarray) -> tuple[tuple[float, float], tuple[float, float]]:
    points = contour.reshape(-1, 2).astype(np.float32)
    center = np.mean(points, axis=0)
    angle = np.deg2rad(_principal_axis_angle(contour))
    extent = max(float(np.ptp(points[:, 0])), float(np.ptp(points[:, 1])), 1.0) * 0.45
    dx = np.cos(angle) * extent
    dy = np.sin(angle) * extent
    first = (float(center[0] - dx), float(center[1] - dy))
    second = (float(center[0] + dx), float(center[1] + dy))
    return (first, second) if first[1] <= second[1] else (second, first)


def _line_payload(
    start: tuple[float, float],
    end: tuple[float, float],
    *,
    width: int,
    height: int,
    label: str,
) -> dict[str, object]:
    return {
        "label": label,
        "start": _normalize_point(start, width=width, height=height),
        "end": _normalize_point(end, width=width, height=height),
    }


def _axis_line(contour: np.ndarray, *, width: int, height: int, label: str) -> dict[str, object]:
    start, end = _principal_axis_segment(contour)
    return _line_payload(start, end, width=width, height=height, label=label)


def _neutral_vertical_line(contour: np.ndarray, *, width: int, height: int, label: str) -> dict[str, object]:
    start, end = _principal_axis_segment(contour)
    center_x = float((start[0] + end[0]) / 2.0)
    return _line_payload((center_x, start[1]), (center_x, end[1]), width=width, height=height, label=label)


def _clinical_signed_angle(contour: np.ndarray, *, side: str) -> tuple[float, tuple[float, float], tuple[float, float]]:
    axis_start, axis_end = _principal_axis_segment(contour)
    raw_angle = _principal_axis_angle(contour)
    signed_vertical = _signed_deviation_from_vertical(raw_angle)
    lateral_multiplier = -1.0 if side == "left" else 1.0
    return signed_vertical * lateral_multiplier, axis_start, axis_end


def _interpret_progression(angle_deg: float) -> str:
    if angle_deg > 2.0:
        return "toe_out"
    if angle_deg < -2.0:
        return "toe_in"
    return "neutral"


def _interpret_calcaneal(angle_deg: float) -> str:
    if angle_deg > 2.0:
        return "valgus"
    if angle_deg < -2.0:
        return "varus"
    return "neutral"


def _classify_foot_progression(angle_deg: float) -> tuple[str, list[str]]:
    if angle_deg < -5.0:
        return "toe_in", ["toe_in"]
    if angle_deg > 10.0:
        return "toe_out", ["toe_out"]
    return "neutral", []


def _classify_calcaneal(angle_deg: float) -> tuple[str, list[str]]:
    if angle_deg < 0.0:
        return "varus", ["rearfoot_varus"]
    if angle_deg <= 6.0:
        return "normal", []
    if angle_deg <= 16.0:
        return "valgus_mild", ["rearfoot_valgus"]
    if angle_deg <= 26.0:
        return "valgus_moderate", ["rearfoot_valgus"]
    return "valgus_severe", ["rearfoot_valgus", "rearfoot_valgus_severe"]


def _classify_arch_ratio(ratio: float) -> tuple[str, list[str]]:
    if ratio < 0.04:
        return "low_arch", ["low_arch"]
    if ratio <= 0.10:
        return "normal_arch", []
    return "high_arch", ["high_arch"]


def _axis_stability(contour: np.ndarray) -> float:
    points = contour.reshape(-1, 2).astype(np.float32)
    centered = points - np.mean(points, axis=0)
    covariance = np.cov(centered.T)
    eigenvalues, _ = np.linalg.eigh(covariance)
    ordered = np.sort(np.abs(eigenvalues))
    return float(ordered[-1] / max(ordered[0], 1e-6))


def _confidence_from_contour(
    contour: np.ndarray,
    *,
    width: int,
    height: int,
    metric_kind: str,
    angle_deg: float | None = None,
) -> tuple[float, list[str]]:
    area = float(cv2.contourArea(contour))
    x, y, box_w, box_h = cv2.boundingRect(contour)
    notes: list[str] = []
    confidence = 0.9

    border_touches = _touches_image_border(contour, width=width, height=height)
    if border_touches > 0:
        notes.append("partial foot contour")
        confidence -= 0.10 * border_touches

    box_area = float(max(box_w * box_h, 1))
    solidity = area / box_area
    if solidity < 0.30:
        notes.append("segmentation irregular")
        confidence -= 0.14
    elif solidity < 0.45:
        confidence -= 0.06

    stability = _axis_stability(contour)
    if stability < 2.5:
        notes.append("axis detection unstable")
        confidence -= 0.18
    elif stability < 4.0:
        confidence -= 0.08

    if box_h < height * 0.14 or box_w < width * 0.05:
        notes.append("foot crop too small")
        confidence -= 0.18

    if metric_kind == "progression":
        if box_h > height * 0.55:
            notes.append("contour includes lower leg")
            confidence -= 0.08
        if angle_deg is not None and abs(angle_deg) > 22.0:
            notes.append("camera tilt suspected")
            confidence -= 0.10
    elif metric_kind == "calcaneal":
        if box_w < width * 0.06:
            notes.append("heel not fully visible")
            confidence -= 0.18
        if box_h > height * 0.22:
            notes.append("contour includes lower leg")
            confidence -= 0.10
        if y + box_h >= height - 2:
            notes.append("heel base clipped")
            confidence -= 0.10

    confidence = float(np.clip(confidence, 0.0, 0.95))
    deduped_notes = list(dict.fromkeys(notes))
    return confidence, deduped_notes


def _metric_detail_payload(*, confidence: float, quality_notes: list[str], classification: str, flags: list[str]) -> dict[str, object]:
    return {
        "confidence": confidence,
        "quality_notes": list(dict.fromkeys(quality_notes)),
        "classification": classification,
        "flags": list(dict.fromkeys(flags)),
    }


def _largest_true_run(mask: np.ndarray) -> tuple[int, int] | None:
    best_start = -1
    best_end = -1
    run_start = -1
    for index, value in enumerate(mask.tolist()):
        if value and run_start < 0:
            run_start = index
        elif not value and run_start >= 0:
            if index - run_start > best_end - best_start:
                best_start = run_start
                best_end = index
            run_start = -1
    if run_start >= 0 and len(mask) - run_start > best_end - best_start:
        best_start = run_start
        best_end = len(mask)
    if best_start < 0:
        return None
    return best_start, best_end


def _touches_image_border(contour: np.ndarray, *, width: int, height: int) -> int:
    points = contour.reshape(-1, 2)
    return (
        int(np.any(points[:, 0] <= 1))
        + int(np.any(points[:, 0] >= width - 2))
        + int(np.any(points[:, 1] <= 1))
        + int(np.any(points[:, 1] >= height - 2))
    )


def _grabcut_foreground_mask(image_bgr: np.ndarray) -> np.ndarray:
    height, width = image_bgr.shape[:2]
    scale = min(1.0, 640.0 / float(max(height, width)))
    resized = image_bgr
    if scale < 1.0:
        resized = cv2.resize(
            image_bgr,
            (max(1, int(width * scale)), max(1, int(height * scale))),
            interpolation=cv2.INTER_AREA,
        )

    small_h, small_w = resized.shape[:2]
    mask = np.zeros((small_h, small_w), dtype=np.uint8)
    rect = (
        max(1, int(small_w * 0.08)),
        max(1, int(small_h * 0.05)),
        max(2, int(small_w * 0.84)),
        max(2, int(small_h * 0.90)),
    )
    bgd_model = np.zeros((1, 65), dtype=np.float64)
    fgd_model = np.zeros((1, 65), dtype=np.float64)
    cv2.grabCut(resized, mask, rect, bgd_model, fgd_model, 2, cv2.GC_INIT_WITH_RECT)
    foreground = np.where((mask == cv2.GC_FGD) | (mask == cv2.GC_PR_FGD), 255, 0).astype(np.uint8)
    kernel = np.ones((5, 5), dtype=np.uint8)
    foreground = cv2.morphologyEx(foreground, cv2.MORPH_OPEN, kernel)
    foreground = cv2.morphologyEx(foreground, cv2.MORPH_CLOSE, kernel)
    if scale < 1.0:
        foreground = cv2.resize(foreground, (width, height), interpolation=cv2.INTER_NEAREST)
    return foreground


def _select_arch_contour(mask: np.ndarray) -> np.ndarray | None:
    height, width = mask.shape[:2]
    contours = _largest_contours(mask, count=8, min_area_ratio=0.003)
    best_contour = None
    best_score = float("-inf")
    image_area = float(height * width)
    for contour in contours:
        x, y, box_w, box_h = cv2.boundingRect(contour)
        if box_w < width * 0.15 or box_h < height * 0.15:
            continue
        area_ratio = cv2.contourArea(contour) / max(image_area, 1.0)
        border_touches = _touches_image_border(contour, width=width, height=height)
        if area_ratio > 0.90 and border_touches >= 3:
            continue
        score = area_ratio
        score += 0.12 * min(box_w / max(width, 1), 1.0)
        score += 0.12 * min(box_h / max(height, 1), 1.0)
        score -= 0.18 * border_touches
        if score > best_score:
            best_score = score
            best_contour = contour
    return best_contour


def _extract_arch_contour(image_bgr: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    if float(np.std(image_bgr)) < 2.0:
        raise ValueError("Unable to isolate the foot contour in the arch image.")

    try:
        grabcut_mask = _grabcut_foreground_mask(image_bgr)
        contour = _select_arch_contour(grabcut_mask)
        if contour is not None:
            return contour, grabcut_mask
    except cv2.error:
        pass

    skin_mask = _skin_mask(image_bgr)
    contour = _select_arch_contour(skin_mask)
    if contour is not None:
        return contour, skin_mask

    raise ValueError("Unable to isolate the foot contour in the arch image.")


def _column_profiles(mask: np.ndarray, *, x_min: int, x_max: int) -> tuple[np.ndarray, np.ndarray]:
    top_profile = np.full(x_max - x_min + 1, np.nan, dtype=np.float32)
    bottom_profile = np.full(x_max - x_min + 1, np.nan, dtype=np.float32)
    for index, x_coord in enumerate(range(x_min, x_max + 1)):
        column = np.flatnonzero(mask[:, x_coord] > 0)
        if column.size == 0:
            continue
        top_profile[index] = float(column.min())
        bottom_profile[index] = float(column.max())
    return top_profile, bottom_profile


def _fit_ground_line(x_coords: np.ndarray, bottom_profile: np.ndarray) -> tuple[np.ndarray, np.ndarray, list[str], float]:
    quality_notes: list[str] = []
    valid_bottom = bottom_profile[~np.isnan(bottom_profile)]
    if valid_bottom.size < 10:
        raise ValueError("Unable to estimate a stable plantar base from the foot silhouette.")

    contact_threshold = float(np.quantile(valid_bottom, 0.82))
    contact_mask = (~np.isnan(bottom_profile)) & (bottom_profile >= contact_threshold)
    contact_count = int(np.count_nonzero(contact_mask))
    if contact_count < 8:
        raise ValueError("Insufficient plantar contact points to estimate the arch base.")

    contact_x = x_coords[contact_mask]
    contact_y = bottom_profile[contact_mask]
    slope, intercept = np.polyfit(contact_x.astype(np.float32), contact_y.astype(np.float32), deg=1)
    ground_y = slope * x_coords + intercept

    heel_region = contact_x <= np.quantile(contact_x, 0.30)
    toe_region = contact_x >= np.quantile(contact_x, 0.70)
    if not np.any(heel_region) or not np.any(toe_region):
        quality_notes.append("Plantar contact support is incomplete; local ground fit may be unstable.")

    support_fraction = contact_count / max(len(x_coords), 1)
    if support_fraction < 0.18:
        quality_notes.append("Visible plantar contact area is limited; arch base confidence reduced.")
    confidence = max(0.2, min(0.95, 0.92 - 0.6 * max(0.0, 0.18 - support_fraction)))
    return ground_y, contact_mask, quality_notes, float(confidence)


def _build_arch_debug(
    *,
    contour: np.ndarray,
    width: int,
    height: int,
    arch_top: tuple[float, float],
    arch_base: tuple[float, float],
    heel_reference: tuple[float, float],
    toe_reference: tuple[float, float],
    ground_start: tuple[float, float],
    ground_end: tuple[float, float],
    band_start: tuple[float, float],
    band_end: tuple[float, float],
    heel_contact: tuple[float, float] | None,
    toe_contact: tuple[float, float] | None,
    ratio: float | None,
    confidence: float,
    quality_notes: list[str],
) -> dict[str, Any]:
    highlighted_points: dict[str, dict[str, float]] = {}
    if heel_contact is not None:
        highlighted_points["heel_contact"] = _normalize_point(heel_contact, width=width, height=height)
    if toe_contact is not None:
        highlighted_points["forefoot_contact"] = _normalize_point(toe_contact, width=width, height=height)

    return {
        "contours": [
            {"label": "arch_contour", "points": _normalize_contour(contour, width=width, height=height)},
        ],
        "reference_lines": [
            {
                "label": "local_ground_line",
                "start": _normalize_point(ground_start, width=width, height=height),
                "end": _normalize_point(ground_end, width=width, height=height),
            },
            {
                "label": "arch_height_measure",
                "start": _normalize_point(arch_top, width=width, height=height),
                "end": _normalize_point(arch_base, width=width, height=height),
            },
            {
                "label": "foot_length_reference",
                "start": _normalize_point(heel_reference, width=width, height=height),
                "end": _normalize_point(toe_reference, width=width, height=height),
            },
            {
                "label": "midfoot_search_band",
                "start": _normalize_point(band_start, width=width, height=height),
                "end": _normalize_point(band_end, width=width, height=height),
            },
        ],
        "points_used": {
            "arch_top": _normalize_point(arch_top, width=width, height=height),
            "arch_base": _normalize_point(arch_base, width=width, height=height),
            "heel_reference": _normalize_point(heel_reference, width=width, height=height),
            "toe_reference": _normalize_point(toe_reference, width=width, height=height),
            "midfoot_band_start": _normalize_point(band_start, width=width, height=height),
            "midfoot_band_end": _normalize_point(band_end, width=width, height=height),
        },
        "highlighted_points": highlighted_points,
        "analysis_quality": {
            "confidence": confidence,
            "quality_notes": quality_notes,
            "arch_height_ratio": ratio,
        },
    }


def analyze_foot_progression_image(image_bgr: np.ndarray) -> dict[str, object]:
    """Estimate signed frontal foot progression relative to a neutral vertical reference."""
    height, width = image_bgr.shape[:2]
    mask = _skin_mask(image_bgr)
    lower_half = mask[mask.shape[0] // 2 :, :]
    contours = _largest_contours(lower_half, count=2)
    if len(contours) < 2:
        raise ValueError("Unable to isolate both feet in the frontal feet image.")

    offsets = []
    for contour in contours:
        shifted = contour.copy()
        shifted[:, 0, 1] += mask.shape[0] // 2
        offsets.append((cv2.boundingRect(shifted)[0], shifted))
    offsets.sort(key=lambda item: item[0])
    left_contour = offsets[0][1]
    right_contour = offsets[1][1]

    left_angle, _, _ = _clinical_signed_angle(left_contour, side="left")
    right_angle, _, _ = _clinical_signed_angle(right_contour, side="right")
    left_classification, left_flags = _classify_foot_progression(left_angle)
    right_classification, right_flags = _classify_foot_progression(right_angle)
    left_confidence, left_notes = _confidence_from_contour(
        left_contour,
        width=width,
        height=height,
        metric_kind="progression",
        angle_deg=left_angle,
    )
    right_confidence, right_notes = _confidence_from_contour(
        right_contour,
        width=width,
        height=height,
        metric_kind="progression",
        angle_deg=right_angle,
    )
    if np.sign(left_angle) == np.sign(right_angle) and abs(left_angle) > 8.0 and abs(right_angle) > 8.0:
        tilt_note = "camera tilt suspected"
        left_notes.append(tilt_note)
        right_notes.append(tilt_note)
        left_confidence = float(np.clip(left_confidence - 0.08, 0.0, 0.95))
        right_confidence = float(np.clip(right_confidence - 0.08, 0.0, 0.95))

    return {
        "metrics": {
            "foot_progression_angle_left": left_angle,
            "foot_progression_angle_right": right_angle,
        },
        "metric_details": {
            "foot_progression_angle_left": _metric_detail_payload(
                confidence=left_confidence,
                quality_notes=left_notes,
                classification=left_classification,
                flags=left_flags,
            ),
            "foot_progression_angle_right": _metric_detail_payload(
                confidence=right_confidence,
                quality_notes=right_notes,
                classification=right_classification,
                flags=right_flags,
            ),
        },
        "debug": {
            "contours": [
                {"label": "left_foot_contour", "points": _normalize_contour(left_contour, width=width, height=height)},
                {"label": "right_foot_contour", "points": _normalize_contour(right_contour, width=width, height=height)},
            ],
            "reference_lines": [
                _axis_line(left_contour, width=width, height=height, label="left_foot_axis"),
                _neutral_vertical_line(left_contour, width=width, height=height, label="left_foot_neutral"),
                _axis_line(right_contour, width=width, height=height, label="right_foot_axis"),
                _neutral_vertical_line(right_contour, width=width, height=height, label="right_foot_neutral"),
            ],
            "analysis": {
                "foot_progression_angle_left": {
                    "value": left_angle,
                    "interpretation": _interpret_progression(left_angle),
                    "classification": left_classification,
                    "confidence": left_confidence,
                    "quality_notes": list(dict.fromkeys(left_notes)),
                },
                "foot_progression_angle_right": {
                    "value": right_angle,
                    "interpretation": _interpret_progression(right_angle),
                    "classification": right_classification,
                    "confidence": right_confidence,
                    "quality_notes": list(dict.fromkeys(right_notes)),
                },
            },
        },
    }


def analyze_calcaneal_image(image_bgr: np.ndarray) -> dict[str, object]:
    """Estimate signed rearfoot varus-valgus deviation relative to a neutral vertical reference."""
    height, width = image_bgr.shape[:2]
    mask = _skin_mask(image_bgr)
    lower_half = mask[mask.shape[0] // 3 :, :]
    contours = _largest_contours(lower_half, count=2)
    if len(contours) < 2:
        raise ValueError("Unable to isolate both rear feet in the posterior feet image.")

    processed: list[tuple[int, np.ndarray]] = []
    for contour in contours:
        shifted = contour.copy()
        shifted[:, 0, 1] += mask.shape[0] // 3
        x, y, width_box, height_box = cv2.boundingRect(shifted)
        y_threshold = y + int(height_box * 0.45)
        heel_points = shifted[shifted[:, 0, 1] >= y_threshold]
        heel_contour = heel_points.reshape(-1, 1, 2) if heel_points.size else shifted
        processed.append((x, heel_contour))
    processed.sort(key=lambda item: item[0])
    left_contour = processed[0][1]
    right_contour = processed[1][1]

    left_angle, _, _ = _clinical_signed_angle(left_contour, side="left")
    right_angle, _, _ = _clinical_signed_angle(right_contour, side="right")
    left_classification, left_flags = _classify_calcaneal(left_angle)
    right_classification, right_flags = _classify_calcaneal(right_angle)
    left_confidence, left_notes = _confidence_from_contour(
        left_contour,
        width=width,
        height=height,
        metric_kind="calcaneal",
        angle_deg=left_angle,
    )
    right_confidence, right_notes = _confidence_from_contour(
        right_contour,
        width=width,
        height=height,
        metric_kind="calcaneal",
        angle_deg=right_angle,
    )
    if np.sign(left_angle) == np.sign(right_angle) and abs(left_angle) > 10.0 and abs(right_angle) > 10.0:
        tilt_note = "camera tilt suspected"
        left_notes.append(tilt_note)
        right_notes.append(tilt_note)
        left_confidence = float(np.clip(left_confidence - 0.08, 0.0, 0.95))
        right_confidence = float(np.clip(right_confidence - 0.08, 0.0, 0.95))

    return {
        "metrics": {
            "calcaneal_angle_left": left_angle,
            "calcaneal_angle_right": right_angle,
        },
        "metric_details": {
            "calcaneal_angle_left": _metric_detail_payload(
                confidence=left_confidence,
                quality_notes=left_notes,
                classification=left_classification,
                flags=left_flags,
            ),
            "calcaneal_angle_right": _metric_detail_payload(
                confidence=right_confidence,
                quality_notes=right_notes,
                classification=right_classification,
                flags=right_flags,
            ),
        },
        "debug": {
            "contours": [
                {"label": "left_calcaneus_contour", "points": _normalize_contour(left_contour, width=width, height=height)},
                {"label": "right_calcaneus_contour", "points": _normalize_contour(right_contour, width=width, height=height)},
            ],
            "reference_lines": [
                _axis_line(left_contour, width=width, height=height, label="left_calcaneal_axis"),
                _neutral_vertical_line(left_contour, width=width, height=height, label="left_calcaneal_neutral"),
                _axis_line(right_contour, width=width, height=height, label="right_calcaneal_axis"),
                _neutral_vertical_line(right_contour, width=width, height=height, label="right_calcaneal_neutral"),
            ],
            "analysis": {
                "calcaneal_angle_left": {
                    "value": left_angle,
                    "interpretation": _interpret_calcaneal(left_angle),
                    "classification": left_classification,
                    "confidence": left_confidence,
                    "quality_notes": list(dict.fromkeys(left_notes)),
                },
                "calcaneal_angle_right": {
                    "value": right_angle,
                    "interpretation": _interpret_calcaneal(right_angle),
                    "classification": right_classification,
                    "confidence": right_confidence,
                    "quality_notes": list(dict.fromkeys(right_notes)),
                },
            },
        },
    }


def analyze_arch_image(image_bgr: np.ndarray) -> dict[str, object]:
    """Estimate a midfoot height-to-length ratio and expose anatomically constrained debug metadata."""
    height, width = image_bgr.shape[:2]
    contour, source_mask = _extract_arch_contour(image_bgr)

    contour_2d = contour.reshape(-1, 2)
    x_min = int(np.min(contour_2d[:, 0]))
    x_max = int(np.max(contour_2d[:, 0]))
    y_min = int(np.min(contour_2d[:, 1]))
    y_max = int(np.max(contour_2d[:, 1]))
    if x_max <= x_min or y_max <= y_min:
        raise ValueError("Unable to derive a valid foot bounding box from the arch contour.")

    filled_mask = np.zeros_like(source_mask)
    cv2.drawContours(filled_mask, [contour], -1, 255, thickness=-1)
    top_profile, bottom_profile = _column_profiles(filled_mask, x_min=x_min, x_max=x_max)
    x_coords = np.arange(x_min, x_max + 1, dtype=np.float32)

    box_height = float(y_max - y_min)
    foot_run: tuple[int, int] | None = None
    for threshold_ratio in (0.58, 0.54, 0.50, 0.46):
        ankle_limit_y = y_min + box_height * threshold_ratio
        foot_mask = (~np.isnan(top_profile)) & (top_profile >= ankle_limit_y)
        foot_run = _largest_true_run(foot_mask)
        if foot_run is not None and (foot_run[1] - foot_run[0]) >= max(25, int(0.22 * len(x_coords))):
            break
    if foot_run is None:
        raise ValueError("Unable to isolate the foot segment below the ankle in the arch image.")

    foot_start_index, foot_end_index = foot_run
    foot_x = x_coords[foot_start_index:foot_end_index]
    foot_top = top_profile[foot_start_index:foot_end_index]
    foot_bottom = bottom_profile[foot_start_index:foot_end_index]
    if foot_x.size < 20:
        raise ValueError("Foot segment below the ankle is too small for arch measurement.")

    ground_y, contact_mask, ground_notes, ground_confidence = _fit_ground_line(foot_x, foot_bottom)
    valid_foot_mask = ~np.isnan(foot_top)
    if not np.any(valid_foot_mask):
        raise ValueError("Unable to sample the dorsum profile across the foot segment.")

    foot_span = max(foot_end_index - foot_start_index - 1, 1)
    band_start_index = int(foot_start_index + 0.28 * foot_span)
    band_end_index = int(foot_start_index + 0.62 * foot_span)
    band_end_index = max(band_end_index, band_start_index + 1)

    band_slice = slice(band_start_index - foot_start_index, band_end_index - foot_start_index + 1)
    band_x = foot_x[band_slice]
    band_top = foot_top[band_slice]
    band_bottom = foot_bottom[band_slice]
    band_ground = ground_y[band_slice]
    band_valid = (~np.isnan(band_top)) & (~np.isnan(band_bottom))
    if not np.any(band_valid):
        raise ValueError("Unable to sample the midfoot region in the arch image.")

    band_clearance = band_ground - band_bottom
    band_clearance = np.where(band_valid, band_clearance, -np.inf)
    arch_local_index = int(np.argmax(band_clearance))
    arch_x = float(band_x[arch_local_index])
    arch_top_y = float(band_bottom[arch_local_index])
    arch_base_y = float(band_ground[arch_local_index])
    arch_height = arch_base_y - arch_top_y

    heel_x = float(foot_x[0])
    toe_x = float(foot_x[-1])
    heel_y = float(ground_y[0])
    toe_y = float(ground_y[-1])
    foot_length = max(toe_x - heel_x, 1.0)
    ratio = arch_height / foot_length

    quality_notes = list(ground_notes)
    confidence = ground_confidence
    border_touches = _touches_image_border(contour, width=width, height=height)
    if border_touches >= 2:
        quality_notes.append("Silhouette touches the crop border; contour isolation may be incomplete.")
        confidence -= 0.12
    if arch_height <= 0.0:
        raise ValueError("Arch height could not be estimated above the local plantar base.")
    if band_clearance[arch_local_index] < max(3.0, 0.015 * foot_length):
        quality_notes.append("Midfoot plantar clearance is weak; arch location may be ambiguous.")
        confidence -= 0.15
    if ratio < 0.03 or ratio > 0.45:
        quality_notes.append("Arch height ratio falls outside a plausible anatomical range for this capture.")
        confidence -= 0.28

    confidence = float(np.clip(confidence, 0.0, 0.95))
    status = "computed" if confidence >= 0.55 else "low_confidence"
    classification, flags = _classify_arch_ratio(float(ratio))

    contact_x = foot_x[contact_mask]
    contact_y = foot_bottom[contact_mask]
    heel_contact = (float(contact_x[0]), float(contact_y[0])) if contact_x.size else None
    toe_contact = (float(contact_x[-1]), float(contact_y[-1])) if contact_x.size else None

    arch_top = (arch_x, arch_top_y)
    arch_base = (arch_x, arch_base_y)
    heel_reference = (heel_x, heel_y)
    toe_reference = (toe_x, toe_y)
    band_start = (float(x_coords[band_start_index]), float(ground_y[max(0, band_start_index - foot_start_index)]))
    band_end = (float(x_coords[band_end_index]), float(ground_y[min(len(ground_y) - 1, band_end_index - foot_start_index)]))

    return {
        "metric": float(ratio),
        "status": status,
        "confidence": confidence,
        "quality_notes": quality_notes,
        "classification": classification,
        "flags": flags,
        "debug": _build_arch_debug(
            contour=contour,
            width=width,
            height=height,
            arch_top=arch_top,
            arch_base=arch_base,
            heel_reference=heel_reference,
            toe_reference=toe_reference,
            ground_start=heel_reference,
            ground_end=toe_reference,
            band_start=band_start,
            band_end=band_end,
            heel_contact=heel_contact,
            toe_contact=toe_contact,
            ratio=float(ratio),
            confidence=confidence,
            quality_notes=quality_notes,
        ),
    }


def compute_foot_progression_angles(image_bgr: np.ndarray) -> dict[str, float]:
    """Estimate each foot long-axis rotation from the frontal feet image."""
    return analyze_foot_progression_image(image_bgr)["metrics"]


def compute_calcaneal_angles(image_bgr: np.ndarray) -> dict[str, float]:
    """Estimate rearfoot/Achilles alignment from the posterior feet image."""
    return analyze_calcaneal_image(image_bgr)["metrics"]


def compute_arch_height_ratio(image_bgr: np.ndarray) -> float:
    """Estimate a midfoot height-to-length ratio from a lateral arch image."""
    return float(analyze_arch_image(image_bgr)["metric"])


__all__ = [
    "analyze_arch_image",
    "analyze_calcaneal_image",
    "analyze_foot_progression_image",
    "compute_arch_height_ratio",
    "compute_calcaneal_angles",
    "compute_foot_progression_angles",
]
