"""YouTube acquisition helpers for the local Level 1 pipeline."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from src.analysis.whisper_asr import _resolve_ffmpeg_cmd


@dataclass(slots=True)
class YoutubeMetadata:
    """Subset of YouTube metadata needed by the local pipeline."""

    title: str | None = None
    uploader: str | None = None
    duration_sec: float | None = None


def fetch_youtube_metadata(url: str) -> tuple[YoutubeMetadata, str]:
    """Fetch lightweight YouTube metadata without downloading media."""
    try:
        from yt_dlp import YoutubeDL
    except Exception:
        return YoutubeMetadata(), "yt_dlp_unavailable"

    options = {
        "quiet": True,
        "skip_download": True,
        "no_warnings": True,
        "extract_flat": False,
    }
    try:
        with YoutubeDL(options) as ydl:
            info = ydl.extract_info(url, download=False)
        return (
            YoutubeMetadata(
                title=info.get("title"),
                uploader=info.get("uploader"),
                duration_sec=float(info["duration"]) if info.get("duration") else None,
            ),
            "ok",
        )
    except Exception:
        return YoutubeMetadata(), "metadata_failed"


def download_youtube_video(url: str, output_dir: str | Path, *, filename_stem: str = "source") -> tuple[Path | None, str]:
    """Download one YouTube video to a local mp4 file using yt-dlp."""
    try:
        from yt_dlp import YoutubeDL
    except Exception:
        return None, "yt_dlp_unavailable"

    destination_dir = Path(output_dir)
    destination_dir.mkdir(parents=True, exist_ok=True)
    output_template = str(destination_dir / f"{filename_stem}.%(ext)s")
    ffmpeg_cmd = _resolve_ffmpeg_cmd()
    options = {
        "quiet": True,
        "no_warnings": True,
        "noplaylist": True,
        "format": "best[ext=mp4]/bestvideo[ext=mp4]+bestaudio[ext=m4a]/best",
        "merge_output_format": "mp4",
        "outtmpl": output_template,
    }
    if ffmpeg_cmd:
        options["ffmpeg_location"] = str(Path(ffmpeg_cmd).parent)
    try:
        with YoutubeDL(options) as ydl:
            ydl.download([url])
    except Exception:
        return None, "download_failed"

    candidates = sorted(destination_dir.glob(f"{filename_stem}.*"))
    for candidate in candidates:
        if candidate.suffix.lower() in {".mp4", ".mkv", ".webm", ".mov"}:
            return candidate, "ok"
    return None, "download_missing"
