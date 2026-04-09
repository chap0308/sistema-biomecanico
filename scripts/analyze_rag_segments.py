"""Build a second-layer knowledge draft from a Level 1 RAG run JSON."""

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

from src.analysis.hf_knowledge_draft import analyze_level1_result_file_with_hf
from src.analysis.knowledge_draft import analyze_level1_result_file


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Generate a knowledge draft from one Level 1 RAG result.")
    parser.add_argument("--input-json", required=True)
    parser.add_argument("--output-json")
    parser.add_argument(
        "--backend",
        choices=["heuristic", "hf", "auto"],
        default="auto",
        help="Analysis backend. 'auto' prefers Hugging Face when configured, else falls back to heuristic.",
    )
    parser.add_argument("--model", help="Optional Hugging Face model override for the hf backend.")
    parser.add_argument(
        "--no-fallback",
        action="store_true",
        help="When using the hf backend, fail instead of falling back to the heuristic analyzer.",
    )
    return parser


def main() -> None:
    args = build_parser().parse_args()
    if args.backend == "heuristic":
        draft = analyze_level1_result_file(args.input_json)
    elif args.backend == "hf":
        draft = analyze_level1_result_file_with_hf(
            args.input_json,
            model=args.model,
            fallback_to_heuristic=not args.no_fallback,
        )
    else:
        draft = analyze_level1_result_file_with_hf(
            args.input_json,
            model=args.model,
            fallback_to_heuristic=True,
        )
    serialized = json.dumps(draft, indent=2, ensure_ascii=False)
    if args.output_json:
        path = Path(args.output_json)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(serialized, encoding="utf-8")
    print(serialized)


if __name__ == "__main__":
    main()
