"""Query the local Qdrant collection for bootstrap RAG validation."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.core.settings import get_rag_settings
from src.indexing.qdrant_store import QdrantStore


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Query indexed RAG segments from local or remote Qdrant.")
    parser.add_argument("--text", required=True, help="Semantic query text.")
    parser.add_argument("--limit", type=int, default=5)
    parser.add_argument("--output-json")
    return parser


def main() -> None:
    args = build_parser().parse_args()
    settings = get_rag_settings()

    qdrant_kwargs = {"collection_name": settings.qdrant_collection}
    if settings.qdrant_prefer_embedded:
        qdrant_kwargs["path"] = settings.qdrant_path
    else:
        qdrant_kwargs["url"] = settings.qdrant_url
        qdrant_kwargs["api_key"] = settings.qdrant_api_key

    store = QdrantStore(**qdrant_kwargs)
    results = store.query(args.text, limit=args.limit)
    payload = {
        "query": args.text,
        "limit": args.limit,
        "collection": settings.qdrant_collection,
        "result_count": len(results),
        "results": [
            {
                "point_id": item.point_id,
                "score": item.score,
                "payload": item.payload,
            }
            for item in results
        ],
    }

    serialized = json.dumps(payload, indent=2, ensure_ascii=False)
    if args.output_json:
        output_path = Path(args.output_json)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(serialized, encoding="utf-8")
    print(serialized)


if __name__ == "__main__":
    main()
