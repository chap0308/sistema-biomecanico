"""Build cleaned transcripts and descriptive tables from downloaded YouTube Shorts metadata."""

from __future__ import annotations

import csv
import json
import re
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
BATCH_DIR = ROOT / "data" / "to-learn" / "youtube_batch"
OUT_DIR = ROOT / "data" / "to-learn" / "youtube_analysis"


def _clean_vtt(path: Path) -> str:
    text = path.read_text(encoding="utf-8")
    lines = []
    for raw_line in text.splitlines():
        line = raw_line.strip()
        if not line:
            continue
        if line.startswith("WEBVTT") or line.startswith("Kind:") or line.startswith("Language:"):
            continue
        if "-->" in line:
            continue
        line = re.sub(r"<\d{2}:\d{2}:\d{2}\.\d{3}>", "", line)
        line = re.sub(r"</?c>", "", line)
        line = re.sub(r"<[^>]+>", "", line)
        line = re.sub(r"\s+", " ", line).strip()
        if line:
            lines.append(line)

    deduped: list[str] = []
    for line in lines:
        if deduped and deduped[-1] == line:
            continue
        deduped.append(line)

    transcript = " ".join(deduped)
    transcript = re.sub(r"\s+", " ", transcript).strip()
    return transcript


def _infer_region(title: str, transcript: str) -> str:
    corpus = f"{title} {transcript}".lower()
    if any(token in corpus for token in ("foot", "feet", "arch", "flat feet")):
        return "foot_ankle"
    if any(token in corpus for token in ("hip", "psoas", "cross your legs", "femur")):
        return "hip_pelvis"
    if any(token in corpus for token in ("tmj", "jaw")):
        return "jaw_cervical"
    if any(token in corpus for token in ("rotator cuff", "scapular", "lower traps", "upper traps", "rounded shoulders", "shoulder", "upper back")):
        return "shoulder_scapula_thorax"
    return "uncategorized"


def _infer_content_type(title: str, transcript: str) -> str:
    corpus = f"{title} {transcript}".lower()
    if "habit" in corpus or "posture" in corpus:
        return "habit_and_corrective"
    if "why" in title.lower():
        return "problem_mechanism_and_fix"
    if "how to" in title.lower() or "fix" in title.lower():
        return "corrective_protocol"
    return "educational_protocol"


def _infer_delivery_type(title: str, transcript: str) -> str:
    corpus = f"{title} {transcript}".lower()
    has_release = any(token in corpus for token in ("foam roll", "lacrosse ball", "roll", "ball"))
    has_strength = any(token in corpus for token in ("band", "cable", "exercise", "lower traps", "rotator cuff", "triceps"))
    has_breath = any(token in corpus for token in ("breathe", "breath", "inhale", "exhale", "rib cage", "chest wall"))
    has_mobility = any(token in corpus for token in ("stretch", "mobility", "range of motion", "glide"))
    parts = []
    if has_release:
        parts.append("release")
    if has_breath:
        parts.append("breathing")
    if has_mobility:
        parts.append("mobility")
    if has_strength:
        parts.append("strength")
    return "+".join(parts) if parts else "education"


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    videos: list[dict[str, str]] = []
    regions = Counter()
    delivery_types = Counter()
    content_types = Counter()

    for info_path in sorted(BATCH_DIR.glob("*.info.json")):
        meta = json.loads(info_path.read_text(encoding="utf-8"))
        video_id = str(meta["id"])
        vtt_path = BATCH_DIR / f"{video_id}.en.vtt"
        transcript = _clean_vtt(vtt_path)
        region = _infer_region(str(meta.get("title", "")), transcript)
        content_type = _infer_content_type(str(meta.get("title", "")), transcript)
        delivery_type = _infer_delivery_type(str(meta.get("title", "")), transcript)

        record = {
            "video_id": video_id,
            "title": str(meta.get("title", "")),
            "url": str(meta.get("webpage_url", "")),
            "uploader": str(meta.get("uploader", "")),
            "upload_date": str(meta.get("upload_date", "")),
            "duration_sec": str(meta.get("duration", "")),
            "duration_human": str(meta.get("duration_string", "")),
            "body_region_guess": region,
            "content_type_guess": content_type,
            "delivery_type_guess": delivery_type,
            "transcript_clean": transcript,
        }
        videos.append(record)
        regions[region] += 1
        content_types[content_type] += 1
        delivery_types[delivery_type] += 1

        (OUT_DIR / f"{video_id}.txt").write_text(transcript, encoding="utf-8")

    with (OUT_DIR / "youtube_videos_cleaned.json").open("w", encoding="utf-8") as handle:
        json.dump(videos, handle, indent=2, ensure_ascii=False)

    with (OUT_DIR / "youtube_videos_overview.csv").open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=[
                "video_id",
                "title",
                "url",
                "uploader",
                "upload_date",
                "duration_sec",
                "duration_human",
                "body_region_guess",
                "content_type_guess",
                "delivery_type_guess",
            ],
        )
        writer.writeheader()
        for row in videos:
            writer.writerow({key: row[key] for key in writer.fieldnames})

    with (OUT_DIR / "youtube_dataset_summary.md").open("w", encoding="utf-8") as handle:
        handle.write("# YouTube Shorts Dataset Summary\n\n")
        handle.write(f"- Videos analyzed: {len(videos)}\n")
        handle.write("- Source folder: `data/to-learn/youtube_batch`\n\n")
        handle.write("## Body Region Guess Counts\n\n")
        for key, value in sorted(regions.items()):
            handle.write(f"- `{key}`: {value}\n")
        handle.write("\n## Content Type Guess Counts\n\n")
        for key, value in sorted(content_types.items()):
            handle.write(f"- `{key}`: {value}\n")
        handle.write("\n## Delivery Type Guess Counts\n\n")
        for key, value in sorted(delivery_types.items()):
            handle.write(f"- `{key}`: {value}\n")

if __name__ == "__main__":
    main()
