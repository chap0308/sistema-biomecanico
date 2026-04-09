"""OpenCV helpers for ISA, breathing and static-image debug overlays."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import cv2
import numpy as np

from orchestration.rest_temporal import sample_indexed_video_frames

_STATIC_TEXT_ORDER = [
    ("isa_static_baseline", "ISA baseline"),
    ("left_costal_margin_angle", "Left margin"),
    ("right_costal_margin_angle", "Right margin"),
    ("costal_projection_index", "Projection"),
    ("rib_flare_presence_score", "Rib flare"),
    ("confidence", "Confidence"),
]

_VIDEO_TEXT_ORDER = [
    ("isa", "ISA"),
    ("rib_flare_score", "Rib flare"),
    ("thoracic_abdominal_dissociation", "T/A dissociation"),
]

_REST_VIEW_TEXT_ORDER = {
    "front": [
        ("shoulder_height_difference", "Shoulder diff"),
        ("torso_lateral_tilt", "Torso tilt"),
        ("pelvic_tilt", "Pelvic tilt"),
        ("head_tilt_angle", "Head tilt"),
    ],
    "side": [
        ("pelvic_ankle_sagittal_offset", "Pelvis-ankle"),
        ("cranio_shoulder_angle", "Cranio-shoulder"),
        ("forward_center_of_mass_offset", "COM forward"),
        ("shoulder_protraction_angle_left", "Protraction L"),
        ("shoulder_protraction_angle_right", "Protraction R"),
        ("thoracic_kyphosis_angle", "Thoracic kyphosis"),
        ("thoracic_flattening_index", "Thoracic flattening"),
    ],
    "back": [
        ("shoulder_height_difference", "Shoulder diff"),
        ("torso_lateral_tilt", "Torso tilt"),
        ("pelvic_tilt", "Pelvic tilt"),
        ("head_tilt_angle", "Head tilt"),
    ],
}

_FACE_TEXT_ORDER = [
    ("bipupilar_tilt", "Bipupilar tilt"),
    ("mandibular_lateral_shift", "Mandibular shift"),
]

_FOOT_TEXT_ORDER = {
    "front": [
        ("foot_progression_angle_left", "Foot progression L"),
        ("foot_progression_angle_right", "Foot progression R"),
    ],
    "back": [
        ("calcaneal_angle_left", "Calcaneal L"),
        ("calcaneal_angle_right", "Calcaneal R"),
    ],
    "left_arch": [("arch_height_ratio_left", "Arch height L")],
    "right_arch": [("arch_height_ratio_right", "Arch height R")],
}

_SCAPULA_TEXT_ORDER = [
    ("scapular_elevation_difference", "Elevation diff"),
    ("scapula_spine_distance_left", "Spine dist L"),
    ("scapula_spine_distance_right", "Spine dist R"),
    ("scapular_symmetry_index", "Symmetry index"),
    ("scapular_internal_rotation_left", "Internal rot L"),
    ("scapular_internal_rotation_right", "Internal rot R"),
    ("scapular_upward_rotation_left", "Upward rot L"),
    ("scapular_upward_rotation_right", "Upward rot R"),
    ("winging_index", "Winging index"),
]

_LAYER_STYLES = {
    "landmarks": {"point_color": (90, 210, 255), "highlight_color": (90, 210, 255), "line_color": (90, 210, 255)},
    "head_neck": {"point_color": (255, 200, 90), "highlight_color": (255, 160, 40), "line_color": (255, 200, 90)},
    "torso_pelvis": {"point_color": (0, 200, 255), "highlight_color": (0, 140, 255), "line_color": (0, 255, 200)},
    "shoulder_scapula": {"point_color": (160, 120, 255), "highlight_color": (120, 80, 255), "line_color": (200, 140, 255)},
    "support_axis": {"point_color": (120, 240, 120), "highlight_color": (40, 200, 40), "line_color": (120, 240, 120)},
    "spine_reference": {"point_color": (0, 200, 255), "highlight_color": (0, 140, 255), "line_color": (0, 255, 200)},
    "scapula_distance": {"point_color": (255, 215, 0), "highlight_color": (255, 180, 0), "line_color": (255, 230, 0)},
    "internal_rotation": {"point_color": (255, 160, 110), "highlight_color": (255, 120, 60), "line_color": (255, 160, 110)},
    "upward_rotation": {"point_color": (170, 120, 255), "highlight_color": (140, 90, 255), "line_color": (200, 150, 255)},
    "fallback": {"point_color": (90, 210, 255), "highlight_color": (0, 140, 255), "line_color": (0, 255, 200)},
}


def save_static_overlay_image(
    image_path: Path,
    isa_group: dict[str, Any],
    output_path: Path,
) -> Path:
    """Annotate the frontal ISA image with landmarks and metric labels."""
    image = cv2.imread(str(image_path))
    if image is None:
        raise ValueError(f"Unable to read image for overlay: {image_path}")

    metrics = isa_group.get("metrics", {})
    baseline = metrics.get("isa_static_baseline") or metrics.get("infra_sternal_angle") or {}
    landmarks = baseline.get("landmarks") or _find_any_landmarks(metrics)
    if landmarks is not None:
        _draw_landmarks_and_angle(image, landmarks)

    lines = []
    for metric_name, label in _STATIC_TEXT_ORDER:
        if metric_name == "confidence":
            value = baseline.get("confidence")
        else:
            value = metrics.get(metric_name, {}).get("value")
        if value is None:
            continue
        lines.append(f"{label}: {_format_value(value)}")
    _draw_info_panel(image, lines, header="Static ISA")

    output_path.parent.mkdir(parents=True, exist_ok=True)
    cv2.imwrite(str(output_path), image)
    return output_path


def save_rest_phase1_overlay_image(
    image_path: Path,
    rest_group: dict[str, Any],
    view_name: str,
    output_path: Path,
    *,
    overlay_mode: str = "readable",
    enabled_layers: set[str] | None = None,
) -> Path:
    """Annotate one rest_phase1 static image using grouped debug metadata."""
    image = _read_image(image_path)
    debug_by_view = rest_group.get("debug_by_view", {})
    debug_payload = debug_by_view.get(view_name, {})
    _draw_debug_overlay(image, debug_payload, overlay_mode=overlay_mode, enabled_layers=enabled_layers)
    metrics = rest_group.get("metrics_by_view", {}).get(view_name, {}).get("metrics", {})
    header = f"Rest {view_name} ({overlay_mode})"
    _draw_info_panel(image, _metric_lines(metrics, _REST_VIEW_TEXT_ORDER.get(view_name, [])), header=header)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    cv2.imwrite(str(output_path), image)
    return output_path


def save_face_overlay_image(image_path: Path, face_group: dict[str, Any], output_path: Path) -> Path:
    """Annotate the static face image using FaceMesh debug metadata."""
    image = _read_image(image_path)
    debug_payload = face_group.get("debug", {})
    _draw_face_mesh(image, debug_payload.get("landmarks", []))
    _draw_debug_overlay(image, debug_payload, draw_landmarks=False)
    _draw_info_panel(image, _metric_lines(face_group.get("metrics", {}), _FACE_TEXT_ORDER), header="Face")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    cv2.imwrite(str(output_path), image)
    return output_path


def save_foot_triptych_overlay_image(
    image_path: Path,
    foot_group: dict[str, Any],
    view_name: str,
    output_path: Path,
) -> Path:
    """Annotate one foot image using contour-based debug metadata."""
    image = _read_image(image_path)
    debug_payload = foot_group.get("debug_by_view", {}).get(view_name, {})
    _draw_debug_overlay(image, debug_payload)
    _draw_info_panel(image, _metric_lines(foot_group.get("metrics", {}), _FOOT_TEXT_ORDER.get(view_name, [])), header=f"Foot {view_name}")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    cv2.imwrite(str(output_path), image)
    return output_path


def save_scapula_overlay_image(
    image_path: Path,
    scapula_group: dict[str, Any],
    output_path: Path,
    *,
    overlay_mode: str = "readable",
    enabled_layers: set[str] | None = None,
) -> Path:
    """Annotate the scapula image using grouped debug metadata."""
    image = _read_image(image_path)
    debug_payload = scapula_group.get("debug", {})
    _draw_debug_overlay(image, debug_payload, overlay_mode=overlay_mode, enabled_layers=enabled_layers)
    _draw_info_panel(image, _metric_lines(scapula_group.get("metrics", {}), _SCAPULA_TEXT_ORDER), header=f"Scapula ({overlay_mode})")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    cv2.imwrite(str(output_path), image)
    return output_path


def save_breathing_overlay_video(
    video_path: Path,
    breathing_group: dict[str, Any],
    output_path: Path,
    *,
    max_frames: int,
    frame_step: int,
) -> Path:
    """Build an annotated video from sampled breathing frames."""
    annotated_frames = _build_annotated_breathing_frames(
        video_path,
        breathing_group,
        max_frames=max_frames,
        frame_step=frame_step,
    )
    if not annotated_frames:
        raise ValueError(f"Unable to sample frames from video: {video_path}")

    first_frame = annotated_frames[0][1]
    height, width = first_frame.shape[:2]
    output_path.parent.mkdir(parents=True, exist_ok=True)
    writer = cv2.VideoWriter(
        str(output_path),
        cv2.VideoWriter_fourcc(*"mp4v"),
        6.0,
        (width, height),
    )
    if not writer.isOpened():
        raise ValueError(f"Unable to create annotated video: {output_path}")

    try:
        for _, frame in annotated_frames:
            writer.write(frame)
    finally:
        writer.release()
    return output_path


def save_breathing_overlay_frames(
    video_path: Path,
    breathing_group: dict[str, Any],
    output_dir: Path,
    *,
    max_frames: int,
    frame_step: int,
) -> list[Path]:
    """Save each annotated sampled frame as an individual PNG."""
    annotated_frames = _build_annotated_breathing_frames(
        video_path,
        breathing_group,
        max_frames=max_frames,
        frame_step=frame_step,
    )
    if not annotated_frames:
        raise ValueError(f"Unable to sample frames from video: {video_path}")

    output_dir.mkdir(parents=True, exist_ok=True)
    saved_paths: list[Path] = []
    for frame_index, frame in annotated_frames:
        output_path = output_dir / f"frame_{frame_index:04d}.png"
        cv2.imwrite(str(output_path), frame)
        saved_paths.append(output_path)
    return saved_paths


def save_breathing_overlay_preview(
    video_path: Path,
    breathing_group: dict[str, Any],
    output_path: Path,
    *,
    max_frames: int,
    frame_step: int,
) -> Path:
    """Build a contact-sheet PNG preview of the annotated breathing frames."""
    annotated_frames = _build_annotated_breathing_frames(
        video_path,
        breathing_group,
        max_frames=max_frames,
        frame_step=frame_step,
    )
    if not annotated_frames:
        raise ValueError(f"Unable to sample frames from video: {video_path}")

    selected = _select_preview_frames(annotated_frames, target_count=6)
    preview = _compose_contact_sheet(selected, title="Annotated Breathing Preview")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    cv2.imwrite(str(output_path), preview)
    return output_path


def resolve_rest_overlay_layers(
    debug_payload: dict[str, Any],
    *,
    overlay_mode: str = "readable",
    enabled_layers: set[str] | None = None,
) -> dict[str, dict[str, Any]]:
    """Resolve the layer subset that should be rendered for a rest overlay."""
    layers = debug_payload.get("layers")
    if not isinstance(layers, dict):
        return {}

    available = [str(name) for name in debug_payload.get("available_layers", list(layers.keys()))]
    overlay_modes = debug_payload.get("overlay_modes", {})
    default_selection = overlay_modes.get(overlay_mode) or available
    if enabled_layers is None:
        selected_names = [name for name in default_selection if name in layers]
    else:
        selected_names = [name for name in available if name in enabled_layers and name in layers]
        if not selected_names:
            selected_names = [name for name in default_selection if name in layers]
    return {name: layers[name] for name in selected_names}


def _build_annotated_breathing_frames(
    video_path: Path,
    breathing_group: dict[str, Any],
    *,
    max_frames: int,
    frame_step: int,
) -> list[tuple[int, np.ndarray]]:
    sampled_frames = sample_indexed_video_frames(video_path, max_frames=max_frames, frame_step=frame_step)
    frame_map = {int(item["frame_index"]): item for item in breathing_group.get("time_series", [])}
    key_frames = breathing_group.get("key_frames", {})
    annotated_frames: list[tuple[int, np.ndarray]] = []
    for frame_index, frame in sampled_frames:
        annotated = frame.copy()
        series_item = frame_map.get(frame_index, {"frame_index": frame_index})
        landmarks = series_item.get("landmarks")
        if landmarks is not None:
            _draw_landmarks_and_angle(annotated, landmarks)
        labels = _build_key_frame_labels(frame_index, key_frames)
        if labels:
            _draw_frame_banner(annotated, labels)
        lines = [f"Frame: {frame_index}"]
        for metric_name, label in _VIDEO_TEXT_ORDER:
            value = series_item.get(metric_name)
            if value is not None:
                lines.append(f"{label}: {_format_value(value)}")
        _draw_info_panel(annotated, lines, header="Breathing")
        annotated_frames.append((frame_index, annotated))
    return annotated_frames


def _read_image(image_path: Path) -> np.ndarray:
    image = cv2.imread(str(image_path))
    if image is None:
        raise ValueError(f"Unable to read image for overlay: {image_path}")
    return image


def _draw_debug_overlay(
    image: np.ndarray,
    debug_payload: dict[str, Any],
    *,
    draw_landmarks: bool = True,
    overlay_mode: str = "full",
    enabled_layers: set[str] | None = None,
) -> None:
    resolved_layers = resolve_rest_overlay_layers(
        debug_payload,
        overlay_mode=overlay_mode,
        enabled_layers=enabled_layers,
    )
    if resolved_layers:
        for layer_name, layer_payload in resolved_layers.items():
            style = _LAYER_STYLES.get(layer_name, _LAYER_STYLES["fallback"])
            if layer_name == "landmarks" and not draw_landmarks:
                continue
            _draw_named_points(image, layer_payload.get("points", {}), color=style["point_color"], radius=4)
            _draw_named_points(
                image,
                layer_payload.get("highlighted_points", {}),
                color=style["highlight_color"],
                radius=6,
            )
            _draw_reference_lines(image, layer_payload.get("reference_lines", []), color=style["line_color"])
        return

    if draw_landmarks:
        _draw_named_points(image, debug_payload.get("landmarks", {}), color=(90, 210, 255), radius=4)
    _draw_named_points(image, debug_payload.get("highlighted_points", {}), color=(0, 140, 255), radius=7)
    _draw_reference_lines(image, debug_payload.get("reference_lines", []), color=(0, 255, 200))
    _draw_polylines(image, debug_payload.get("contours", []), color=(120, 240, 120))
    points_used = debug_payload.get("points_used", {})
    if isinstance(points_used, dict):
        _draw_named_points(image, points_used, color=(255, 180, 40), radius=6)


def _draw_face_mesh(image: np.ndarray, points: list[dict[str, Any]]) -> None:
    for point in points:
        pixel = _point_to_pixel(image, point)
        cv2.circle(image, pixel, 1, (160, 160, 255), -1)


def _draw_named_points(image: np.ndarray, points: Any, *, color: tuple[int, int, int], radius: int) -> None:
    if isinstance(points, list):
        iterable = [("", point) for point in points]
    elif isinstance(points, dict):
        iterable = list(points.items())
    else:
        return
    for label, point in iterable:
        if not isinstance(point, dict) or point.get("x") is None or point.get("y") is None:
            continue
        pixel = _point_to_pixel(image, point)
        cv2.circle(image, pixel, radius, color, -1)
        cv2.circle(image, pixel, radius + 2, (255, 255, 255), 1)
        if label:
            cv2.putText(image, str(label), (pixel[0] + 6, pixel[1] - 6), cv2.FONT_HERSHEY_SIMPLEX, 0.42, color, 1)


def _draw_reference_lines(image: np.ndarray, lines: list[dict[str, Any]], *, color: tuple[int, int, int]) -> None:
    for line in lines:
        if not isinstance(line, dict):
            continue
        start = line.get("start")
        end = line.get("end")
        if not isinstance(start, dict) or not isinstance(end, dict):
            continue
        start_px = _point_to_pixel(image, start)
        end_px = _point_to_pixel(image, end)
        cv2.line(image, start_px, end_px, color, 2)
        label = line.get("label")
        if label:
            mid_x = int((start_px[0] + end_px[0]) / 2)
            mid_y = int((start_px[1] + end_px[1]) / 2)
            cv2.putText(image, str(label), (mid_x + 4, mid_y - 4), cv2.FONT_HERSHEY_SIMPLEX, 0.4, color, 1)


def _draw_polylines(image: np.ndarray, contours: list[dict[str, Any]], *, color: tuple[int, int, int]) -> None:
    for contour in contours:
        if not isinstance(contour, dict):
            continue
        points = contour.get("points")
        if not isinstance(points, list) or len(points) < 2:
            continue
        pixels = np.array([_point_to_pixel(image, point) for point in points], dtype=np.int32)
        cv2.polylines(image, [pixels], isClosed=True, color=color, thickness=2)


def _select_preview_frames(
    frames: list[tuple[int, np.ndarray]],
    *,
    target_count: int,
) -> list[tuple[int, np.ndarray]]:
    if len(frames) <= target_count:
        return frames
    indices = np.linspace(0, len(frames) - 1, num=target_count, dtype=int)
    return [frames[index] for index in indices.tolist()]


def _compose_contact_sheet(frames: list[tuple[int, np.ndarray]], *, title: str) -> np.ndarray:
    margin = 20
    header_height = 70
    thumb_width = 360
    thumb_height = 640
    columns = 3
    rows = int(np.ceil(len(frames) / columns))
    canvas_width = margin + columns * (thumb_width + margin)
    canvas_height = header_height + margin + rows * (thumb_height + 50 + margin)
    canvas = np.full((canvas_height, canvas_width, 3), 24, dtype=np.uint8)
    cv2.putText(canvas, title, (margin, 42), cv2.FONT_HERSHEY_SIMPLEX, 1.0, (255, 255, 255), 2)

    for index, (frame_index, frame) in enumerate(frames):
        row = index // columns
        column = index % columns
        x = margin + column * (thumb_width + margin)
        y = header_height + row * (thumb_height + 50 + margin)
        resized = cv2.resize(frame, (thumb_width, thumb_height))
        canvas[y:y + thumb_height, x:x + thumb_width] = resized
        cv2.putText(canvas, f"Frame {frame_index}", (x, y + thumb_height + 30), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (230, 230, 230), 2)
    return canvas


def _find_any_landmarks(metrics: dict[str, Any]) -> dict[str, Any] | None:
    for metric in metrics.values():
        if isinstance(metric, dict) and metric.get("landmarks"):
            return metric["landmarks"]
    return None


def _draw_landmarks_and_angle(image: np.ndarray, landmarks: dict[str, Any]) -> None:
    points = {
        name: _point_to_pixel(image, value)
        for name, value in landmarks.items()
        if isinstance(value, dict) and value.get("x") is not None and value.get("y") is not None
    }
    required_names = {"left_costal_margin", "substernal_vertex", "right_costal_margin"}
    if not required_names.issubset(points):
        return

    left = points["left_costal_margin"]
    vertex = points["substernal_vertex"]
    right = points["right_costal_margin"]
    cv2.line(image, vertex, left, (0, 255, 255), 2)
    cv2.line(image, vertex, right, (0, 255, 255), 2)
    for point in points.values():
        cv2.circle(image, point, 6, (0, 140, 255), -1)
        cv2.circle(image, point, 8, (255, 255, 255), 1)


def _point_to_pixel(image: np.ndarray, point: dict[str, Any]) -> tuple[int, int]:
    height, width = image.shape[:2]
    return int(round(float(point["x"]) * width)), int(round(float(point["y"]) * height))


def _metric_lines(metrics: dict[str, Any], order: list[tuple[str, str]]) -> list[str]:
    lines: list[str] = []
    for metric_name, label in order:
        metric = metrics.get(metric_name, {}) if isinstance(metrics, dict) else {}
        if not isinstance(metric, dict):
            continue
        lines.append(_format_metric_line(label, metric))
    return [line for line in lines if line]


def _format_metric_line(label: str, metric: dict[str, Any]) -> str:
    value = metric.get("value")
    status = metric.get("status")
    if value is None and not status:
        return ""
    rendered = "n/a" if value is None else _format_value(value)
    suffix = ""
    if status in {"low_confidence", "placeholder"}:
        suffix = f" [{status}]"
    return f"{label}: {rendered}{suffix}"


def _draw_info_panel(image: np.ndarray, lines: list[str], *, header: str) -> None:
    if not lines:
        return
    margin = 20
    line_height = 26
    panel_width = 420
    panel_height = 36 + line_height * len(lines)
    top_left = (margin, margin)
    bottom_right = (margin + panel_width, margin + panel_height)
    overlay = image.copy()
    cv2.rectangle(overlay, top_left, bottom_right, (20, 20, 20), -1)
    cv2.addWeighted(overlay, 0.55, image, 0.45, 0, image)
    cv2.putText(image, header, (margin + 14, margin + 24), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
    for index, line in enumerate(lines, start=1):
        y = margin + 24 + index * line_height
        cv2.putText(image, line, (margin + 14, y), cv2.FONT_HERSHEY_SIMPLEX, 0.58, (230, 230, 230), 1)


def _draw_frame_banner(image: np.ndarray, labels: list[str]) -> None:
    banner_text = " | ".join(labels)
    overlay = image.copy()
    cv2.rectangle(overlay, (20, image.shape[0] - 60), (min(image.shape[1] - 20, 760), image.shape[0] - 20), (10, 80, 180), -1)
    cv2.addWeighted(overlay, 0.6, image, 0.4, 0, image)
    cv2.putText(
        image,
        banner_text,
        (34, image.shape[0] - 32),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.7,
        (255, 255, 255),
        2,
    )


def _build_key_frame_labels(frame_index: int, key_frames: dict[str, Any]) -> list[str]:
    labels: list[str] = []
    if frame_index == key_frames.get("max_inhalation_frame"):
        labels.append("Max inhalation")
    if frame_index == key_frames.get("max_exhalation_frame"):
        labels.append("Max exhalation")
    if frame_index == key_frames.get("rib_flare_persistence_frame"):
        labels.append("Rib flare persistence")
    if frame_index == key_frames.get("thoracic_abdominal_exhalation_frame"):
        labels.append("T/A exhalation")
    return labels


def _format_value(value: Any) -> str:
    if isinstance(value, float):
        return f"{value:.3f}"
    return str(value)



_MOVEMENT_TEXT_ORDER_READABLE = [
    ("humeral_abduction_angle_left", "Hum abd L"),
    ("humeral_abduction_angle_right", "Hum abd R"),
    ("scapular_elevation_dynamic_left", "Sc elev L"),
    ("scapular_elevation_dynamic_right", "Sc elev R"),
    ("dynamic_elevation_asymmetry", "Elev asym"),
    ("scapular_upward_rotation_dynamic_left", "Up rot L"),
    ("scapular_upward_rotation_dynamic_right", "Up rot R"),
]

_MOVEMENT_TEXT_ORDER_FULL = _MOVEMENT_TEXT_ORDER_READABLE + [
    ("dynamic_upward_rotation_asymmetry", "Up rot asym"),
    ("scapular_internal_rotation_dynamic_left", "Protr L"),
    ("scapular_internal_rotation_dynamic_right", "Protr R"),
    ("dynamic_protraction_asymmetry", "Protr asym"),
    ("dynamic_winging_left", "Wing L"),
    ("dynamic_winging_right", "Wing R"),
    ("dynamic_winging_asymmetry", "Wing asym"),
    ("scapulohumeral_ratio_left", "SH ratio L"),
    ("scapulohumeral_ratio_right", "SH ratio R"),
]


def save_movement_overlay_video(
    video_path: Path,
    movement_payload: dict[str, Any],
    output_path: Path,
    *,
    max_frames: int,
    frame_step: int,
    overlay_mode: str = "readable",
) -> Path:
    """Build an annotated posterior movement video from sampled frames."""
    annotated_frames = _build_annotated_movement_frames(
        video_path,
        movement_payload,
        max_frames=max_frames,
        frame_step=frame_step,
        overlay_mode=overlay_mode,
    )
    if not annotated_frames:
        raise ValueError(f"Unable to sample frames from video: {video_path}")

    first_frame = annotated_frames[0][1]
    height, width = first_frame.shape[:2]
    output_path.parent.mkdir(parents=True, exist_ok=True)
    writer = cv2.VideoWriter(str(output_path), cv2.VideoWriter_fourcc(*"mp4v"), 6.0, (width, height))
    if not writer.isOpened():
        raise ValueError(f"Unable to create annotated video: {output_path}")
    try:
        for _, frame in annotated_frames:
            writer.write(frame)
    finally:
        writer.release()
    return output_path


def _build_annotated_movement_frames(
    video_path: Path,
    movement_payload: dict[str, Any],
    *,
    max_frames: int,
    frame_step: int,
    overlay_mode: str,
) -> list[tuple[int, np.ndarray]]:
    sampled_frames = sample_indexed_video_frames(video_path, max_frames=max_frames, frame_step=frame_step)
    frame_map = {int(item["frame_index"]): item for item in movement_payload.get("time_series", []) if isinstance(item, dict) and item.get("frame_index") is not None}
    key_frames = movement_payload.get("key_frames", {}) if isinstance(movement_payload, dict) else {}
    annotated_frames: list[tuple[int, np.ndarray]] = []
    for frame_index, frame in sampled_frames:
        row = frame_map.get(frame_index)
        if not isinstance(row, dict):
            continue
        annotated = frame.copy()
        _draw_movement_frame_overlay(annotated, row, key_frames=key_frames, overlay_mode=overlay_mode)
        annotated_frames.append((frame_index, annotated))
    return annotated_frames


def _draw_movement_frame_overlay(
    image: np.ndarray,
    series_item: dict[str, Any],
    *,
    key_frames: dict[str, Any],
    overlay_mode: str,
) -> None:
    landmarks = series_item.get("landmarks", {}) if isinstance(series_item, dict) else {}
    reference_lines = series_item.get("reference_lines", []) if isinstance(series_item, dict) else []
    if isinstance(landmarks, dict):
        _draw_named_points(image, landmarks, color=(90, 210, 255), radius=4)
    if isinstance(reference_lines, list):
        if overlay_mode == "readable":
            filtered_lines = [line for line in reference_lines if line.get("label") in {"torso_axis", "humerus_axis_left", "humerus_axis_right", "biacromial_line"}]
        else:
            filtered_lines = reference_lines
        _draw_reference_lines(image, filtered_lines, color=(0, 255, 200))

    labels = _build_movement_key_frame_labels(int(series_item.get("frame_index", -1)), key_frames)
    if labels:
        _draw_frame_banner(image, labels)

    lines = [f"Frame: {series_item.get('frame_index')}"]
    phase = series_item.get("phase")
    if phase:
        lines.append(f"Phase: {phase}")
    for metric_name, label in (_MOVEMENT_TEXT_ORDER_READABLE if overlay_mode == "readable" else _MOVEMENT_TEXT_ORDER_FULL):
        value = series_item.get(metric_name)
        if value is None:
            continue
        lines.append(f"{label}: {_format_value(value)}")
    _draw_info_panel(image, lines, header=f"Shoulder Abduction ({overlay_mode})")


def _build_movement_key_frame_labels(frame_index: int, key_frames: dict[str, Any]) -> list[str]:
    labels: list[str] = []
    if frame_index == key_frames.get("movement_start_frame"):
        labels.append("Movement start")
    if frame_index == key_frames.get("truncated_clip_frame"):
        labels.append("Late clip start")
    if frame_index == key_frames.get("left_onset_frame"):
        labels.append("Left onset")
    if frame_index == key_frames.get("right_onset_frame"):
        labels.append("Right onset")
    if frame_index == key_frames.get("peak_frame"):
        labels.append("Peak abduction")
    if frame_index == key_frames.get("descent_start_frame"):
        labels.append("Descent")
    return labels
