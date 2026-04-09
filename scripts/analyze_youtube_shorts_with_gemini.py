"""Analyze selected YouTube Shorts with Gemini and save structured knowledge drafts."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from video.gemini_knowledge import analyze_youtube_video, save_analysis
from video.video_knowledge_registry import (
    append_run,
    get_analyzed_video_ids,
    load_registry,
    register_analysis,
    save_registry,
)
from video.youtube_shorts import scrape_channel_shorts


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description='Analyze selected YouTube Shorts with Gemini.')
    parser.add_argument('--channel-url', required=True)
    parser.add_argument('--order', choices=('newest', 'popular', 'oldest'), default='newest')
    parser.add_argument('--start-rank', type=int, required=True, help='1-based inclusive start rank.')
    parser.add_argument('--end-rank', type=int, required=True, help='1-based inclusive end rank.')
    parser.add_argument('--browser-channel', default='msedge')
    parser.add_argument('--model', default='gemini-2.5-flash')
    parser.add_argument(
        '--output-dir',
        default='data/knowledge/video_knowledge_drafts',
        help='Directory to save individual and aggregate JSON outputs.',
    )
    parser.add_argument(
        '--registry-file',
        default='data/knowledge/video_knowledge_registry.json',
        help='JSON registry used to skip already analyzed videos.',
    )
    parser.add_argument(
        '--include-analyzed',
        action='store_true',
        help='Re-analyze videos even if they already exist in the registry.',
    )
    parser.add_argument('--headful', action='store_true')
    return parser


def main() -> None:
    args = build_parser().parse_args()
    if args.start_rank < 1 or args.end_rank < args.start_rank:
        raise SystemExit('Invalid rank range.')

    scrape_limit = args.end_rank
    videos = scrape_channel_shorts(
        channel_url=args.channel_url,
        limit=scrape_limit,
        order=args.order,
        browser_channel=args.browser_channel,
        headless=not args.headful,
    )
    selected = videos[args.start_rank - 1 : args.end_rank]
    out_dir = Path(args.output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    registry_path = Path(args.registry_file)
    registry = load_registry(registry_path)
    analyzed_ids = get_analyzed_video_ids(registry)

    pending = selected if args.include_analyzed else [video for video in selected if video.video_id not in analyzed_ids]
    skipped = [] if args.include_analyzed else [video for video in selected if video.video_id in analyzed_ids]

    aggregate: list[dict] = []
    analyzed_video_ids: list[str] = []
    for video in pending:
        analysis = analyze_youtube_video(
            video_url=video.url,
            title_hint=video.title,
            model=args.model,
        )
        output_path = out_dir / f'{video.order_index + 1:03d}_{video.video_id}.json'
        save_analysis(output_path, analysis)
        aggregate.append({
            'rank': video.order_index + 1,
            'video_id': video.video_id,
            'url': video.url,
            'title': video.title,
            'analysis_file': str(output_path),
            'analysis': analysis.model_dump(mode='json'),
        })
        registry = register_analysis(
            registry=registry,
            video_id=video.video_id,
            video_url=video.url,
            title=video.title,
            channel_url=args.channel_url,
            order=args.order,
            rank=video.order_index + 1,
            model=args.model,
            analysis_file=str(output_path),
            usefulness=analysis.classification.usefulness.value,
            content_kind=analysis.classification.content_kind.value,
        )
        analyzed_video_ids.append(video.video_id)
        print(f'Analyzed rank {video.order_index + 1}: {video.video_id}')

    aggregate_path = out_dir / f'aggregate_{args.order}_{args.start_rank}_{args.end_rank}.json'
    aggregate_path.write_text(json.dumps(aggregate, indent=2, ensure_ascii=False), encoding='utf-8')
    run_summary = {
        'channel_url': args.channel_url,
        'order': args.order,
        'start_rank': args.start_rank,
        'end_rank': args.end_rank,
        'selected_count': len(selected),
        'pending_count': len(pending),
        'skipped_count': len(skipped),
        'analyzed_video_ids': analyzed_video_ids,
        'skipped_video_ids': [video.video_id for video in skipped],
        'registry_file': str(registry_path),
        'aggregate_file': str(aggregate_path),
    }
    (out_dir / 'run_summary.json').write_text(json.dumps(run_summary, indent=2, ensure_ascii=False), encoding='utf-8')
    registry = append_run(
        registry=registry,
        channel_url=args.channel_url,
        order=args.order,
        start_rank=args.start_rank,
        end_rank=args.end_rank,
        analyzed_video_ids=analyzed_video_ids,
        skipped_video_ids=[video.video_id for video in skipped],
        model=args.model,
    )
    save_registry(registry_path, registry)
    print(f'Aggregate saved to: {aggregate_path}')
    print(f'Pending videos analyzed: {len(pending)}')
    print(f'Skipped already analyzed: {len(skipped)}')
    print(f'Registry saved to: {registry_path}')


if __name__ == '__main__':
    main()
