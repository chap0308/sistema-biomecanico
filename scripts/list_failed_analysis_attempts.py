"""List failed analysis attempts recorded in Supabase."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.storage.supabase_store import SupabaseRagStore


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="List failed analysis attempts from Supabase.")
    parser.add_argument("--limit", type=int, default=10)
    parser.add_argument("--order", choices=("asc", "desc"), default="desc")
    parser.add_argument(
        "--requested-backend",
        default="gemini_upgrade",
        help="Requested backend to filter. Default: gemini_upgrade.",
    )
    parser.add_argument(
        "--output-json",
        default="data/knowledge/rag_runs/failed_analysis_attempts.json",
        help="Path to save the summary.",
    )
    return parser


def main() -> None:
    args = build_parser().parse_args()
    store = SupabaseRagStore()
    reconciled_count = store.reconcile_resolved_analysis_errors(requested_backend=args.requested_backend)
    rows = store.list_failed_analysis_attempts(
        requested_backend=args.requested_backend,
        limit=args.limit,
        ascending=args.order == "asc",
    )
    payload = {
        "requested_backend": args.requested_backend,
        "reconciled_count": reconciled_count,
        "count": len(rows),
        "results": rows,
    }
    output_path = Path(args.output_json)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(payload, indent=2, ensure_ascii=False, default=str), encoding="utf-8")
    print(json.dumps(payload, indent=2, ensure_ascii=False, default=str))
    print(f"Summary saved to: {output_path}")


if __name__ == "__main__":
    main()
