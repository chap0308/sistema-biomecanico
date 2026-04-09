"""Video preprocessing utilities before pose extraction."""

from pathlib import Path


def prepare_video_for_analysis(video_path: Path) -> Path:
    """Normalize input video and return process-ready path.

    TODO:
    - Validate codec/resolution/fps constraints.
    - Add optional trimming and frame extraction pipeline.
    - Persist derived artifacts required by pose estimation.
    """
    return video_path

