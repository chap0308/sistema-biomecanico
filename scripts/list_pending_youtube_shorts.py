"""List YouTube Shorts that have not been analyzed yet."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.storage.youtube_scrape_store import YoutubeScrapeStore
from video.youtube_shorts import scrape_channel_shorts


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="List pending YouTube Shorts not yet analyzed.")
    parser.add_argument("--channel-url", required=True)
    parser.add_argument("--order", choices=("newest", "popular", "oldest"), default="newest")
    parser.add_argument("--limit", type=int, required=True, help="How many top results to inspect.")
    parser.add_argument("--start-rank", type=int, default=1, help="1-based inclusive start rank inside the scraped range.")
    parser.add_argument("--end-rank", type=int, help="1-based inclusive end rank inside the scraped range. Defaults to --limit.")
    parser.add_argument("--browser-channel", default="msedge")
    parser.add_argument(
        "--output-file",
        default="data/knowledge/youtube_channels/pending_selection.json",
        help="Where to save the pending selection snapshot.",
    )
    parser.add_argument("--headful", action="store_true")
    return parser


def main() -> None:
    args = build_parser().parse_args()
    end_rank = args.end_rank or args.limit
    if args.start_rank < 1 or end_rank < args.start_rank or args.limit < end_rank:
        raise SystemExit("Invalid rank range.")

    videos = scrape_channel_shorts(
        channel_url=args.channel_url,
        limit=args.limit,
        order=args.order,
        browser_channel=args.browser_channel,
        headless=not args.headful,
    )
    selected = videos[args.start_rank - 1 : end_rank]
    selection = YoutubeScrapeStore().select_pending(selected)
    pending = selection.pending_videos
    already_analyzed = [video for video in selected if video.video_id in selection.analyzed_video_ids]

    output_path = Path(args.output_file)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "channel_url": args.channel_url,
        "order": args.order,
        "limit": args.limit,
        "start_rank": args.start_rank,
        "end_rank": end_rank,
        "selected_count": len(selected),
        "pending_count": len(pending),
        "already_analyzed_count": len(already_analyzed),
        "pending_videos": [video.to_dict() for video in pending],
        "already_analyzed_videos": [video.to_dict() for video in already_analyzed],
    }
    output_path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")

    print(f"Selected videos: {len(selected)}")
    print(f"Pending videos: {len(pending)}")
    print(f"Already analyzed: {len(already_analyzed)}")
    print(f"Snapshot saved to: {output_path}")


if __name__ == "__main__":
    main()
