"""Local ASR helpers built around ffmpeg and faster-whisper."""

from __future__ import annotations

import os
import shutil
import subprocess
from dataclasses import dataclass
from pathlib import Path


@dataclass(slots=True)
class TranscriptSegment:
    """One transcript span produced by the local ASR pipeline."""

    start_sec: float
    end_sec: float
    text: str
    confidence: float | None = None


@dataclass(slots=True)
class TranscriptResult:
    """Structured transcript result with status and text spans."""

    text: str
    segments: list[TranscriptSegment]
    status: str
    confidence: float | None = None


def ffmpeg_available() -> bool:
    """Return whether ffmpeg is available in PATH."""
    return _resolve_ffmpeg_cmd() is not None


def _resolve_ffmpeg_cmd() -> str | None:
    """Resolve ffmpeg from env, PATH, or the common WinGet install location."""
    env_cmd = os.getenv("FFMPEG_CMD", "").strip().strip('"')
    if env_cmd and Path(env_cmd).exists():
        return env_cmd

    from_path = shutil.which("ffmpeg")
    if from_path:
        return from_path

    winget_root = Path.home() / "AppData" / "Local" / "Microsoft" / "WinGet" / "Packages"
    if winget_root.exists():
        matches = sorted(winget_root.glob("**/ffmpeg.exe"))
        if matches:
            return str(matches[0])

    return None


def extract_audio_ffmpeg(video_path: str | Path, output_path: str | Path) -> Path | None:
    """Extract mono 16 kHz wav audio with ffmpeg when available."""
    ffmpeg_cmd = _resolve_ffmpeg_cmd()
    if not ffmpeg_cmd:
        return None

    source = Path(video_path)
    destination = Path(output_path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    command = [
        ffmpeg_cmd,
        "-y",
        "-i",
        str(source),
        "-vn",
        "-acodec",
        "pcm_s16le",
        "-ar",
        "16000",
        "-ac",
        "1",
        str(destination),
    ]
    completed = subprocess.run(command, capture_output=True, text=True, check=False)
    if completed.returncode != 0 or not destination.exists():
        return None
    return destination


def transcribe_audio(
    audio_path: str | Path,
    *,
    language: str = "es",
    model_size: str = "tiny",
) -> TranscriptResult:
    """Transcribe audio with faster-whisper if it is available."""
    try:
        from faster_whisper import WhisperModel
    except Exception:
        return TranscriptResult(text="", segments=[], status="faster_whisper_unavailable")

    audio_file = Path(audio_path)
    if not audio_file.exists():
        return TranscriptResult(text="", segments=[], status="audio_missing")

    try:
        model = WhisperModel(model_size, device="cpu", compute_type="int8")
        raw_segments, info = model.transcribe(str(audio_file), language=language, vad_filter=True)
        segments: list[TranscriptSegment] = []
        full_text_parts: list[str] = []
        confidences: list[float] = []
        for raw_segment in raw_segments:
            text = (raw_segment.text or "").strip()
            if not text:
                continue
            no_speech_prob = getattr(raw_segment, "no_speech_prob", None)
            confidence = None
            if no_speech_prob is not None:
                confidence = max(0.0, min(1.0, 1.0 - float(no_speech_prob)))
                confidences.append(confidence)
            segments.append(
                TranscriptSegment(
                    start_sec=float(raw_segment.start),
                    end_sec=float(raw_segment.end),
                    text=text,
                    confidence=confidence,
                )
            )
            full_text_parts.append(text)
        aggregate_confidence = sum(confidences) / len(confidences) if confidences else None
        status = "ok" if segments else "empty_transcript"
        language_out = getattr(info, "language", None)
        if language_out and language_out != language:
            status = f"{status}:{language_out}"
        return TranscriptResult(
            text=" ".join(full_text_parts).strip(),
            segments=segments,
            status=status,
            confidence=aggregate_confidence,
        )
    except Exception:
        return TranscriptResult(text="", segments=[], status="transcription_failed")
