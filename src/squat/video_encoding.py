"""Browser-compatible video encoding helpers for squat artifacts."""

from __future__ import annotations

import json
from pathlib import Path
import shutil
import subprocess


class VideoEncodingError(RuntimeError):
    """Raised when a web-compatible MP4 cannot be produced."""


def _resolve_media_command(name: str) -> str | None:
    executable = shutil.which(name)
    if executable:
        return executable

    winget_root = (
        Path.home()
        / "AppData"
        / "Local"
        / "Microsoft"
        / "WinGet"
        / "Packages"
    )
    executable_name = f"{name}.exe"
    if winget_root.exists():
        matches = sorted(winget_root.glob(f"**/{executable_name}"))
        if matches:
            return str(matches[-1])
    return None


def probe_video_codec(video_path: str | Path) -> dict[str, str]:
    """Return codec metadata for the first video stream using ffprobe."""
    ffprobe = _resolve_media_command("ffprobe")
    if not ffprobe:
        raise VideoEncodingError("ffprobe is required to validate generated videos.")

    result = subprocess.run(
        [
            ffprobe,
            "-v",
            "error",
            "-select_streams",
            "v:0",
            "-show_entries",
            "stream=codec_name,codec_tag_string,pix_fmt",
            "-of",
            "json",
            str(Path(video_path)),
        ],
        capture_output=True,
        check=False,
        text=True,
        encoding="utf-8",
    )
    if result.returncode != 0:
        raise VideoEncodingError(
            f"Unable to inspect generated video: {result.stderr.strip()}"
        )
    streams = json.loads(result.stdout).get("streams", [])
    if not streams:
        raise VideoEncodingError("Generated video does not contain a video stream.")
    return {key: str(value) for key, value in streams[0].items()}


def encode_h264_mp4(source_path: str | Path, destination_path: str | Path) -> Path:
    """Transcode an intermediate video to a browser-compatible H.264 MP4."""
    ffmpeg = _resolve_media_command("ffmpeg")
    if not ffmpeg:
        raise VideoEncodingError(
            "FFmpeg with libx264 is required to generate browser-compatible MP4 files."
        )

    source = Path(source_path)
    destination = Path(destination_path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    temporary = destination.with_suffix(".h264.part.mp4")
    temporary.unlink(missing_ok=True)

    result = subprocess.run(
        [
            ffmpeg,
            "-y",
            "-v",
            "error",
            "-i",
            str(source),
            "-map",
            "0:v:0",
            "-an",
            "-vf",
            "pad=ceil(iw/2)*2:ceil(ih/2)*2",
            "-c:v",
            "libx264",
            "-preset",
            "veryfast",
            "-crf",
            "20",
            "-pix_fmt",
            "yuv420p",
            "-tag:v",
            "avc1",
            "-movflags",
            "+faststart",
            str(temporary),
        ],
        capture_output=True,
        check=False,
        text=True,
        encoding="utf-8",
    )
    if result.returncode != 0:
        temporary.unlink(missing_ok=True)
        raise VideoEncodingError(
            f"FFmpeg could not generate H.264 video: {result.stderr.strip()}"
        )

    codec = probe_video_codec(temporary)
    if codec.get("codec_name") != "h264" or codec.get("pix_fmt") != "yuv420p":
        temporary.unlink(missing_ok=True)
        raise VideoEncodingError(f"Unexpected generated video codec: {codec}")

    temporary.replace(destination)
    source.unlink(missing_ok=True)
    return destination


def normalize_h264_mp4(video_path: str | Path) -> bool:
    """Convert one existing MP4 in place; return False when already compatible."""
    path = Path(video_path)
    codec = probe_video_codec(path)
    if codec.get("codec_name") == "h264" and codec.get("pix_fmt") == "yuv420p":
        return False

    intermediate = path.with_suffix(".source.mp4")
    intermediate.unlink(missing_ok=True)
    path.replace(intermediate)
    try:
        encode_h264_mp4(intermediate, path)
    except Exception:
        if not path.exists() and intermediate.exists():
            intermediate.replace(path)
        raise
    return True


__all__ = [
    "VideoEncodingError",
    "encode_h264_mp4",
    "normalize_h264_mp4",
    "probe_video_codec",
]
