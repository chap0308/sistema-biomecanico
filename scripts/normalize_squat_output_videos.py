"""Convert existing squat overlay and review videos to browser-compatible H.264."""

from __future__ import annotations

import argparse
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.squat.video_encoding import normalize_h264_mp4, probe_video_codec


DEFAULT_OUTPUTS = ROOT / "data" / "sentadilla_bilateral" / "outputs"


def normalize_outputs(outputs_dir: Path, *, case_id: str | None = None) -> tuple[int, int]:
    """Normalize overlay and review MP4 files and return converted/skipped counts."""
    search_root = outputs_dir / case_id if case_id else outputs_dir
    files = sorted(
        path
        for path in search_root.rglob("*.mp4")
        if path.name in {"overlay.mp4", "review.mp4"}
    )
    converted = 0
    skipped = 0
    for path in files:
        changed = normalize_h264_mp4(path)
        codec = probe_video_codec(path)
        status = "converted" if changed else "compatible"
        print(f"{status}: {path.relative_to(outputs_dir)} -> {codec}")
        converted += int(changed)
        skipped += int(not changed)
    return converted, skipped


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--outputs-dir", type=Path, default=DEFAULT_OUTPUTS)
    parser.add_argument("--case-id")
    args = parser.parse_args()
    converted, skipped = normalize_outputs(
        args.outputs_dir.resolve(),
        case_id=args.case_id,
    )
    print(f"converted={converted} compatible={skipped}")


if __name__ == "__main__":
    main()
