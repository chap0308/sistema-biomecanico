"""Ask the multimodal RAG system using quality-based retrieval."""

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

from src.rag.answering import answer_query
from src.retrieval.hybrid import retrieve_for_query
from src.storage.supabase_store import SupabaseRagStore


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Ask the biomechanics RAG system.")
    parser.add_argument("--query", required=True, help="Natural-language user query.")
    parser.add_argument(
        "--response-quality",
        choices=["low", "medium", "high"],
        default="medium",
        help="Retrieval depth and grounding quality.",
    )
    parser.add_argument("--output-json", help="Optional path to save the final grounded answer.")
    parser.add_argument(
        "--answer-backend",
        choices=["auto", "ollama", "openai", "hf", "grounded"],
        help="Optional answering backend override. Defaults to the configured backend.",
    )
    parser.add_argument(
        "--answer-model",
        help="Optional model override for the selected backend. Example: qwen3:4b or gpt-5-mini.",
    )
    parser.add_argument(
        "--answer-profile",
        choices=["balanced", "cheap"],
        help="Optional cost/quality profile for backend-selected models.",
    )
    return parser


def main() -> None:
    args = build_parser().parse_args()
    supabase_store = SupabaseRagStore()
    bundle = retrieve_for_query(args.query, quality=args.response_quality, supabase_store=supabase_store)
    if args.answer_model:
        import os

        backend = (args.answer_backend or "").lower()
        if backend == "ollama":
            os.environ["OLLAMA_ANSWER_MODEL"] = args.answer_model
        elif backend == "openai":
            os.environ["OPENAI_ANSWER_MODEL"] = args.answer_model
        elif backend == "hf":
            os.environ["HF_ANSWER_MODEL"] = args.answer_model
    answer = answer_query(
        args.query,
        bundle,
        backend=args.answer_backend,
        model_profile=args.answer_profile,
    )
    serialized = json.dumps(answer, indent=2, ensure_ascii=False)
    if args.output_json:
        output_path = Path(args.output_json)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(serialized, encoding="utf-8")
    print(serialized)


if __name__ == "__main__":
    main()
