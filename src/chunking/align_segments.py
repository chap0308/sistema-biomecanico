"""Align transcript, OCR, and frames into retrieval-ready segments."""

from __future__ import annotations

from collections import Counter
from dataclasses import dataclass

from src.analysis.frame_sampler import FrameSample
from src.analysis.ocr import OcrObservation
from src.analysis.scene_detect import SceneBoundary
from src.analysis.whisper_asr import TranscriptSegment
from src.chunking.segment_builder import build_segment
from src.core.models import FrameRef, Segment, Source

STOPWORDS = {
    "the",
    "and",
    "for",
    "that",
    "with",
    "this",
    "from",
    "your",
    "para",
    "porque",
    "como",
    "esto",
    "esta",
    "these",
    "those",
    "pero",
    "sobre",
    "into",
    "cuando",
    "where",
    "have",
    "what",
    "about",
    "que",
    "por",
    "los",
    "las",
    "una",
    "uno",
    "del",
    "con",
    "sin",
}


@dataclass(slots=True)
class AlignmentReport:
    """Small status bundle describing how segments were built."""

    status: str
    scene_count: int
    transcript_segment_count: int
    ocr_observation_count: int


def align_signals_to_segments(
    *,
    source: Source,
    scenes: list[SceneBoundary],
    transcript_segments: list[TranscriptSegment],
    ocr_observations: list[OcrObservation],
    frame_samples: list[FrameSample],
    max_segment_sec: float = 15.0,
) -> tuple[list[Segment], AlignmentReport]:
    """Build retrieval-ready segments by aligning local signals to scene windows."""
    normalized_windows = _expand_windows(scenes, max_segment_sec=max_segment_sec)
    segments: list[Segment] = []
    for index, window in enumerate(normalized_windows, start=1):
        overlapping_transcript = [
            item for item in transcript_segments if item.end_sec > window.start_sec and item.start_sec < window.end_sec
        ]
        overlapping_ocr = [item for item in ocr_observations if window.start_sec <= item.sec <= window.end_sec]
        overlapping_frames = [item for item in frame_samples if window.start_sec <= item.sec <= window.end_sec]

        transcript_text = " ".join(item.text.strip() for item in overlapping_transcript if item.text.strip())
        ocr_text = " ".join(item.text.strip() for item in overlapping_ocr if item.text.strip())
        topics, keywords = _derive_topics_and_keywords(source, transcript_text, ocr_text)
        summary = _build_summary(source, transcript_text, ocr_text, window)
        visual_description = _build_visual_description(overlapping_ocr, overlapping_frames)
        confidence_asr = _average([item.confidence for item in overlapping_transcript])

        segment = build_segment(
            source_id=source.source_id or "",
            segment_index=index,
            start_sec=window.start_sec,
            end_sec=window.end_sec,
            transcript=transcript_text,
            ocr_text=ocr_text,
            visual_description=visual_description,
            segment_summary=summary,
            topics=topics,
            keywords=keywords,
            payload={
                "source_type": source.source_type,
                "course_id": source.course_id,
                "title": source.title or "",
                "uri": source.canonical_uri or source.uri,
                "channel_or_author": source.channel_or_author or "",
            },
        )
        segment.language = source.language_hint
        segment.confidence.asr = confidence_asr
        segment.confidence.ocr = 1.0 if overlapping_ocr else None
        segment.frame_refs = [FrameRef(sec=item.sec, path=item.path) for item in overlapping_frames]
        if not segment.transcript and source.title:
            segment.transcript = source.title
            segment.retrieval_text = build_segment(
                source_id=segment.source_id,
                segment_index=segment.segment_index,
                start_sec=segment.start_sec,
                end_sec=segment.end_sec,
                transcript=segment.transcript,
                ocr_text=segment.ocr_text,
                visual_description=segment.visual_description,
                segment_summary=segment.segment_summary,
                topics=segment.topics,
                keywords=segment.keywords,
                payload=segment.payload,
            ).retrieval_text
        segments.append(segment)

    if not segments:
        fallback = build_segment(
            source_id=source.source_id or "",
            segment_index=1,
            start_sec=0.0,
            end_sec=source.duration_sec or 10.0,
            transcript=source.title or "",
            segment_summary=f"Fallback segment for {source.title or source.uri}",
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
        fallback.language = source.language_hint
        segments = [fallback]

    return segments, AlignmentReport(
        status="ok",
        scene_count=len(normalized_windows),
        transcript_segment_count=len(transcript_segments),
        ocr_observation_count=len(ocr_observations),
    )


def _expand_windows(scenes: list[SceneBoundary], *, max_segment_sec: float) -> list[SceneBoundary]:
    windows: list[SceneBoundary] = []
    for scene in scenes:
        start_sec = float(scene.start_sec)
        end_sec = float(scene.end_sec)
        if end_sec <= start_sec:
            continue
        current = start_sec
        while current < end_sec:
            next_end = min(end_sec, current + max_segment_sec)
            windows.append(SceneBoundary(start_sec=current, end_sec=next_end))
            current = next_end
    return windows


def _derive_topics_and_keywords(source: Source, transcript_text: str, ocr_text: str) -> tuple[list[str], list[str]]:
    corpus = f"{transcript_text} {ocr_text}".lower()
    tokens = [
        token.strip(".,:;!?()[]{}\"'`")
        for token in corpus.split()
        if len(token.strip(".,:;!?()[]{}\"'`")) >= 4
    ]
    filtered = [token for token in tokens if token and token not in STOPWORDS]
    most_common = [token for token, _ in Counter(filtered).most_common(6)]
    topics = list(dict.fromkeys([*source.tags, *most_common[:4]]))
    keywords = list(dict.fromkeys([*source.tags, *most_common]))
    return topics, keywords


def _build_summary(source: Source, transcript_text: str, ocr_text: str, window: SceneBoundary) -> str:
    if transcript_text:
        trimmed = transcript_text[:180].strip()
        return f"Segment {window.start_sec:.1f}-{window.end_sec:.1f}s: {trimmed}"
    if ocr_text:
        trimmed = ocr_text[:180].strip()
        return f"Segment {window.start_sec:.1f}-{window.end_sec:.1f}s with OCR: {trimmed}"
    return f"Segment {window.start_sec:.1f}-{window.end_sec:.1f}s for {source.title or source.uri}"


def _build_visual_description(ocr_observations: list[OcrObservation], frame_samples: list[FrameSample]) -> str:
    if ocr_observations:
        return f"Representative frame contains OCR text: {' | '.join(item.text for item in ocr_observations[:2])}"
    if frame_samples:
        return f"Representative frame sampled at {frame_samples[0].sec:.1f}s."
    return ""


def _average(values: list[float | None]) -> float | None:
    filtered = [value for value in values if value is not None]
    if not filtered:
        return None
    return sum(filtered) / len(filtered)
