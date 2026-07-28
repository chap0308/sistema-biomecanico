"""Visual evidence generated from the anonymized squat overlay."""

from __future__ import annotations

import csv
import math
from pathlib import Path
from typing import Mapping

import cv2

from src.squat.contracts import SquatEventCapture
from src.squat.models import (
    SquatFindingsSummary,
    SquatSegmentationSummary,
)
from src.squat.video_encoding import encode_h264_mp4

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


def generate_analysis_overlay_video(
    overlay_video: str | Path,
    frame_phases_csv: str | Path,
    frame_metrics_csv: str | Path,
    frame_quality_csv: str | Path,
    findings: SquatFindingsSummary,
    *,
    output_dir: str | Path,
) -> Path:
    """Add compact phase, quality, metric and rule evidence to the pose video."""
    source_path = Path(overlay_video)
    destination = Path(output_dir)
    destination.mkdir(parents=True, exist_ok=True)
    intermediate_path = destination / "analysis_overlay.intermediate.mp4"
    output_path = destination / "analysis_overlay.mp4"
    phases = _rows_by_frame(frame_phases_csv)
    metrics = _rows_by_frame(frame_metrics_csv)
    quality = _rows_by_frame(frame_quality_csv)
    decisions: dict[int, list[tuple[str, str]]] = {}
    for decision in findings.decisions:
        decisions.setdefault(decision.repetition_index, []).append(
            (decision.finding, decision.status)
        )

    capture = cv2.VideoCapture(str(source_path))
    if not capture.isOpened():
        capture.release()
        raise RuntimeError(f"Unable to open squat overlay: {source_path}")
    fps = float(capture.get(cv2.CAP_PROP_FPS))
    width = int(capture.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(capture.get(cv2.CAP_PROP_FRAME_HEIGHT))
    writer = cv2.VideoWriter(
        str(intermediate_path),
        cv2.VideoWriter_fourcc(*"mp4v"),
        fps,
        (width, height),
    )
    if not writer.isOpened():
        capture.release()
        raise RuntimeError(
            f"Unable to create analysis overlay: {intermediate_path}"
        )

    frame_index = 0
    try:
        while True:
            readable, frame = capture.read()
            if not readable:
                break
            _draw_analysis_panel(
                frame,
                frame_index=frame_index,
                phase=phases.get(frame_index, {}),
                metrics=metrics.get(frame_index, {}),
                quality=quality.get(frame_index, {}),
                decisions=decisions,
            )
            writer.write(frame)
            frame_index += 1
    finally:
        capture.release()
        writer.release()

    encode_h264_mp4(intermediate_path, output_path)
    return output_path


def _rows_by_frame(path: str | Path) -> dict[int, dict[str, str]]:
    with Path(path).open("r", encoding="utf-8-sig", newline="") as handle:
        rows = csv.DictReader(handle)
        return {
            int(row["frame_index"]): row
            for row in rows
            if row.get("frame_index")
        }


def _draw_analysis_panel(
    frame,
    *,
    frame_index: int,
    phase: Mapping[str, str],
    metrics: Mapping[str, str],
    quality: Mapping[str, str],
    decisions: Mapping[int, list[tuple[str, str]]],
) -> None:
    height, width = frame.shape[:2]
    margin = max(10, int(width * 0.015))
    panel_width = min(width - margin * 2, max(320, int(width * 0.44)))
    panel_height = min(height - margin * 2, max(176, int(height * 0.25)))
    cv2.rectangle(
        frame,
        (margin, margin),
        (margin + panel_width, margin + panel_height),
        (8, 14, 24),
        -1,
    )

    repetition = _integer(phase.get("repetition_index")) or 0
    phase_name = (phase.get("phase") or "reposo").replace("_", " ")
    valid = _boolean(quality.get("valid_for_analysis"))
    visibility = _number(quality.get("minimum_critical_visibility"))
    scale = max(0.42, min(0.72, width / 1400))
    line_height = max(23, int(30 * scale / 0.55))
    x = margin + 14
    y = margin + line_height
    header_color = (112, 231, 221)
    text_color = (235, 240, 247)
    muted_color = (170, 181, 195)
    quality_color = (93, 214, 125) if valid else (70, 170, 255)

    _put_text(
        frame,
        f"R{repetition or '-'} | {phase_name} | frame {frame_index}",
        (x, y),
        scale,
        header_color,
        bold=True,
    )
    y += line_height
    _put_text(
        frame,
        "Calidad: "
        f"{'valido' if valid else 'revision'} | vis {_format_number(visibility, 2)}",
        (x, y),
        scale,
        quality_color,
    )
    y += line_height
    _put_text(
        frame,
        "Tronco "
        f"{_format_metric(metrics.get('trunk_inclination_deg'), 'deg')}  "
        "Pelvis "
        f"{_format_metric(metrics.get('pelvis_lateral_shift_pct'), '%')}",
        (x, y),
        scale,
        text_color,
    )
    y += line_height
    _put_text(
        frame,
        "Rodilla I "
        f"{_format_metric(metrics.get('left_knee_medial_deviation_pct'), '%')}  "
        "D "
        f"{_format_metric(metrics.get('right_knee_medial_deviation_pct'), '%')}",
        (x, y),
        scale,
        text_color,
    )
    y += line_height
    _put_text(
        frame,
        "Diferencia bilateral "
        f"{_format_metric(metrics.get('bilateral_alignment_difference_pct'), '%')}",
        (x, y),
        scale,
        text_color,
    )
    if repetition in decisions:
        y += line_height
        present = sum(
            status == "presente" for _, status in decisions[repetition]
        )
        _put_text(
            frame,
            f"Reglas presentes: {present}/4 | umbrales provisionales",
            (x, min(y, margin + panel_height - 10)),
            scale * 0.9,
            muted_color,
        )


def _put_text(
    frame,
    text: str,
    origin: tuple[int, int],
    scale: float,
    color: tuple[int, int, int],
    *,
    bold: bool = False,
) -> None:
    cv2.putText(
        frame,
        text,
        origin,
        cv2.FONT_HERSHEY_SIMPLEX,
        scale,
        color,
        2 if bold else 1,
        cv2.LINE_AA,
    )


def _format_metric(value: str | None, unit: str) -> str:
    number = _number(value)
    return f"{number:.2f}{unit}" if number is not None else "--"


def _format_number(value: float | None, decimals: int) -> str:
    return f"{value:.{decimals}f}" if value is not None else "--"


def _number(value: str | None) -> float | None:
    if value is None or value == "":
        return None
    number = float(value)
    return number if math.isfinite(number) else None


def _integer(value: str | None) -> int | None:
    number = _number(value)
    return int(number) if number is not None else None


def _boolean(value: str | None) -> bool:
    return str(value).strip().lower() in {"true", "1", "yes", "si", "sí"}


__all__ = [
    "generate_analysis_overlay_video",
    "generate_repetition_event_captures",
]
