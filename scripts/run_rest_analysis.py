"""Run the analysis API endpoints against local image or video files."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
from typing import Any

from fastapi.testclient import TestClient

ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

SCRIPTS_DIR = Path(__file__).resolve().parent
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

from app.dependencies import get_movement_pipeline
from app.main import app
from debug_utils.plotting import (
    save_debug_plots,
    save_group_metrics_csvs,
    save_movement_debug_plots,
    save_movement_time_series_csv,
    save_static_debug_plots,
    save_time_series_csv,
)
from debug_utils.visualization import (
    save_breathing_overlay_frames,
    save_breathing_overlay_preview,
    save_breathing_overlay_video,
    save_face_overlay_image,
    save_foot_triptych_overlay_image,
    save_rest_phase1_overlay_image,
    save_scapula_overlay_image,
    save_static_overlay_image,
)

_VIDEO_SUFFIXES = {".mp4", ".mov", ".avi", ".mkv", ".webm"}
_GROUP_FIELD_FLAGS = {
    "rest_phase1_front": "rest-phase1-front",
    "rest_phase1_side": "rest-phase1-side",
    "rest_phase1_back": "rest-phase1-back",
    "face_front_face": "face-front-face",
    "foot_triptych_front": "foot-triptych-front",
    "foot_triptych_back": "foot-triptych-back",
    "foot_triptych_left_arch": "foot-triptych-left-arch",
    "foot_triptych_right_arch": "foot-triptych-right-arch",
    "isa_front_torso": "isa-front-torso",
    "scapula_back_upper_body": "scapula-back-upper-body",
}


def build_parser() -> argparse.ArgumentParser:
    """Create the CLI parser."""
    parser = argparse.ArgumentParser(
        description="Run image and video analysis endpoints against local media files.",
    )
    parser.add_argument(
        "inputs",
        nargs="*",
        type=Path,
        help="Optional legacy mode: one or more image/video paths.",
    )
    parser.add_argument(
        "--rest-video",
        type=Path,
        help="Single rotating rest video for `/api/v1/analyze/video/rest`.",
    )
    parser.add_argument(
        "--movement-type",
        default=None,
        help="Dedicated movement type for `/api/v1/analyze/video/movement`, e.g. 'shoulder_abduction'.",
    )
    parser.add_argument(
        "--movement-back-video",
        type=Path,
        help="Posterior movement video for `/api/v1/analyze/video/movement`.",
    )
    parser.add_argument(
        "--movement-front-video",
        type=Path,
        help="Optional frontal movement video for `/api/v1/analyze/video/movement`.",
    )
    parser.add_argument(
        "--prior-analysis-json",
        type=Path,
        help="Optional JSON file sent as `prior_analysis` to `/api/v1/analyze/video/movement`.",
    )
    parser.add_argument(
        "--breathing-video",
        type=Path,
        help="Mandatory breathing video for `/api/v1/analyze/rest/baseline`.",
    )
    parser.add_argument(
        "--view",
        choices=("front", "back", "side"),
        default=None,
        help="Override the anatomical view for legacy single-file requests.",
    )
    parser.add_argument(
        "--include-placeholders",
        action=argparse.BooleanOptionalAction,
        default=True,
        help="Include placeholder metrics in the response.",
    )
    parser.add_argument(
        "--video-analysis-type",
        default="rest",
        help="Video test type for legacy video inputs. Defaults to 'rest'.",
    )
    parser.add_argument(
        "--aggregation",
        choices=("mean", "median"),
        default="median",
        help="Temporal aggregation strategy for video inputs.",
    )
    parser.add_argument(
        "--frame-step",
        type=int,
        default=10,
        help="Sample every Nth frame when processing videos.",
    )
    parser.add_argument(
        "--max-frames",
        type=int,
        default=18,
        help="Maximum number of frames to analyze per video.",
    )
    parser.add_argument(
        "--reject-outliers",
        action=argparse.BooleanOptionalAction,
        default=True,
        help="Drop simple temporal outliers before aggregating video metrics.",
    )
    for field_name, flag_name in _GROUP_FIELD_FLAGS.items():
        parser.add_argument(
            f"--{flag_name}",
            type=Path,
            dest=field_name,
            help=f"Path for multipart field '{field_name}'.",
        )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Print the full JSON response.",
    )
    parser.add_argument(
        "--save-json",
        action="store_true",
        help="Save the response payload as response.json.",
    )
    parser.add_argument(
        "--save-overlay-image",
        action="store_true",
        help="Save an annotated ISA frontal image when available.",
    )
    parser.add_argument(
        "--save-overlay-video",
        action="store_true",
        help="Save an annotated breathing video when available.",
    )
    parser.add_argument(
        "--save-csv",
        action="store_true",
        help="Save breathing time series as frame_metrics.csv.",
    )
    parser.add_argument(
        "--save-plots",
        action="store_true",
        help="Save breathing debug plots as PNG files.",
    )
    parser.add_argument(
        "--save-group-overlays",
        action="store_true",
        help="Save annotated overlays for grouped static image analysis.",
    )
    parser.add_argument(
        "--rest-overlay-mode",
        choices=("readable", "full", "both"),
        default="both",
        help="Overlay preset for rest_phase1 debug images. Defaults to saving both readable and full variants.",
    )
    parser.add_argument(
        "--rest-debug-layers",
        nargs="*",
        default=None,
        help="Optional explicit rest_phase1 overlay layers (for example: head_neck torso_pelvis support_axis).",
    )
    parser.add_argument(
        "--scapula-overlay-mode",
        choices=("readable", "full", "both"),
        default="both",
        help="Overlay preset for scapula debug images. Defaults to saving both readable and full variants.",
    )
    parser.add_argument(
        "--scapula-debug-layers",
        nargs="*",
        default=None,
        help="Optional explicit scapula overlay layers (for example: spine_reference scapula_distance upward_rotation).",
    )
    parser.add_argument(
        "--save-group-csv",
        action="store_true",
        help="Save grouped static-image metrics as CSV summaries.",
    )
    parser.add_argument(
        "--save-group-plots",
        action="store_true",
        help="Save grouped static-image comparison plots.",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("debug/run_rest_analysis"),
        help="Directory for saved debug artifacts.",
    )
    return parser


def infer_view(path: Path) -> str:
    """Infer a view from the filename when the user does not provide one."""
    name = path.stem.lower()
    if any(token in name for token in ("front", "frontal", "anterior")):
        return "front"
    if any(token in name for token in ("back", "posterior", "rear", "dorsal")):
        return "back"
    if any(token in name for token in ("side", "lateral", "perfil")):
        return "side"
    return "front"


def _mime_type_for_path(path: Path) -> str:
    return "video/mp4" if path.suffix.lower() in _VIDEO_SUFFIXES else "image/jpeg"


def run_grouped_analysis(client: TestClient, args: argparse.Namespace) -> tuple[int, Any]:
    """Send a grouped multipart request to the static image endpoint."""
    files: list[tuple[str, tuple[str, bytes, str]]] = []
    for field_name in _GROUP_FIELD_FLAGS:
        path = getattr(args, field_name)
        if path is None:
            continue
        with path.open("rb") as media_file:
            payload = media_file.read()
        files.append((field_name, (path.name, payload, "image/jpeg")))

    response = client.post(
        "/api/v1/analyze/image/rest",
        files=files,
        data={"include_placeholders": str(args.include_placeholders).lower()},
    )
    try:
        body: Any = response.json()
    except Exception:
        body = response.text
    return response.status_code, body


def run_rest_baseline_analysis(client: TestClient, args: argparse.Namespace) -> tuple[int, Any]:
    """Send a grouped multipart request to the new baseline endpoint."""
    assert args.breathing_video is not None
    files: list[tuple[str, tuple[str, bytes, str]]] = []
    for field_name in _GROUP_FIELD_FLAGS:
        path = getattr(args, field_name)
        if path is None:
            continue
        with path.open("rb") as media_file:
            payload = media_file.read()
        files.append((field_name, (path.name, payload, "image/jpeg")))

    with args.breathing_video.open("rb") as media_file:
        breathing_payload = media_file.read()
    files.append(
        (
            "breathing_video",
            (args.breathing_video.name, breathing_payload, _mime_type_for_path(args.breathing_video)),
        )
    )

    response = client.post(
        "/api/v1/analyze/rest/baseline",
        files=files,
        data={
            "include_placeholders": str(args.include_placeholders).lower(),
            "aggregation": args.aggregation,
            "frame_step": str(args.frame_step),
            "max_frames": str(args.max_frames),
            "reject_outliers": str(args.reject_outliers).lower(),
        },
    )
    try:
        body: Any = response.json()
    except Exception:
        body = response.text
    return response.status_code, body


def run_isa_video_analysis(client: TestClient, args: argparse.Namespace) -> tuple[int, Any]:
    """Send the ISA image plus breathing video to the dedicated thoracic endpoint."""
    assert args.isa_front_torso is not None
    assert args.breathing_video is not None

    with args.isa_front_torso.open("rb") as media_file:
        isa_payload = media_file.read()
    with args.breathing_video.open("rb") as media_file:
        breathing_payload = media_file.read()

    response = client.post(
        "/api/v1/analyze/video/isa",
        files=[
            ("isa_front_torso", (args.isa_front_torso.name, isa_payload, _mime_type_for_path(args.isa_front_torso))),
            (
                "breathing_video",
                (args.breathing_video.name, breathing_payload, _mime_type_for_path(args.breathing_video)),
            ),
        ],
        data={
            "include_placeholders": str(args.include_placeholders).lower(),
            "aggregation": args.aggregation,
            "frame_step": str(args.frame_step),
            "max_frames": str(args.max_frames),
            "reject_outliers": str(args.reject_outliers).lower(),
        },
    )
    try:
        body: Any = response.json()
    except Exception:
        body = response.text
    return response.status_code, body


def run_rest_video_analysis(client: TestClient, args: argparse.Namespace) -> tuple[int, Any]:
    """Send a single rotating rest video to the multiview video endpoint."""
    assert args.rest_video is not None
    with args.rest_video.open("rb") as media_file:
        payload = media_file.read()
    response = client.post(
        "/api/v1/analyze/video/rest",
        files={"video": (args.rest_video.name, payload, _mime_type_for_path(args.rest_video))},
        data={
            "include_placeholders": str(args.include_placeholders).lower(),
            "aggregation": args.aggregation,
            "frame_step": str(args.frame_step),
            "max_frames": str(args.max_frames),
            "reject_outliers": str(args.reject_outliers).lower(),
        },
    )
    try:
        body: Any = response.json()
    except Exception:
        body = response.text
    return response.status_code, body

def run_movement_analysis(client: TestClient, args: argparse.Namespace) -> tuple[int, Any]:
    """Run movement analysis directly from local video paths for debug workflows."""
    _ = client
    assert args.movement_back_video is not None
    assert args.movement_type is not None

    prior_analysis = None
    if args.prior_analysis_json is not None:
        prior_analysis = json.loads(args.prior_analysis_json.read_text(encoding="utf-8"))

    pipeline = get_movement_pipeline()
    body = pipeline.analyze_video_paths(
        args.movement_back_video,
        movement_type=args.movement_type,
        front_video_path=args.movement_front_video,
        prior_analysis=prior_analysis,
        include_placeholders=args.include_placeholders,
        aggregation=args.aggregation,
        frame_step=args.frame_step,
        max_frames=args.max_frames,
        reject_outliers=args.reject_outliers,
    )
    return 200, body

def run_legacy_analysis(
    client: TestClient,
    input_path: Path,
    *,
    view: str,
    include_placeholders: bool,
    video_analysis_type: str,
    aggregation: str,
    frame_step: int,
    max_frames: int,
    reject_outliers: bool,
) -> tuple[int, Any]:
    """Run the legacy single-file image/video request flow."""
    with input_path.open("rb") as media_file:
        payload = media_file.read()

    if input_path.suffix.lower() in _VIDEO_SUFFIXES:
        response = client.post(
            "/api/v1/analyze/video",
            files={"video": (input_path.name, payload, "video/mp4")},
            data={
                "video_analysis_type": video_analysis_type,
                "view": view,
                "include_placeholders": str(include_placeholders).lower(),
                "aggregation": aggregation,
                "frame_step": str(frame_step),
                "max_frames": str(max_frames),
                "reject_outliers": str(reject_outliers).lower(),
            },
        )
    else:
        response = client.post(
            "/api/v1/analyze/rest",
            files={"image": (input_path.name, payload, _mime_type_for_path(input_path))},
            data={
                "view": view,
                "include_placeholders": str(include_placeholders).lower(),
            },
        )

    try:
        body = response.json()
    except Exception:
        body = response.text
    return response.status_code, body


def print_summary(status_code: int, body: Any) -> None:
    """Print a compact summary for the response."""
    print(f"status={status_code}")
    if not isinstance(body, dict):
        print(body)
        return

    if "error" in body:
        print(body["error"])
        return

    if "metrics_by_group" in body:
        print(f"requested_groups={body.get('requested_groups', [])}")
        for group_name, group_payload in body["metrics_by_group"].items():
            print(f"group={group_name} status={group_payload.get('status')}")
            if "metrics_by_view" in group_payload:
                for view_name, view_payload in group_payload["metrics_by_view"].items():
                    print(f"  view={view_name} metrics={len(view_payload.get('metrics', {}))}")
            else:
                print(f"  metrics={_count_metric_leaves(group_payload.get('metrics', {}))}")
        print(f"integrated_findings={len(body.get('integrated_findings', {}).get('items', []))}")
        print(f"preliminary_deficiencies={len(body.get('preliminary_deficiencies', {}).get('items', []))}")
        print(f"triggered_tests_next={len(body.get('triggered_tests_next', {}).get('items', []))}")
        return

    if "groups" in body:
        print(f"requested_groups={body.get('requested_groups', [])}")
        for group_name, group_payload in body["groups"].items():
            if not isinstance(group_payload, dict):
                continue
            print(f"group={group_name} status={group_payload.get('status')}")
            if "metrics_by_view" in group_payload:
                for view_name, view_payload in group_payload["metrics_by_view"].items():
                    print(f"  view={view_name} metrics={len(view_payload.get('metrics', {}))}")
            else:
                print(f"  metrics={_count_metric_leaves(group_payload.get('metrics', {}))}")
        return

    print(f"analysis_type={body.get('analysis_type')} capture_mode={body.get('capture_mode')}")


def _count_metric_leaves(metrics: Any) -> int:
    if not isinstance(metrics, dict):
        return 0
    if "value" in metrics and "name" in metrics:
        return 1
    return sum(_count_metric_leaves(value) for value in metrics.values())


def save_json_payload(status_code: int, body: Any, output_path: Path) -> Path:
    """Persist the raw response payload to disk."""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(
        json.dumps({"status_code": status_code, "body": body}, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    return output_path


def _grouped_input_paths(args: argparse.Namespace) -> dict[str, Path]:
    return {
        field_name: getattr(args, field_name)
        for field_name in _GROUP_FIELD_FLAGS
        if getattr(args, field_name) is not None
    }


def _save_group_overlays(args: argparse.Namespace, groups: dict[str, Any], output_dir: Path) -> list[Path]:
    saved_paths: list[Path] = []
    if not isinstance(groups, dict):
        return saved_paths

    rest_group = groups.get("rest_phase1")
    if isinstance(rest_group, dict):
        rest_mappings = {
            "front": (args.rest_phase1_front, output_dir / "rest_phase1_front_annotated.jpg"),
            "side": (args.rest_phase1_side, output_dir / "rest_phase1_side_annotated.jpg"),
            "back": (args.rest_phase1_back, output_dir / "rest_phase1_back_annotated.jpg"),
        }
        enabled_layers = set(args.rest_debug_layers) if args.rest_debug_layers else None
        overlay_modes = [args.rest_overlay_mode] if args.rest_overlay_mode != "both" else ["readable", "full"]
        for view_name, mapping in rest_mappings.items():
            image_path, output_path = mapping
            if image_path is None:
                continue
            for overlay_mode in overlay_modes:
                target_path = output_path if overlay_mode == "readable" else output_path.with_name(f"{output_path.stem}_{overlay_mode}{output_path.suffix}")
                saved_paths.append(
                    save_rest_phase1_overlay_image(
                        image_path,
                        rest_group,
                        view_name,
                        target_path,
                        overlay_mode=overlay_mode,
                        enabled_layers=enabled_layers,
                    )
                )

    face_group = groups.get("face")
    if isinstance(face_group, dict) and args.face_front_face is not None:
        saved_paths.append(save_face_overlay_image(args.face_front_face, face_group, output_dir / "face_annotated.jpg"))

    foot_group = groups.get("foot_triptych")
    if isinstance(foot_group, dict):
        foot_mappings = {
            "front": (args.foot_triptych_front, output_dir / "foot_front_annotated.jpg"),
            "back": (args.foot_triptych_back, output_dir / "foot_back_annotated.jpg"),
            "left_arch": (args.foot_triptych_left_arch, output_dir / "foot_left_arch_annotated.jpg"),
            "right_arch": (args.foot_triptych_right_arch, output_dir / "foot_right_arch_annotated.jpg"),
        }
        for view_name, mapping in foot_mappings.items():
            image_path, output_path = mapping
            if image_path is not None:
                saved_paths.append(save_foot_triptych_overlay_image(image_path, foot_group, view_name, output_path))

    scapula_group = groups.get("scapula")
    if isinstance(scapula_group, dict) and args.scapula_back_upper_body is not None:
        enabled_layers = set(args.scapula_debug_layers) if args.scapula_debug_layers else None
        overlay_modes = [args.scapula_overlay_mode] if args.scapula_overlay_mode != "both" else ["readable", "full"]
        base_output_path = output_dir / "scapula_annotated.jpg"
        for overlay_mode in overlay_modes:
            target_path = base_output_path if overlay_mode == "readable" else base_output_path.with_name(f"{base_output_path.stem}_{overlay_mode}{base_output_path.suffix}")
            saved_paths.append(
                save_scapula_overlay_image(
                    args.scapula_back_upper_body,
                    scapula_group,
                    target_path,
                    overlay_mode=overlay_mode,
                    enabled_layers=enabled_layers,
                )
            )

    return saved_paths


def generate_debug_artifacts(
    args: argparse.Namespace,
    *,
    status_code: int,
    body: Any,
) -> list[Path]:
    """Generate optional debug artifacts for the current flow."""
    saved_paths: list[Path] = []
    if status_code >= 400 or not isinstance(body, dict):
        return saved_paths

    should_save_any = any(
        [
            args.save_json,
            args.save_overlay_image,
            args.save_overlay_video,
            args.save_csv,
            args.save_plots,
            args.save_group_overlays,
            args.save_group_csv,
            args.save_group_plots,
        ]
    )
    if not should_save_any:
        return saved_paths

    output_dir = args.output_dir
    output_dir.mkdir(parents=True, exist_ok=True)

    if args.save_json:
        saved_paths.append(save_json_payload(status_code, body, output_dir / "response.json"))

    groups = body.get("groups") if isinstance(body.get("groups"), dict) else None
    if groups is not None:
        if args.save_group_overlays:
            saved_paths.extend(_save_group_overlays(args, groups, output_dir))
        if args.save_group_csv:
            saved_paths.extend(save_group_metrics_csvs(groups, output_dir))
        if args.save_group_plots:
            saved_paths.extend(save_static_debug_plots(groups, output_dir))

    metrics_by_group = body.get("metrics_by_group", {})
    isa_group = metrics_by_group.get("isa") if isinstance(metrics_by_group, dict) else None
    breathing_group = metrics_by_group.get("breathing") if isinstance(metrics_by_group, dict) else None

    if args.save_overlay_image and args.isa_front_torso is not None and isinstance(isa_group, dict):
        saved_paths.append(
            save_static_overlay_image(
                args.isa_front_torso,
                isa_group,
                output_dir / "annotated_static.jpg",
            )
        )

    movement_debug = body.get("quality", {}).get("debug", {}) if isinstance(body.get("quality"), dict) else {}
    if args.save_csv and body.get("analysis_type") == "movement" and movement_debug:
        dataframe = save_movement_time_series_csv(movement_debug, output_dir / "movement_frame_metrics.csv")
        saved_paths.append(output_dir / "movement_frame_metrics.csv")

    if args.save_plots and body.get("analysis_type") == "movement" and movement_debug:
        if "dataframe" not in locals() or dataframe is None:
            dataframe = save_movement_time_series_csv(movement_debug, output_dir / "movement_frame_metrics.csv")
            if not args.save_csv:
                (output_dir / "movement_frame_metrics.csv").unlink(missing_ok=True)
        saved_paths.extend(save_movement_debug_plots(dataframe, output_dir))
    time_series = breathing_group.get("time_series", []) if isinstance(breathing_group, dict) else []
    dataframe = None
    if args.save_csv and time_series:
        dataframe = save_time_series_csv(time_series, output_dir / "frame_metrics.csv")
        saved_paths.append(output_dir / "frame_metrics.csv")

    if args.save_plots and time_series:
        if dataframe is None:
            dataframe = save_time_series_csv(time_series, output_dir / "frame_metrics.csv")
            if not args.save_csv:
                (output_dir / "frame_metrics.csv").unlink(missing_ok=True)
        saved_paths.extend(save_debug_plots(dataframe, output_dir))

    if args.save_overlay_video and args.breathing_video is not None and isinstance(breathing_group, dict):
        saved_paths.append(
            save_breathing_overlay_video(
                args.breathing_video,
                breathing_group,
                output_dir / "annotated_breathing.mp4",
                max_frames=args.max_frames,
                frame_step=args.frame_step,
            )
        )
        saved_paths.append(
            save_breathing_overlay_preview(
                args.breathing_video,
                breathing_group,
                output_dir / "annotated_breathing_preview.png",
                max_frames=args.max_frames,
                frame_step=args.frame_step,
            )
        )
        frame_paths = save_breathing_overlay_frames(
            args.breathing_video,
            breathing_group,
            output_dir / "annotated_breathing_frames",
            max_frames=args.max_frames,
            frame_step=args.frame_step,
        )
        saved_paths.extend(frame_paths)

    return saved_paths


def _handle_response(
    args: argparse.Namespace,
    *,
    status_code: int,
    body: Any,
    input_path: Path | None = None,
    view: str | None = None,
) -> int:
    saved_paths = generate_debug_artifacts(args, status_code=status_code, body=body)
    if args.json:
        payload: dict[str, Any] = {"status_code": status_code, "body": body}
        if input_path is not None:
            payload["input"] = str(input_path)
        if view is not None:
            payload["view"] = view
        print(json.dumps(payload, indent=2, ensure_ascii=False))
    else:
        if input_path is not None:
            print(f"input={input_path} view={view}")
        print_summary(status_code, body)
        if saved_paths:
            print("saved_artifacts=")
            for path in saved_paths:
                print(f"  {path}")
    return 0 if status_code < 400 else 1


def main() -> int:
    """CLI entrypoint."""
    parser = build_parser()
    args = parser.parse_args()
    client = TestClient(app)

    grouped_paths = [getattr(args, field_name) for field_name in _GROUP_FIELD_FLAGS]
    using_grouped_mode = any(path is not None for path in grouped_paths)

    if args.breathing_video is not None:
        provided_group_fields = {
            field_name
            for field_name in _GROUP_FIELD_FLAGS
            if getattr(args, field_name) is not None
        }
        if provided_group_fields == {"isa_front_torso"}:
            all_paths = [args.isa_front_torso, args.breathing_video]
            missing = [str(path) for path in all_paths if path is None or not path.is_file()]
            if missing:
                for path in missing:
                    print(f"Missing file: {path}")
                return 1
            status_code, body = run_isa_video_analysis(client, args)
            return _handle_response(args, status_code=status_code, body=body)

        required_group_paths = [path for path in grouped_paths if path is None]
        if required_group_paths:
            parser.error(
                "With --breathing-video you must provide either all grouped image flags for baseline "
                "or only --isa-front-torso for /api/v1/analyze/video/isa."
            )
        all_paths = [path for path in grouped_paths if path is not None] + [args.breathing_video]
        missing = [str(path) for path in all_paths if not path.is_file()]
        if missing:
            for path in missing:
                print(f"Missing file: {path}")
            return 1
        status_code, body = run_rest_baseline_analysis(client, args)
        return _handle_response(args, status_code=status_code, body=body)

    if args.rest_video is not None:
        if not args.rest_video.is_file():
            print(f"Missing file: {args.rest_video}")
            return 1
        status_code, body = run_rest_video_analysis(client, args)
        return _handle_response(args, status_code=status_code, body=body)

    if args.movement_back_video is not None or args.movement_type is not None:
        if args.movement_back_video is None or args.movement_type is None:
            parser.error("Movement analysis requires both --movement-type and --movement-back-video.")
        movement_paths = [args.movement_back_video]
        if args.movement_front_video is not None:
            movement_paths.append(args.movement_front_video)
        if args.prior_analysis_json is not None:
            movement_paths.append(args.prior_analysis_json)
        missing = [str(path) for path in movement_paths if not path.is_file()]
        if missing:
            for path in missing:
                print(f"Missing file: {path}")
            return 1
        status_code, body = run_movement_analysis(client, args)
        return _handle_response(args, status_code=status_code, body=body)
    if using_grouped_mode:
        missing = [str(path) for path in grouped_paths if path is not None and not path.is_file()]
        if missing:
            for path in missing:
                print(f"Missing file: {path}")
            return 1
        status_code, body = run_grouped_analysis(client, args)
        return _handle_response(args, status_code=status_code, body=body)

    if not args.inputs:
        parser.error("Provide legacy positional inputs, grouped image flags, --rest-video, or movement flags.")

    missing_files = [path for path in args.inputs if not path.is_file()]
    if missing_files:
        for path in missing_files:
            print(f"Missing file: {path}")
        return 1

    exit_code = 0
    for input_path in args.inputs:
        view = args.view or infer_view(input_path)
        status_code, body = run_legacy_analysis(
            client,
            input_path,
            view=view,
            include_placeholders=args.include_placeholders,
            video_analysis_type=args.video_analysis_type,
            aggregation=args.aggregation,
            frame_step=args.frame_step,
            max_frames=args.max_frames,
            reject_outliers=args.reject_outliers,
        )
        result_code = _handle_response(args, status_code=status_code, body=body, input_path=input_path, view=view)
        if result_code != 0:
            exit_code = 1
    return exit_code



_original_build_parser = build_parser


def build_parser() -> argparse.ArgumentParser:
    """Create the CLI parser with movement debug extensions."""
    parser = _original_build_parser()
    if not any(action.dest == "movement_overlay_mode" for action in parser._actions):
        parser.add_argument(
            "--movement-overlay-mode",
            choices=("readable", "full", "both"),
            default="both",
            help="Overlay preset for posterior movement debug videos. Defaults to saving both readable and full variants.",
        )
    return parser


def print_summary(status_code: int, body: Any) -> None:
    """Print a compact summary for the response."""
    print(f"status={status_code}")
    if not isinstance(body, dict):
        print(body)
        return
    if "error" in body:
        print(body["error"])
        return
    if body.get("analysis_type") == "movement":
        print(f"analysis_type={body.get('analysis_type')} movement_type={body.get('movement_type')}")
        views = body.get("views", {}) if isinstance(body.get("views"), dict) else {}
        back_view = views.get("back", {}) if isinstance(views.get("back"), dict) else {}
        pose = back_view.get("pose", {}) if isinstance(back_view.get("pose"), dict) else {}
        print(f"back_frames={pose.get('successful_frame_count')} failed_frames={pose.get('failed_frame_count')}")
        phases = body.get("movement_phases", {}) if isinstance(body.get("movement_phases"), dict) else {}
        print(f"movement_start={phases.get('movement_start_frame')} peak={phases.get('peak_frame')} descent={phases.get('descent_start_frame')}")
        print(f"metrics={_count_metric_leaves(body.get('metrics', {}))}")
        print(f"findings={len(body.get('findings', {}).get('items', []))} deficiencies={len(body.get('deficiencies', {}).get('items', []))}")
        return
    if "metrics_by_group" in body:
        print(f"requested_groups={body.get('requested_groups', [])}")
        for group_name, group_payload in body["metrics_by_group"].items():
            print(f"group={group_name} status={group_payload.get('status')}")
            if "metrics_by_view" in group_payload:
                for view_name, view_payload in group_payload["metrics_by_view"].items():
                    print(f"  view={view_name} metrics={len(view_payload.get('metrics', {}))}")
            else:
                print(f"  metrics={_count_metric_leaves(group_payload.get('metrics', {}))}")
        print(f"integrated_findings={len(body.get('integrated_findings', {}).get('items', []))}")
        print(f"preliminary_deficiencies={len(body.get('preliminary_deficiencies', {}).get('items', []))}")
        print(f"triggered_tests_next={len(body.get('triggered_tests_next', {}).get('items', []))}")
        return
    if "groups" in body:
        print(f"requested_groups={body.get('requested_groups', [])}")
        for group_name, group_payload in body["groups"].items():
            if not isinstance(group_payload, dict):
                continue
            print(f"group={group_name} status={group_payload.get('status')}")
            if "metrics_by_view" in group_payload:
                for view_name, view_payload in group_payload["metrics_by_view"].items():
                    print(f"  view={view_name} metrics={len(view_payload.get('metrics', {}))}")
            else:
                print(f"  metrics={_count_metric_leaves(group_payload.get('metrics', {}))}")
        return
    print(f"analysis_type={body.get('analysis_type')} capture_mode={body.get('capture_mode')}")


def generate_debug_artifacts(
    args: argparse.Namespace,
    *,
    status_code: int,
    body: Any,
) -> list[Path]:
    """Generate optional debug artifacts for the current flow."""
    from debug_utils.plotting import save_movement_phases_csv
    from debug_utils.visualization import save_movement_overlay_video

    saved_paths: list[Path] = []
    if status_code >= 400 or not isinstance(body, dict):
        return saved_paths

    should_save_any = any(
        [
            args.save_json,
            args.save_overlay_image,
            args.save_overlay_video,
            args.save_csv,
            args.save_plots,
            args.save_group_overlays,
            args.save_group_csv,
            args.save_group_plots,
        ]
    )
    if not should_save_any:
        return saved_paths

    output_dir = args.output_dir
    output_dir.mkdir(parents=True, exist_ok=True)

    if args.save_json:
        saved_paths.append(save_json_payload(status_code, body, output_dir / "response.json"))

    groups = body.get("groups") if isinstance(body.get("groups"), dict) else None
    if groups is not None:
        if args.save_group_overlays:
            saved_paths.extend(_save_group_overlays(args, groups, output_dir))
        if args.save_group_csv:
            saved_paths.extend(save_group_metrics_csvs(groups, output_dir))
        if args.save_group_plots:
            saved_paths.extend(save_static_debug_plots(groups, output_dir))

    metrics_by_group = body.get("metrics_by_group", {})
    isa_group = metrics_by_group.get("isa") if isinstance(metrics_by_group, dict) else None
    breathing_group = metrics_by_group.get("breathing") if isinstance(metrics_by_group, dict) else None

    if args.save_overlay_image and args.isa_front_torso is not None and isinstance(isa_group, dict):
        saved_paths.append(save_static_overlay_image(args.isa_front_torso, isa_group, output_dir / "annotated_static.jpg"))

    if body.get("analysis_type") == "movement":
        movement_debug = body.get("quality", {}).get("debug", {}) if isinstance(body.get("quality"), dict) else {}
        movement_dataframe = None
        if args.save_csv and movement_debug:
            movement_dataframe = save_movement_time_series_csv(movement_debug, output_dir / "frame_metrics.csv")
            saved_paths.append(output_dir / "frame_metrics.csv")
            save_movement_phases_csv(movement_debug, output_dir / "movement_phases.csv")
            saved_paths.append(output_dir / "movement_phases.csv")
        if args.save_plots and movement_debug:
            if movement_dataframe is None:
                movement_dataframe = save_movement_time_series_csv(movement_debug, output_dir / "frame_metrics.csv")
                if not args.save_csv:
                    (output_dir / "frame_metrics.csv").unlink(missing_ok=True)
            saved_paths.extend(save_movement_debug_plots(movement_dataframe, output_dir))
        if args.save_overlay_video and args.movement_back_video is not None:
            overlay_modes = [args.movement_overlay_mode] if args.movement_overlay_mode != "both" else ["readable", "full"]
            for overlay_mode in overlay_modes:
                target_path = output_dir / ("annotated_back.mp4" if overlay_mode == "readable" else "annotated_back_full.mp4")
                saved_paths.append(
                    save_movement_overlay_video(
                        args.movement_back_video,
                        body,
                        target_path,
                        max_frames=args.max_frames,
                        frame_step=args.frame_step,
                        overlay_mode=overlay_mode,
                    )
                )
        return saved_paths

    time_series = breathing_group.get("time_series", []) if isinstance(breathing_group, dict) else []
    dataframe = None
    if args.save_csv and time_series:
        dataframe = save_time_series_csv(time_series, output_dir / "frame_metrics.csv")
        saved_paths.append(output_dir / "frame_metrics.csv")
    if args.save_plots and time_series:
        if dataframe is None:
            dataframe = save_time_series_csv(time_series, output_dir / "frame_metrics.csv")
            if not args.save_csv:
                (output_dir / "frame_metrics.csv").unlink(missing_ok=True)
        saved_paths.extend(save_debug_plots(dataframe, output_dir))
    if args.save_overlay_video and args.breathing_video is not None and isinstance(breathing_group, dict):
        saved_paths.append(save_breathing_overlay_video(args.breathing_video, breathing_group, output_dir / "annotated_breathing.mp4", max_frames=args.max_frames, frame_step=args.frame_step))
        saved_paths.append(save_breathing_overlay_preview(args.breathing_video, breathing_group, output_dir / "annotated_breathing_preview.png", max_frames=args.max_frames, frame_step=args.frame_step))
        saved_paths.extend(save_breathing_overlay_frames(args.breathing_video, breathing_group, output_dir / "annotated_breathing_frames", max_frames=args.max_frames, frame_step=args.frame_step))
    return saved_paths


if __name__ == "__main__":
    raise SystemExit(main())
