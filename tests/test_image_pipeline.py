"""Tests for the grouped static image pipeline and its subpipelines."""

from __future__ import annotations

from pathlib import Path

from api.schemas.image import ImageRestMultipartRequest, UploadedStaticImage
from app.dependencies import get_image_rest_pipeline

_DATA_ROOT = Path("data/images/evaluations")


def _uploaded_image(path: Path) -> UploadedStaticImage:
    return UploadedStaticImage(
        filename=path.name,
        content_type="image/jpeg",
        payload=path.read_bytes(),
    )


def _request_with_all_groups() -> ImageRestMultipartRequest:
    return ImageRestMultipartRequest(
        image_groups={
            "rest_phase1": {
                "front": _uploaded_image(_DATA_ROOT / "frontal" / "frontal-1.jpeg"),
                "side": _uploaded_image(_DATA_ROOT / "lateral" / "lateral-1.jpeg"),
                "back": _uploaded_image(_DATA_ROOT / "posterior" / "posterior-1.jpeg"),
            },
            "face": {
                "front_face": _uploaded_image(_DATA_ROOT / "face" / "face-1.jpeg"),
            },
            "foot_triptych": {
                "front": _uploaded_image(_DATA_ROOT / "feet" / "frontal" / "frontal-feet-1.jpeg"),
                "back": _uploaded_image(_DATA_ROOT / "feet" / "posterior" / "posterior-feet-1.jpeg"),
                "left_arch": _uploaded_image(_DATA_ROOT / "feet" / "lateral" / "arch-left-1.jpeg"),
                "right_arch": _uploaded_image(_DATA_ROOT / "feet" / "lateral" / "arch-right-1.jpeg"),
            },
            "isa": {
                "front_torso": _uploaded_image(_DATA_ROOT / "isa" / "isa-5.JPG"),
            },
            "scapula": {
                "back_upper_body": _uploaded_image(_DATA_ROOT / "escapula" / "escapula-1.jpeg"),
            },
        },
        include_placeholders=True,
    )


def test_image_pipeline_with_real_assets_returns_grouped_metrics() -> None:
    pipeline = get_image_rest_pipeline()

    result = pipeline.analyze(_request_with_all_groups())

    assert result["analysis_type"] == "rest"
    assert result["capture_mode"] == "multipart_image_groups"
    assert set(result["requested_groups"]) == {"rest_phase1", "face", "foot_triptych", "isa", "scapula"}
    assert result["findings"]["status"] == "pending"
    assert result["deficiencies"]["status"] == "pending"
    assert result["triggered_tests"]["status"] == "pending"

    rest_phase1 = result["groups"]["rest_phase1"]
    assert set(rest_phase1["metrics_by_view"]) == {"front", "side", "back"}
    assert set(rest_phase1["metrics_by_view"]["front"]["metrics"]) == {
        "shoulder_height_difference",
        "torso_lateral_tilt",
        "pelvic_tilt",
        "head_tilt_angle",
    }
    assert set(rest_phase1["metrics_by_view"]["side"]["metrics"]) == {
        "pelvic_ankle_sagittal_offset",
        "cranio_shoulder_angle",
        "forward_center_of_mass_offset",
        "shoulder_protraction_angle_left",
        "shoulder_protraction_angle_right",
        "thoracic_kyphosis_angle",
        "thoracic_flattening_index",
        "scapular_anterior_tilt_left",
        "scapular_anterior_tilt_right",
    }
    assert set(rest_phase1["metrics_by_view"]["back"]["metrics"]) == {
        "shoulder_height_difference",
        "torso_lateral_tilt",
        "pelvic_tilt",
        "head_tilt_angle",
    }

    face = result["groups"]["face"]
    assert set(face["metrics"]) == {"bipupilar_tilt", "mandibular_lateral_shift"}

    feet = result["groups"]["foot_triptych"]
    assert set(feet["processing_by_view"]) == {"front", "back", "left_arch", "right_arch"}
    assert set(feet["metrics"]) == {
        "foot_progression_angle_left",
        "foot_progression_angle_right",
        "calcaneal_angle_left",
        "calcaneal_angle_right",
        "arch_height_ratio_left",
        "arch_height_ratio_right",
    }

    isa = result["groups"]["isa"]
    assert set(isa["metrics"]) == {
        "infra_sternal_angle",
        "isa_static_baseline",
        "rib_flare_presence_score",
        "rib_flare_asymmetry",
        "left_costal_margin_angle",
        "right_costal_margin_angle",
        "costal_projection_index",
    }
    assert isa["metrics"]["infra_sternal_angle"]["status"] in {"computed", "low_confidence"}
    assert isa["metrics"]["infra_sternal_angle"]["value"] is not None
    assert isa["metrics"]["infra_sternal_angle"]["confidence"] is not None
    assert isa["metrics"]["rib_flare_presence_score"]["value"] is not None

    scapula = result["groups"]["scapula"]
    assert "winging_index" in scapula["metrics"]
    assert "cranio_shoulder_angle" not in scapula["metrics"]


def test_image_pipeline_can_run_individual_group_only() -> None:
    pipeline = get_image_rest_pipeline()
    request = ImageRestMultipartRequest(
        image_groups={
            "face": {
                "front_face": _uploaded_image(_DATA_ROOT / "face" / "face-1.jpeg"),
            }
        },
        include_placeholders=True,
    )

    result = pipeline.analyze(request)

    assert result["requested_groups"] == ["face"]
    assert set(result["groups"]) == {"face"}
    assert set(result["groups"]["face"]["metrics"]) == {"bipupilar_tilt", "mandibular_lateral_shift"}

