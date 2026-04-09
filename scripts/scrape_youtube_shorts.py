"""CLI wrapper for YouTube Shorts discovery with Playwright."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from video.youtube_shorts import diff_new_videos, load_seen_state, save_seen_state, scrape_channel_shorts, update_seen_state
from src.pipelines.youtube_batch_analysis import run_gemini_pipeline, run_local_pipeline
from src.storage.youtube_scrape_store import YoutubeScrapeStore


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Discover YouTube Shorts URLs from a channel page.")
    parser.add_argument("--channel-url", required=True, help="YouTube channel Shorts URL or channel URL.")
    parser.add_argument("--limit", type=int, default=30, help="Maximum number of Shorts to collect.")
    parser.add_argument(
        "--order",
        choices=("newest", "popular", "oldest"),
        default="newest",
        help="Shorts tab order to scrape.",
    )
    parser.add_argument(
        "--state-file",
        default="data/knowledge/youtube_channels/conorharris_state.json",
        help="Path to the persistent state JSON file.",
    )
    parser.add_argument(
        "--output-file",
        default="data/knowledge/youtube_channels/latest_scrape.json",
        help="Path to save the latest scrape snapshot.",
    )
    parser.add_argument(
        "--browser-channel",
        default="msedge",
        help="Playwright browser channel. Use msedge for installed Microsoft Edge.",
    )
    parser.add_argument(
        "--skip-supabase",
        action="store_true",
        help="Do not register scrape results in Supabase.",
    )
    parser.add_argument(
        "--analyze-pending",
        action="store_true",
        help="After scraping, analyze pending videos with the selected backend.",
    )
    parser.add_argument(
        "--analysis-backend",
        choices=("local", "gemini", "skill_seekers", "hf_video_direct"),
        default="local",
        help="Analysis backend to run when --analyze-pending is enabled.",
    )
    parser.add_argument(
        "--model",
        default="gemini-2.5-flash",
        help="Model override for backends that need one, such as Gemini.",
    )
    parser.add_argument(
        "--analysis-output-dir",
        default="data/knowledge/video_knowledge_drafts/from_scrape",
        help="Directory to save analysis artifacts when --analyze-pending is enabled.",
    )
    parser.add_argument("--headful", action="store_true", help="Run with a visible browser window.")
    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()

    videos = scrape_channel_shorts(
        channel_url=args.channel_url,
        limit=args.limit,
        order=args.order,
        browser_channel=args.browser_channel,
        headless=not args.headful,
    )

    state_path = Path(args.state_file)
    output_path = Path(args.output_file)
    state = load_seen_state(state_path)
    new_videos = diff_new_videos(videos, set(state.get("seen_video_ids", [])))
    updated_state = update_seen_state(
        state=state,
        channel_url=args.channel_url,
        order=args.order,
        limit=args.limit,
        videos=videos,
    )
    save_seen_state(state_path, updated_state)

    scrape_registry = None
    pending_videos = new_videos
    analyzed_videos: list = []
    if not args.skip_supabase:
        scrape_registry = YoutubeScrapeStore().record_scrape_run(
            channel_url=args.channel_url,
            order=args.order,
            limit=args.limit,
            browser_channel=args.browser_channel,
            videos=videos,
        )
        analyzed_ids = set(scrape_registry["analyzed_video_ids"])
        pending_videos = [video for video in videos if video.video_id not in analyzed_ids]
        analyzed_videos = [video for video in videos if video.video_id in analyzed_ids]

    analysis_results = None
    analysis_output_dir = None
    if args.analyze_pending:
        analysis_output_dir = Path(args.analysis_output_dir).resolve()
        analysis_output_dir.mkdir(parents=True, exist_ok=True)
        if args.analysis_backend == "local":
            analysis_results = run_local_pipeline(pending_videos, analysis_output_dir)
        elif args.analysis_backend == "gemini":
            analysis_results = run_gemini_pipeline(pending_videos, analysis_output_dir, model=args.model)
        else:
            raise SystemExit(
                f"Analysis backend '{args.analysis_backend}' is reserved for future implementation. "
                "Use 'local' or 'gemini' for now."
            )
        scrape_registry = YoutubeScrapeStore().record_scrape_run(
            channel_url=args.channel_url,
            order=args.order,
            limit=args.limit,
            browser_channel=args.browser_channel,
            videos=videos,
        )
        analyzed_ids = set(scrape_registry["analyzed_video_ids"])
        pending_videos = [video for video in videos if video.video_id not in analyzed_ids]
        analyzed_videos = [video for video in videos if video.video_id in analyzed_ids]

    output_path.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "channel_url": args.channel_url,
        "order": args.order,
        "limit": args.limit,
        "browser_channel": args.browser_channel,
        "total_found": len(videos),
        "new_found": len(new_videos),
        "pending_in_supabase": len(pending_videos),
        "already_analyzed_in_supabase": len(analyzed_videos),
        "videos": [item.to_dict() for item in videos],
        "new_videos": [item.to_dict() for item in new_videos],
        "pending_videos": [item.to_dict() for item in pending_videos],
        "already_analyzed_videos": [item.to_dict() for item in analyzed_videos],
        "state_file": str(state_path),
        "analysis_backend": args.analysis_backend if args.analyze_pending else None,
        "analysis_output_dir": str(analysis_output_dir) if analysis_output_dir is not None else None,
        "analysis_results": analysis_results,
        "supabase_registry": {
            **scrape_registry,
            "analyzed_video_ids": sorted(scrape_registry["analyzed_video_ids"]),
            "pending_videos": [item.to_dict() for item in scrape_registry["pending_videos"]],
        }
        if scrape_registry is not None
        else None,
    }
    output_path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")

    print(f"Found {len(videos)} videos.")
    print(f"New videos: {len(new_videos)}")
    if scrape_registry is not None:
        print(f"Pending in Supabase: {len(pending_videos)}")
        print(f"Already analyzed in Supabase: {len(analyzed_videos)}")
    if analysis_results is not None:
        print(f"Analyzed in this run: {len(analysis_results)}")
    print(f"Snapshot saved to: {output_path}")
    print(f"State saved to: {state_path}")


if __name__ == "__main__":
    main()
