"""Visual evidence generated from the anonymized squat overlay."""

from __future__ import annotations

from pathlib import Path

import cv2

from src.squat.contracts import SquatEventCapture
from src.squat.models import SquatSegmentationSummary

_EVENT_FIELDS = (
    ("inicio_descenso", "start_frame", "start_seconds"),
    ("maxima_profundidad", "peak_depth_frame", "peak_depth_seconds"),
    ("final_ascenso", "end_frame", "end_seconds"),
)


def generate_repetition_event_captures(
    overlay_video: str | Path,
    segmentation: SquatSegmentationSummary,
    *,
    output_dir: str | Path,
) -> list[SquatEventCapture]:
    """Export start, peak and end images from the anonymized overlay."""
    video_path = Path(overlay_video)
    if not video_path.is_file():
        raise FileNotFoundError(f"Squat overlay does not exist: {video_path}")

    destination = Path(output_dir)
    destination.mkdir(parents=True, exist_ok=True)
    capture = cv2.VideoCapture(str(video_path))
    if not capture.isOpened():
        capture.release()
        raise RuntimeError(f"Unable to open squat overlay: {video_path}")

    results: list[SquatEventCapture] = []
    try:
        for repetition in segmentation.repetitions:
            for event, frame_field, seconds_field in _EVENT_FIELDS:
                frame_index = int(getattr(repetition, frame_field))
                capture.set(cv2.CAP_PROP_POS_FRAMES, frame_index)
                readable, frame = capture.read()
                if not readable:
                    raise RuntimeError(
                        f"Unable to read frame {frame_index} from {video_path}"
                    )
                filename = (
                    f"rep_{repetition.repetition_index:02d}_"
                    f"{event}.png"
                )
                output_path = destination / filename
                if not cv2.imwrite(str(output_path), frame):
                    raise RuntimeError(f"Unable to write event capture: {output_path}")
                results.append(
                    SquatEventCapture(
                        repetition_index=repetition.repetition_index,
                        event=event,
                        frame_index=frame_index,
                        timestamp_seconds=float(getattr(repetition, seconds_field)),
                        relative_path=filename,
                    )
                )
    finally:
        capture.release()
    return results


__all__ = ["generate_repetition_event_captures"]
