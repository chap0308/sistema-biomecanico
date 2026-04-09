"""Tests for the Level 1 local video pipeline."""

import shutil
import uuid
from pathlib import Path

from src.analysis.frame_sampler import FrameSample
from src.analysis.ocr import OcrObservation
from src.analysis.scene_detect import SceneBoundary
from src.analysis.whisper_asr import TranscriptResult, TranscriptSegment
from src.chunking.align_segments import align_signals_to_segments
from src.core.models import Source
from src.pipelines import process_video_local as process_video_local_module


def test_align_signals_to_segments_builds_multimodal_segment() -> None:
    source = Source(
        source_type="local_video",
        uri="D:/videos/demo.mp4",
        title="Demo drill",
        tags=["hip", "rotation"],
        duration_sec=18.0,
    )
    segments, report = align_signals_to_segments(
        source=source,
        scenes=[SceneBoundary(0.0, 8.0)],
        transcript_segments=[TranscriptSegment(0.0, 5.0, "Rotate through the hip, not the spine.", 0.9)],
        ocr_observations=[OcrObservation(3.0, "frame.jpg", "HIP ROTATION", None)],
        frame_samples=[FrameSample(3.0, "frame.jpg")],
    )

    assert report.status == "ok"
    assert len(segments) == 1
    assert "Rotate through the hip" in segments[0].transcript
    assert "HIP ROTATION" in segments[0].ocr_text
    assert segments[0].frame_refs
    assert "hip" in segments[0].retrieval_text.lower()


def test_process_video_local_falls_back_for_missing_file() -> None:
    source = Source(
        source_type="local_video",
        uri="D:/missing/video.mp4",
        title="Missing video",
        duration_sec=12.0,
        tags=["scapula"],
    )

    result = process_video_local_module.process_video_local(source)

    assert result["status"] == "bootstrap_ready"
    assert result["analysis_report"]["reason"] == "missing_local_video"
    assert len(result["segments"]) == 1


def test_process_video_local_runs_level1_when_dependencies_are_mocked() -> None:
    test_dir = Path("data/test-local-video") / f"video_{uuid.uuid4().hex}"
    shutil.rmtree(test_dir, ignore_errors=True)
    test_dir.mkdir(parents=True, exist_ok=True)
    video_path = test_dir / "demo.mp4"
    video_path.write_bytes(b"fake video")

    source = Source(
        source_type="local_video",
        uri=str(video_path.resolve()),
        title="Hip tutorial",
        duration_sec=24.0,
        tags=["hip", "mobility"],
    )

    work_audio = test_dir / "audio.wav"
    work_audio.write_bytes(b"fake audio")
    frame_path = test_dir / "frame.jpg"
    frame_path.write_bytes(b"fake frame")

    original_extract = process_video_local_module.extract_audio_ffmpeg
    original_transcribe = process_video_local_module.transcribe_audio
    original_detect = process_video_local_module.detect_scenes
    original_sample = process_video_local_module.sample_scene_keyframes
    original_ocr = process_video_local_module.run_ocr_on_frames

    process_video_local_module.extract_audio_ffmpeg = lambda *_args, **_kwargs: work_audio
    process_video_local_module.transcribe_audio = lambda *_args, **_kwargs: TranscriptResult(
        text="Keep the ribs down and rotate through the hip.",
        segments=[TranscriptSegment(0.0, 7.0, "Keep the ribs down and rotate through the hip.", 0.8)],
        status="ok",
        confidence=0.8,
    )
    process_video_local_module.detect_scenes = lambda *_args, **_kwargs: ([SceneBoundary(0.0, 10.0)], "ok")
    process_video_local_module.sample_scene_keyframes = (
        lambda *_args, **_kwargs: ([FrameSample(5.0, str(frame_path.resolve()))], "ok")
    )
    process_video_local_module.run_ocr_on_frames = (
        lambda *_args, **_kwargs: ([OcrObservation(5.0, str(frame_path.resolve()), "RIBS DOWN", None)], "ok")
    )

    try:
        result = process_video_local_module.process_video_local(source)
    finally:
        process_video_local_module.extract_audio_ffmpeg = original_extract
        process_video_local_module.transcribe_audio = original_transcribe
        process_video_local_module.detect_scenes = original_detect
        process_video_local_module.sample_scene_keyframes = original_sample
        process_video_local_module.run_ocr_on_frames = original_ocr
        shutil.rmtree(test_dir, ignore_errors=True)

    assert result["status"] == "processed_local_level1"
    assert result["analysis_report"]["transcript_status"] == "ok"
    assert result["analysis_report"]["scene_count"] == 1
    assert len(result["segments"]) == 1
    assert "rotate through the hip" in result["segments"][0].retrieval_text.lower()
    assert any(asset.kind == "audio" for asset in result["assets"])


