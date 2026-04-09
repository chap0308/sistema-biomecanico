"""Tests for the integrated rest baseline pipeline."""

from __future__ import annotations

from pathlib import Path

from api.schemas.baseline import RestBaselineMultipartRequest, UploadedVideo
from api.schemas.image import UploadedStaticImage
from app.dependencies import get_rest_baseline_pipeline

_DATA_ROOT = Path("data/images/evaluations")
_VIDEO_ROOT = Path("data/videos/breathing_cycle_test")



def _uploaded_image(path: Path) -> UploadedStaticImage:
    return UploadedStaticImage(
        filename=path.name,
        content_type="image/jpeg",
        payload=path.read_bytes(),
    )



def _uploaded_video(path: Path) -> UploadedVideo:
    return UploadedVideo(
        filename=path.name,
        content_type="video/mp4",
        payload=path.read_bytes(),
    )



def test_rest_baseline_pipeline_with_real_assets_returns_breathing_group() -> None:
    pipeline = get_rest_baseline_pipeline()
    request = RestBaselineMultipartRequest(
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
        breathing_video=_uploaded_video(_VIDEO_ROOT / "respiracion.mp4"),
        include_placeholders=True,
        aggregation="median",
        frame_step=10,
        max_frames=12,
        reject_outliers=True,
    )

    result = pipeline.analyze(request)

    assert result["analysis_type"] == "rest_baseline"
    assert result["requested_groups"][-1] == "breathing_video"
    assert "breathing" in result["metrics_by_group"]
    assert "scapula_rest" in result["metrics_by_group"]
    assert set(result["metrics_by_group"]["isa"]["metrics"]) == {
        "infra_sternal_angle",
        "isa_static_baseline",
        "rib_flare_presence_score",
        "rib_flare_asymmetry",
        "left_costal_margin_angle",
        "right_costal_margin_angle",
        "costal_projection_index",
    }
    breathing_metrics = result["metrics_by_group"]["breathing"]["metrics"]
    assert set(breathing_metrics) == {"isa", "rib_flare", "thoracic_abdominal"}
    assert set(breathing_metrics["isa"]) == {"max_inhalation", "min_exhalation", "dynamic_delta"}
    assert set(breathing_metrics["rib_flare"]) == {
        "dynamic_asymmetry",
        "excursion_left",
        "excursion_right",
        "persistence_exhalation",
    }
    assert set(breathing_metrics["thoracic_abdominal"]) == {
        "dissociation_score",
        "phase_offset",
        "amplitude_ratio",
        "exhalation_mismatch",
        "upper_abdominal_excursion",
        "lower_thoracic_excursion",
    }
    assert breathing_metrics["isa"]["dynamic_delta"]["value"] is not None
    assert breathing_metrics["thoracic_abdominal"]["dissociation_score"]["value"] is not None
    assert result["metrics_by_group"]["breathing"]["signals"]["isa_source_of_truth"] == "breathing_video"
    assert result["metrics_by_group"]["breathing"]["time_series"]
    assert result["findings_by_group"]["foot_triptych"]["items"]
    assert result["findings_by_group"]["scapula_rest"]["status"] == "completed"
    assert result["deficiencies_by_group"]["scapula_rest"]["status"] == "completed"
    assert result["integrated_findings"]["status"] == "completed"
    assert result["preliminary_deficiencies"]["status"] == "completed"
    assert result["triggered_tests_next"]["status"] == "completed"
    assert result["baseline_scapular_state"]["status"] == "completed"
    assert set(result["baseline_scapula_context"]) == {"elevation_asymmetry", "protraction_bias", "winging_suspected", "rotation_asymmetry"}
    assert result["baseline_scapular_asymmetry"]["status"] == "completed"
    assert result["baseline_scapular_proxy_metrics"]["status"] == "completed"
    assert set(result["baseline_scapular_asymmetry"]["metrics"]) == {
        "scapular_elevation_difference",
        "scapular_symmetry_index",
    }
    assert "winging_index" in result["baseline_scapular_proxy_metrics"]["metrics"]
