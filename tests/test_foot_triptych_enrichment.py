"""Tests for enriched foot-triptych metric payloads and robustness notes."""

from __future__ import annotations

from pathlib import Path

import cv2

from api.schemas.image import UploadedStaticImage
from orchestration.image_subpipelines.foot_triptych_pipeline import FootTriptychPipeline
from biomechanics.foot_metrics import analyze_arch_image, analyze_calcaneal_image, analyze_foot_progression_image

_DATA_ROOT = Path("data/images/evaluations/feet")


def _uploaded_image(path: Path) -> UploadedStaticImage:
    return UploadedStaticImage(
        filename=path.name,
        content_type="image/jpeg",
        payload=path.read_bytes(),
    )


def test_foot_triptych_pipeline_returns_classification_flags_and_summary() -> None:
    pipeline = FootTriptychPipeline()
    result = pipeline.analyze(
        {
            "front": _uploaded_image(_DATA_ROOT / "frontal" / "frontal-lower-3.jpeg"),
            "back": _uploaded_image(_DATA_ROOT / "posterior" / "posterior-feet-5.jpeg"),
            "left_arch": _uploaded_image(_DATA_ROOT / "lateral" / "arch-left-1.jpeg"),
            "right_arch": _uploaded_image(_DATA_ROOT / "lateral" / "arch-right-1.jpeg"),
        },
        include_placeholders=True,
    )

    assert result["confidence_overall"] is not None
    assert result["confidence_overall"] > 0.0
    assert "foot_triptych_summary" in result
    assert result["foot_triptych_summary"]["rearfoot_pattern"] != "undetermined"
    assert "classification" in result["metrics"]["calcaneal_angle_left"]
    assert "flags" in result["metrics"]["foot_progression_angle_right"]
    assert result["metrics"]["arch_height_ratio_left"]["classification"] is not None


def test_calcaneal_confidence_drops_when_heel_is_clipped() -> None:
    image = cv2.imread(str(_DATA_ROOT / "posterior" / "posterior-feet-5.jpeg"))
    assert image is not None

    baseline = analyze_calcaneal_image(image)
    clipped = analyze_calcaneal_image(image[:-120, 60:])

    assert clipped["metric_details"]["calcaneal_angle_left"]["confidence"] < baseline["metric_details"]["calcaneal_angle_left"]["confidence"]
    assert "heel base clipped" in clipped["metric_details"]["calcaneal_angle_left"]["quality_notes"]


def test_arch_metric_degrades_to_placeholder_when_plantar_base_is_not_detectable() -> None:
    pipeline = FootTriptychPipeline()
    result = pipeline.analyze(
        {
            "front": _uploaded_image(_DATA_ROOT / "frontal" / "frontal-lower-3.jpeg"),
            "back": _uploaded_image(_DATA_ROOT / "posterior" / "posterior-feet-5.jpeg"),
            "left_arch": _uploaded_image(_DATA_ROOT / "lateral" / "arch-right-2.jpeg"),
            "right_arch": _uploaded_image(_DATA_ROOT / "lateral" / "arch-left-2.jpeg"),
        },
        include_placeholders=True,
    )

    assert result["metrics"]["arch_height_ratio_left"]["status"] == "placeholder"
    assert result["metrics"]["arch_height_ratio_right"]["status"] == "placeholder"
    assert result["metrics"]["arch_height_ratio_left"]["confidence"] == 0.0
    assert result["processing_by_view"]["left_arch"]["notes"]


def test_foot_progression_warns_when_capture_is_rotated() -> None:
    image = cv2.imread(str(_DATA_ROOT / "frontal" / "frontal-lower-3.jpeg"))
    assert image is not None
    rotation = cv2.getRotationMatrix2D((image.shape[1] // 2, image.shape[0] // 2), 18, 1.0)
    rotated = cv2.warpAffine(image, rotation, (image.shape[1], image.shape[0]), borderValue=(255, 255, 255))

    analysis = analyze_foot_progression_image(rotated)
    notes = analysis["metric_details"]["foot_progression_angle_right"]["quality_notes"]

    assert "camera tilt suspected" in notes or "partial foot contour" in notes