def test_process_video_local_processes_youtube_when_download_is_mocked() -> None:
    test_dir = Path("data/test-youtube-level1") / f"video_{uuid.uuid4().hex}"
    shutil.rmtree(test_dir, ignore_errors=True)
    test_dir.mkdir(parents=True, exist_ok=True)
    downloaded_path = test_dir / "downloaded.mp4"
    downloaded_path.write_bytes(b"fake youtube video")
    frame_path = test_dir / "frame.jpg"
    frame_path.write_bytes(b"fake frame")
    audio_path = test_dir / "audio.wav"
    audio_path.write_bytes(b"fake audio")

    source = Source(
        source_type="youtube",
        uri="https://www.youtube.com/shorts/example123",
        title=None,
        duration_sec=None,
        tags=["foot", "ankle"],
    )

    original_fetch = process_video_local_module.fetch_youtube_metadata
    original_download = process_video_local_module.download_youtube_video
    original_extract = process_video_local_module.extract_audio_ffmpeg
    original_transcribe = process_video_local_module.transcribe_audio
    original_detect = process_video_local_module.detect_scenes
    original_sample = process_video_local_module.sample_scene_keyframes
    original_ocr = process_video_local_module.run_ocr_on_frames

    from src.analysis.youtube_fetch import YoutubeMetadata

    process_video_local_module.fetch_youtube_metadata = (
        lambda *_args, **_kwargs: (YoutubeMetadata(title="Foot Drill", uploader="Conor", duration_sec=35.0), "ok")
    )
    process_video_local_module.download_youtube_video = lambda *_args, **_kwargs: (downloaded_path, "ok")
    process_video_local_module.extract_audio_ffmpeg = lambda *_args, **_kwargs: audio_path
    process_video_local_module.transcribe_audio = lambda *_args, **_kwargs: TranscriptResult(
        text="Use the ball under the foot and keep three points of contact.",
        segments=[TranscriptSegment(0.0, 6.0, "Use the ball under the foot and keep three points of contact.", 0.9)],
        status="ok",
        confidence=0.9,
    )
    process_video_local_module.detect_scenes = lambda *_args, **_kwargs: ([SceneBoundary(0.0, 8.0)], "ok")
    process_video_local_module.sample_scene_keyframes = (
        lambda *_args, **_kwargs: ([FrameSample(4.0, str(frame_path.resolve()))], "ok")
    )
    process_video_local_module.run_ocr_on_frames = (
        lambda *_args, **_kwargs: ([OcrObservation(4.0, str(frame_path.resolve()), "FOOT CONTACT", None)], "ok")
    )

    try:
        result = process_video_local_module.process_video_local(source)
    finally:
        process_video_local_module.fetch_youtube_metadata = original_fetch
        process_video_local_module.download_youtube_video = original_download
        process_video_local_module.extract_audio_ffmpeg = original_extract
        process_video_local_module.transcribe_audio = original_transcribe
        process_video_local_module.detect_scenes = original_detect
        process_video_local_module.sample_scene_keyframes = original_sample
        process_video_local_module.run_ocr_on_frames = original_ocr
        shutil.rmtree(test_dir, ignore_errors=True)

    assert result["status"] == "processed_local_level1"
    assert result["analysis_report"]["metadata_status"] == "ok"
    assert result["analysis_report"]["download_status"] == "ok"
    assert result["source"].title == "Foot Drill"
    assert result["source"].channel_or_author == "Conor"
    assert any(asset.metadata.get("origin") == "youtube_download" for asset in result["assets"])
    assert "foot contact" in result["segments"][0].retrieval_text.lower()
