"""Local-first Level 1 video pipeline."""

from __future__ import annotations

from pathlib import Path

from src.analysis.frame_sampler import sample_scene_keyframes
from src.analysis.ocr import run_ocr_on_frames
from src.analysis.scene_detect import detect_scenes
from src.analysis.whisper_asr import extract_audio_ffmpeg, transcribe_audio
from src.analysis.youtube_fetch import download_youtube_video, fetch_youtube_metadata
from src.chunking.align_segments import align_signals_to_segments
from src.chunking.segment_builder import build_segment
from src.core.models import Asset, Segment, Source


def process_video_local(source: Source) -> dict[str, object]:
    """Process a source with the local Level 1 pipeline when possible."""
    if source.source_type == "youtube":
        return _process_youtube_source(source)

    if source.source_type != "local_video":
        return _build_bootstrap_payload(source, reason="non_local_source")

    video_path = Path(source.uri)
    if not video_path.exists():
        return _build_bootstrap_payload(source, reason="missing_local_video")

    return _process_video_file(source, video_path)


def _process_youtube_source(source: Source) -> dict[str, object]:
    """Acquire a YouTube video locally, then process it like a local file."""
    work_dir = Path("data/processed/rag") / (source.source_id or "unknown_source")
    metadata, metadata_status = fetch_youtube_metadata(source.uri)
    if not source.title and metadata.title:
        source.title = metadata.title
    if not source.channel_or_author and metadata.uploader:
        source.channel_or_author = metadata.uploader
    if source.duration_sec is None and metadata.duration_sec is not None:
        source.duration_sec = metadata.duration_sec

    downloaded_video, download_status = download_youtube_video(
        source.uri,
        work_dir / "downloads",
        filename_stem="source",
    )
    if downloaded_video is None:
        payload = _build_bootstrap_payload(source, reason=f"youtube_{download_status}")
        payload["analysis_report"]["metadata_status"] = metadata_status
        payload["analysis_report"]["download_status"] = download_status
        return payload

    payload = _process_video_file(source, downloaded_video)
    payload["analysis_report"]["metadata_status"] = metadata_status
    payload["analysis_report"]["download_status"] = download_status
    for asset in payload["assets"]:
        if asset.kind == "video" and asset.path == str(downloaded_video):
            asset.metadata["origin"] = "youtube_download"
            break
    return payload


