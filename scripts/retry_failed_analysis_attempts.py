"""Retry failed Gemini upgrade attempts recorded in Supabase."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.storage.supabase_store import SupabaseRagStore


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Retry failed Gemini upgrade attempts.")
    parser.add_argument("--limit", type=int, default=5)
    parser.add_argument("--order", choices=("asc", "desc"), default="desc")
    parser.add_argument(
        "--requested-backend",
        default="gemini_upgrade",
        help="Requested backend to filter. Default: gemini_upgrade.",
    )
    parser.add_argument("--model", default="gemini-2.5-flash")
    parser.add_argument(
        "--output-json",
        default="data/knowledge/rag_runs/retry_failed_analysis_attempts.json",
        help="Path to save the retry summary.",
    )
    return parser


def main() -> None:
    args = build_parser().parse_args()
    store = SupabaseRagStore()
    reconciled_count = store.reconcile_resolved_analysis_errors(requested_backend=args.requested_backend)
    attempts = store.list_failed_analysis_attempts(
        requested_backend=args.requested_backend,
        limit=args.limit,
        ascending=args.order == "asc",
    )
    urls = list(dict.fromkeys(str(item["source_url"]) for item in attempts))
    command = [
        sys.executable,
        str(ROOT / "scripts" / "upgrade_drafts_to_gemini.py"),
        "--model",
        args.model,
        "--output-json",
        str(Path(args.output_json).resolve().with_name("retry_failed_upgrade_inner.json")),
    ]
    for url in urls:
        command.extend(["--url", url])

    completed = subprocess.run(
        command,
        check=False,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    payload = {
        "requested_backend": args.requested_backend,
        "reconciled_count": reconciled_count,
        "retry_count": len(urls),
        "urls": urls,
        "returncode": completed.returncode,
        "stdout_tail": completed.stdout[-4000:] if completed.stdout else "",
        "stderr_tail": completed.stderr[-4000:] if completed.stderr else "",
    }
    output_path = Path(args.output_json)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
    print(json.dumps(payload, indent=2, ensure_ascii=False))
    print(f"Summary saved to: {output_path}")
    if completed.returncode != 0:
        raise SystemExit(completed.returncode)


if __name__ == "__main__":
    main()
