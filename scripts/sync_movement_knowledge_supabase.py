"""Push Supabase migrations and import movement knowledge JSON incrementally."""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Run a complete movement knowledge sync: db push + incremental import."
    )
    parser.add_argument(
        "--dataset-name",
        default="movement_knowledge_base",
        help="Logical dataset label stored in the database.",
    )
    parser.add_argument(
        "--root",
        default="data/knowledge/video_knowledge_drafts",
        help="Root folder that contains Gemini analysis JSON files.",
    )
    parser.add_argument(
        "--skip-db-push",
        action="store_true",
        help="Skip migration push and run only the incremental import.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Parse files only; do not write to the database.",
    )
    parser.add_argument(
        "--limit",
        type=int,
        help="Optional maximum number of files to process.",
    )
    return parser


def main() -> None:
    args = build_parser().parse_args()

    if not args.skip_db_push:
        _run(
            [
                "supabase",
                "db",
                "push",
            ]
        )

    command = [
        sys.executable,
        str(ROOT / "scripts" / "import_movement_knowledge_to_supabase.py"),
        "--root",
        args.root,
        "--dataset-name",
        args.dataset_name,
    ]
    if args.dry_run:
        command.append("--dry-run")
    if args.limit is not None:
        command.extend(["--limit", str(args.limit)])

    _run(command)


def _run(command: list[str]) -> None:
    print("Running:")
    print(" ".join(command))
    completed = subprocess.run(command, check=False)
    if completed.returncode != 0:
        raise SystemExit(completed.returncode)


if __name__ == "__main__":
    main()
