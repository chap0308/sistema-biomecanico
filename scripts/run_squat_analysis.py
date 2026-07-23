"""Register and run local bilateral-squat analysis cases."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from src.squat.models import TARGET_FINDINGS, SquatCaseRecord
from src.squat.pipeline import register_squat_case
from src.squat.pose_video import extract_squat_pose_video
from src.squat.registry import initialize_case_registry
from src.squat.segmentation import segment_squat_pose_artifacts

DEFAULT_REGISTRY = Path("data/sentadilla_bilateral/metadata/casos.csv")
DEFAULT_OUTPUT_DIR = Path("data/sentadilla_bilateral/outputs")


def build_parser() -> argparse.ArgumentParser:
    """Create the command-line parser for the squat pipeline."""
    parser = argparse.ArgumentParser(
        description="Manage the local bilateral-squat thesis pipeline.",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    init_parser = subparsers.add_parser("init", help="Initialize the case registry.")
    init_parser.add_argument("--registry", type=Path, default=DEFAULT_REGISTRY)

    register_parser = subparsers.add_parser(
        "register",
        help="Inspect and register one local frontal squat video.",
    )
    register_parser.add_argument("--case-id", required=True)
    register_parser.add_argument("--video", type=Path, required=True)
    register_parser.add_argument("--participant-code")
    register_parser.add_argument(
        "--profile",
        choices=("positivo_controlado", "negativo", "no_etiquetado"),
        default="no_etiquetado",
    )
    register_parser.add_argument(
        "--intended-finding",
        action="append",
        choices=TARGET_FINDINGS,
        default=[],
        help="Expected controlled finding. Repeat the flag for multiple labels.",
    )
    register_parser.add_argument(
        "--protocol-review-status",
        choices=("pendiente", "aceptado", "rechazado"),
        default="pendiente",
    )
    register_parser.add_argument("--exclusion-reason")
    register_parser.add_argument("--registry", type=Path, default=DEFAULT_REGISTRY)
    register_parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)

    pose_parser = subparsers.add_parser(
        "extract-pose",
        help="Extract temporal MediaPipe landmarks and debug artifacts.",
    )
    pose_parser.add_argument("--case-id", required=True)
    pose_parser.add_argument("--video", type=Path, required=True)
    pose_parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    pose_parser.add_argument("--min-visibility", type=float, default=0.5)
    pose_parser.add_argument(
        "--anonymize-face",
        action=argparse.BooleanOptionalAction,
        default=True,
    )

    segment_parser = subparsers.add_parser(
        "segment",
        help="Detect repetitions and temporal phases from pose artifacts.",
    )
    segment_parser.add_argument("--case-id", required=True)
    segment_parser.add_argument("--landmarks-csv", type=Path, required=True)
    segment_parser.add_argument("--frame-quality-csv", type=Path, required=True)
    segment_parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    return parser


def main(argv: list[str] | None = None) -> int:
    """Execute a squat pipeline command and return its process exit code."""
    args = build_parser().parse_args(argv)
    if args.command == "init":
        path = initialize_case_registry(args.registry)
        print(json.dumps({"status": "initialized", "registry": str(path)}, ensure_ascii=False))
        return 0

    if args.command == "extract-pose":
        summary = extract_squat_pose_video(
            args.video,
            case_id=args.case_id,
            output_dir=args.output_dir,
            min_visibility=args.min_visibility,
            anonymize_face=args.anonymize_face,
        )
        print(json.dumps(summary.model_dump(mode="json"), indent=2, ensure_ascii=False))
        return 0

    if args.command == "segment":
        summary = segment_squat_pose_artifacts(
            args.landmarks_csv,
            args.frame_quality_csv,
            case_id=args.case_id,
            output_dir=args.output_dir,
        )
        print(json.dumps(summary.model_dump(mode="json"), indent=2, ensure_ascii=False))
        return 0

    case = SquatCaseRecord(
        case_id=args.case_id,
        video_path=str(args.video),
        participant_code=args.participant_code,
        profile=args.profile,
        intended_findings=args.intended_finding,
        protocol_review_status=args.protocol_review_status,
        exclusion_reason=args.exclusion_reason,
    )
    result, result_path = register_squat_case(
        case,
        registry_path=args.registry,
        output_dir=args.output_dir,
    )
    print(
        json.dumps(
            {
                "analysis_id": result.analysis_id,
                "status": result.status,
                "ready_for_pose": result.ready_for_pose,
                "result_path": str(result_path),
            },
            indent=2,
            ensure_ascii=False,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
