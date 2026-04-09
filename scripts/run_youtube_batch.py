"""Run YouTube Shorts discovery, Supabase deduplication, and selected analysis backend."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.storage.youtube_scrape_store import YoutubeScrapeStore
from src.pipelines.youtube_batch_analysis import run_gemini_pipeline, run_local_pipeline
from video.youtube_shorts import scrape_channel_shorts

DEFAULT_CHANNEL_URL = "https://www.youtube.com/@conorharris/shorts"
DEFAULT_ORDER = "newest"
DEFAULT_MODEL = "gemini-2.5-flash"
DEFAULT_BROWSER_CHANNEL = "msedge"
DEFAULT_OUTPUT_BASE = "data/knowledge/video_knowledge_drafts"

ANALYSIS_BACKENDS = ("local", "gemini", "skill_seekers", "hf_video_direct")


def parse_range(value: str) -> tuple[int, int]:
    """Parse a range like 21-30 into integer bounds."""
    if "-" not in value:
        raise argparse.ArgumentTypeError("Range must use the format START-END, for example 21-30.")
    start_text, end_text = value.split("-", 1)
    try:
        start = int(start_text)
        end = int(end_text)
    except ValueError as exc:
        raise argparse.ArgumentTypeError("Range must contain integer values.") from exc
    if start < 1 or end < start:
        raise argparse.ArgumentTypeError("Range must satisfy START >= 1 and END >= START.")
    return start, end


def build_output_dir(*, channel_url: str, order: str, start_rank: int, end_rank: int, output_base: str, backend: str) -> str:
    """Create a consistent output folder name for each batch."""
    channel_slug = channel_url.rstrip("/").split("/")[-2 if channel_url.rstrip("/").endswith("shorts") else -1]
    safe_channel_slug = channel_slug.lstrip("@").replace("-", "_")
    return f"{output_base}/{safe_channel_slug}_{order}_{start_rank}_{end_rank}_{backend}"


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Run YouTube Shorts discovery + Supabase deduplication + one analysis backend."
    )
    parser.add_argument("--range", required=True, type=parse_range, help="Rank range to analyze, for example 21-30.")
    parser.add_argument("--channel-url", default=DEFAULT_CHANNEL_URL)
    parser.add_argument("--order", choices=("newest", "popular", "oldest"), default=DEFAULT_ORDER)
    parser.add_argument("--browser-channel", default=DEFAULT_BROWSER_CHANNEL)
    parser.add_argument("--model", default=DEFAULT_MODEL)
    parser.add_argument("--output-base", default=DEFAULT_OUTPUT_BASE)
    parser.add_argument("--analysis-backend", choices=ANALYSIS_BACKENDS, default="local")
    parser.add_argument("--include-analyzed", action="store_true")
    parser.add_argument("--headful", action="store_true")
    return parser


def main() -> None:
    args = build_parser().parse_args()
    start_rank, end_rank = args.range
    output_dir = Path(
        build_output_dir(
            channel_url=args.channel_url,
            order=args.order,
            start_rank=start_rank,
            end_rank=end_rank,
            output_base=args.output_base,
            backend=args.analysis_backend,
        )
    )
    output_dir.mkdir(parents=True, exist_ok=True)

    videos = scrape_channel_shorts(
        channel_url=args.channel_url,
        limit=end_rank,
        order=args.order,
        browser_channel=args.browser_channel,
        headless=not args.headful,
    )
    scrape_store = YoutubeScrapeStore()
    scrape_info = scrape_store.record_scrape_run(
        channel_url=args.channel_url,
        order=args.order,
        limit=end_rank,
        browser_channel=args.browser_channel,
        videos=videos,
    )

    selected = videos[start_rank - 1 : end_rank]
    pending_selection = scrape_store.select_pending(selected)
    pending = selected if args.include_analyzed else pending_selection.pending_videos
    skipped = [] if args.include_analyzed else [video for video in selected if video.video_id in pending_selection.analyzed_video_ids]

    if args.analysis_backend == "local":
        results = run_local_pipeline(pending, output_dir)
    elif args.analysis_backend == "gemini":
        results = run_gemini_pipeline(pending, output_dir, model=args.model)
    else:
        raise SystemExit(
            f"Analysis backend '{args.analysis_backend}' is reserved for future implementation. "
            "Use 'local' or 'gemini' for now."
        )

    summary = {
        "channel_url": args.channel_url,
        "order": args.order,
        "start_rank": start_rank,
        "end_rank": end_rank,
        "analysis_backend": args.analysis_backend,
        "selected_count": len(selected),
        "pending_count": len(pending),
        "skipped_count": len(skipped),
        "scrape_run_id": scrape_info["run_id"],
        "analyzed_video_ids": [item["video_id"] for item in results],
        "skipped_video_ids": [video.video_id for video in skipped],
        "results": results,
    }
    summary_path = output_dir / "run_summary.json"
    summary_path.write_text(json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8")
    print(json.dumps(summary, indent=2, ensure_ascii=False))
    print(f"Summary saved to: {summary_path}")

if __name__ == "__main__":
    main()