def _process_video_file(source: Source, video_path: Path) -> dict[str, object]:
    """Run the local Level 1 pipeline over a concrete local video file."""
    source.ingest_status = "processing_local_level1"
    work_dir = Path("data/processed/rag") / (source.source_id or "unknown_source")
    frames_dir = work_dir / "frames"
    audio_path = work_dir / "audio.wav"
    work_dir.mkdir(parents=True, exist_ok=True)

    assets: list[Asset] = []
    assets.append(
        Asset(
            source_id=source.source_id or "",
            kind="video",
            path=str(video_path),
            mime_type=_guess_video_mime_type(video_path.suffix),
            end_sec=source.duration_sec,
            metadata={"pipeline_level": 1},
        )
    )

    extracted_audio = extract_audio_ffmpeg(video_path, audio_path)
    transcript_status = "audio_not_extracted"
    transcript_result = None
    if extracted_audio is not None:
        assets.append(
            Asset(
                source_id=source.source_id or "",
                kind="audio",
                path=str(extracted_audio),
                mime_type="audio/wav",
                end_sec=source.duration_sec,
                metadata={"pipeline_level": 1, "extractor": "ffmpeg"},
            )
        )
        transcript_result = transcribe_audio(extracted_audio, language=source.language_hint)
        transcript_status = transcript_result.status
        transcript_path = work_dir / "transcript.txt"
        transcript_path.write_text(transcript_result.text, encoding="utf-8")
        assets.append(
            Asset(
                source_id=source.source_id or "",
                kind="transcript",
                path=str(transcript_path),
                mime_type="text/plain",
                end_sec=source.duration_sec,
                metadata={"pipeline_level": 1, "status": transcript_result.status},
            )
        )

    scenes, scene_status = detect_scenes(video_path, fallback_duration_sec=source.duration_sec)
    frame_samples, frame_status = sample_scene_keyframes(video_path, scenes=scenes, output_dir=frames_dir)
    for frame in frame_samples:
        assets.append(
            Asset(
                source_id=source.source_id or "",
                kind="frame",
                path=frame.path,
                mime_type="image/jpeg",
                start_sec=frame.sec,
                end_sec=frame.sec,
                metadata={"pipeline_level": 1},
            )
        )

    ocr_observations, ocr_status = run_ocr_on_frames([(item.sec, item.path) for item in frame_samples])
    if ocr_observations:
        ocr_path = work_dir / "ocr.txt"
        ocr_path.write_text("\n".join(item.text for item in ocr_observations), encoding="utf-8")
        assets.append(
            Asset(
                source_id=source.source_id or "",
                kind="ocr",
                path=str(ocr_path),
                mime_type="text/plain",
                end_sec=source.duration_sec,
                metadata={"pipeline_level": 1, "status": ocr_status},
            )
        )

    transcript_segments = transcript_result.segments if transcript_result is not None else []
    segments, alignment_report = align_signals_to_segments(
        source=source,
        scenes=scenes,
        transcript_segments=transcript_segments,
        ocr_observations=ocr_observations,
        frame_samples=frame_samples,
    )
    source.ingest_status = "processed_local_level1"
    return {
            "source": source,
            "assets": assets,
            "segments": segments,
            "pipeline": "process_video_local",
            "status": "processed_local_level1",
        "analysis_report": {
            "audio_extracted": extracted_audio is not None,
            "transcript_status": transcript_status,
            "scene_status": scene_status,
            "frame_status": frame_status,
            "ocr_status": ocr_status,
            "segment_alignment_status": alignment_report.status,
            "scene_count": alignment_report.scene_count,
            "transcript_segment_count": alignment_report.transcript_segment_count,
            "ocr_observation_count": alignment_report.ocr_observation_count,
            },
    }

def _guess_video_mime_type(suffix: str) -> str:
    normalized = suffix.lower()
    if normalized == ".mp4":
        return "video/mp4"
    if normalized == ".mov":
        return "video/quicktime"
    if normalized == ".avi":
        return "video/x-msvideo"
    return "application/octet-stream"


def _build_bootstrap_payload(source: Source, *, reason: str) -> dict[str, object]:
    segment = build_segment(
        source_id=source.source_id or "",
        segment_index=1,
        start_sec=0.0,
        end_sec=source.duration_sec or 10.0,
        transcript=source.title or "",
        segment_summary=f"Bootstrap segment for {source.title or source.uri}",
        topics=list(source.tags),
        keywords=list(source.tags),
        payload={
            "source_type": source.source_type,
            "course_id": source.course_id,
            "title": source.title or "",
            "uri": source.canonical_uri or source.uri,
            "channel_or_author": source.channel_or_author or "",
        },
    )
    segment.language = source.language_hint
    assets: list[Asset] = []
    if source.source_type in {"local_video", "youtube"}:
        path = Path(source.uri)
        assets.append(
            Asset(
                source_id=source.source_id or "",
                kind="video",
                path=str(path),
                mime_type=_guess_video_mime_type(path.suffix),
                end_sec=source.duration_sec,
                metadata={"bootstrap_only": True, "reason": reason},
            )
        )
    return {
        "source": source,
        "assets": assets,
        "segments": [segment],
        "pipeline": "process_video_local",
        "status": "bootstrap_ready",
        "analysis_report": {
            "reason": reason,
            "audio_extracted": False,
            "transcript_status": "not_attempted",
            "scene_status": "not_attempted",
            "frame_status": "not_attempted",
            "ocr_status": "not_attempted",
            "segment_alignment_status": "bootstrap",
            "scene_count": 0,
            "transcript_segment_count": 0,
            "ocr_observation_count": 0,
        },
    }
