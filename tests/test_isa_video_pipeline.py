"""Tests for the dedicated ISA plus breathing pipeline."""

from __future__ import annotations

from pathlib import Path

from api.schemas.baseline import UploadedVideo
from api.schemas.image import UploadedStaticImage
from api.schemas.isa import IsaVideoMultipartRequest
from app.dependencies import get_isa_video_pipeline

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



def test_isa_video_pipeline_with_real_assets_returns_isa_and_breathing_groups() -> None:
    pipeline = get_isa_video_pipeline()
    request = IsaVideoMultipartRequest(
        isa_image=_uploaded_image(_DATA_ROOT / "isa" / "isa-5.JPG"),
        breathing_video=_uploaded_video(_VIDEO_ROOT / "respiracion.mp4"),
        include_placeholders=True,
        aggregation="median",
        frame_step=10,
        max_frames=12,
        reject_outliers=True,
    )

    result = pipeline.analyze(request)

    assert result["analysis_type"] == "isa_video"
    assert result["requested_groups"] == ["isa", "breathing_video"]
    assert set(result["metrics_by_group"]) == {"isa", "breathing"}
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
    assert "max_inhalation_frame" in result["metrics_by_group"]["breathing"]["key_frames"]
