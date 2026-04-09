"""Project second-layer knowledge drafts into persistence and retrieval records."""

from __future__ import annotations

import json
import re
from dataclasses import dataclass
from typing import Any

from src.chunking.segment_builder import build_segment
from src.core.ids import stable_id
from src.core.knowledge_models import KnowledgeDraft
from src.core.models import Segment, Source

BODY_REGION_ALIASES: dict[str, list[str]] = {
    "scapula": ["scapula", "scapular", "escapula", "escápula", "omoplato", "omóplato"],
    "shoulder": ["shoulder", "hombro", "deltoid", "deltoides"],
    "neck": ["neck", "cuello", "cervical", "jaw-neck"],
    "upper_back": ["upper back", "espalda alta", "trap", "trapecio", "trapecios", "rhomboid", "romboide"],
    "thoracic_spine": ["thoracic", "toracica", "torácica", "dorsal", "thorax", "torax", "tórax"],
    "rib_cage": ["rib cage", "ribcage", "ribs", "costillas", "caja toracica", "caja torácica"],
    "core": ["core", "abdominal", "oblique", "obliques", "abdomen", "abdominales"],
    "pelvis": ["pelvis", "pelvic", "pelvica", "pélvica", "hip", "hips", "cadera", "caderas"],
    "foot": ["foot", "pie", "feet", "plantar", "arch", "arco", "big toe", "dedo gordo"],
    "ankle": ["ankle", "tobillo", "ankles", "talocrural"],
    "jaw": ["jaw", "tmj", "mandibula", "mandíbula"],
    "lower_leg": ["lower leg", "shin", "calf", "pantorrilla", "tibia"],
}

PRIMARY_REGION_PRIORITY: list[str] = [
    "scapula",
    "shoulder",
    "neck",
    "upper_back",
    "thoracic_spine",
    "rib_cage",
    "pelvis",
    "core",
    "ankle",
    "foot",
    "lower_leg",
    "jaw",
]


@dataclass(slots=True)
class KnowledgeProjection:
    """Persistence-ready knowledge draft plus retrieval-ready derived segments."""

    draft: KnowledgeDraft
    source: Source
    derived_segments: list[Segment]
    content_sha256: str


def project_knowledge_draft(source: Source, draft_payload: dict[str, Any]) -> KnowledgeProjection:
    """Normalize a knowledge draft and derive retrieval-ready segments from knowledge units."""
    draft = _normalize_draft(source, KnowledgeDraft.model_validate(draft_payload))
    usefulness = (draft.classification.usefulness or "").strip().lower()
    if usefulness == "not_useful":
        derived_segments = []
    else:
        derived_segments = [
            _knowledge_unit_to_segment(source, draft, unit_payload, index)
            for index, unit_payload in enumerate(draft.knowledge_units, start=1)
        ]
    return KnowledgeProjection(
        draft=draft,
        source=source,
        derived_segments=derived_segments,
        content_sha256=_compute_draft_sha(draft),
    )


def _knowledge_unit_to_segment(
    source: Source,
    draft: KnowledgeDraft,
    unit_payload: Any,
    index: int,
) -> Segment:
    unit = unit_payload.model_dump(mode="json")
    start_sec, end_sec = _extract_time_bounds(unit.get("timestamps", []), fallback_index=index)

    text_parts = [
        unit.get("title", ""),
        unit.get("summary", ""),
        " ".join(unit.get("mechanisms", [])),
        " ".join(unit.get("execution_steps", [])),
        " ".join(unit.get("cues", [])),
        " ".join(unit.get("breathing_cues", [])),
        " ".join(unit.get("errors_to_avoid", [])),
        " ".join(unit.get("advice", [])),
        " ".join(unit.get("retest", [])),
    ]
    transcript = " ".join(part.strip() for part in text_parts if part and str(part).strip())
    unit_regions = _infer_unit_body_regions(unit, draft)
    unit_problem_layers = _infer_unit_problem_layers(unit, draft)
    primary_body_region = _infer_primary_body_region(unit, unit_regions)

    topics = _dedupe(
        [
            *unit_regions,
            primary_body_region or "",
            *unit_problem_layers,
            unit.get("unit_type", ""),
            *draft.searchable_topics,
        ]
    )[:12]
    keywords = _dedupe(
        [
            *draft.searchable_tags,
            *[str(item).lower() for item in unit.get("observable_signs", [])],
        ]
    )[:16]
    payload = {
        "source_type": source.source_type,
        "source_uri": source.uri,
        "category": "knowledge_unit",
        "analysis_origin": draft.analysis_origin,
        "content_kind": draft.classification.content_kind,
        "knowledge_unit_type": unit.get("unit_type", "educational_point"),
        "knowledge_unit_title": unit.get("title", ""),
        "knowledge_unit_summary": unit.get("summary", ""),
        "execution_steps": unit.get("execution_steps", []),
        "cues": unit.get("cues", []),
        "breathing_cues": unit.get("breathing_cues", []),
        "errors_to_avoid": unit.get("errors_to_avoid", []),
        "when_useful": unit.get("when_useful", []),
        "when_not_useful": unit.get("when_not_useful", []),
        "retest": unit.get("retest", []),
        "advice": unit.get("advice", []),
        "primary_summary": draft.primary_summary,
        "body_regions": unit_regions,
        "primary_body_region": primary_body_region,
        "problem_layers": unit_problem_layers,
        "timestamps_raw": unit.get("timestamps", []),
    }
    segment = build_segment(
        source_id=source.source_id or "",
        segment_index=1000 + index,
        start_sec=start_sec,
        end_sec=end_sec,
        transcript=transcript,
        ocr_text="",
        visual_description=" | ".join(draft.key_visual_points[:4]),
        segment_summary=unit.get("summary", "") or unit.get("title", ""),
        topics=topics,
        keywords=keywords,
        payload=payload,
    )
    segment.segment_id = stable_id(
        "kseg",
        f"{source.source_id}:{unit.get('unit_type','educational_point')}:{unit.get('title','')}:{index}",
    )
    segment.retrieval_text = " | ".join(
        part
        for part in [
            draft.primary_summary.strip(),
            segment.transcript.strip(),
            segment.visual_description.strip(),
            " ".join(topics),
            " ".join(keywords),
        ]
        if part
    )
    return segment


def _extract_time_bounds(timestamps: list[str], *, fallback_index: int) -> tuple[float, float]:
    found: list[float] = []
    for item in timestamps:
        for token in re.findall(r"\d{1,2}:\d{2}(?::\d{2})?", item.replace("‑", "-")):
            found.append(_parse_timestamp(token))
    if len(found) >= 2:
        return min(found), max(found)
    if len(found) == 1:
        return found[0], found[0] + 15.0
    base = float((fallback_index - 1) * 15)
    return base, base + 15.0


def _parse_timestamp(value: str) -> float:
    parts = [int(part) for part in value.split(":")]
    if len(parts) == 2:
        minutes, seconds = parts
        return float(minutes * 60 + seconds)
    if len(parts) == 3:
        hours, minutes, seconds = parts
        return float(hours * 3600 + minutes * 60 + seconds)
    return 0.0


def _dedupe(values: list[str]) -> list[str]:
    ordered: list[str] = []
    seen: set[str] = set()
    for value in values:
        cleaned = str(value or "").strip()
        if not cleaned:
            continue
        key = cleaned.lower()
        if key in seen:
            continue
        seen.add(key)
        ordered.append(cleaned)
    return ordered


def _compute_draft_sha(draft: KnowledgeDraft) -> str:
    import hashlib

    canonical = json.dumps(draft.model_dump(mode="json"), ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def _normalize_draft(source: Source, draft: KnowledgeDraft) -> KnowledgeDraft:
    draft.knowledge_units = _prune_knowledge_units(source, draft)
    draft.classification.body_regions = _normalize_body_regions(draft.classification.body_regions)
    draft.searchable_topics = _dedupe(draft.searchable_topics)[:16]
    draft.searchable_tags = _dedupe(draft.searchable_tags)[:20]
    draft.problem_statements = _dedupe(draft.problem_statements)[:16]
    draft.habits_or_contexts = _dedupe(draft.habits_or_contexts)[:16]
    draft.key_visual_points = _dedupe(draft.key_visual_points)[:16]
    draft.tests_mentioned = _dedupe(draft.tests_mentioned)[:12]
    draft.exercises_mentioned = _dedupe(draft.exercises_mentioned)[:16]
    draft.advice_mentioned = _dedupe(draft.advice_mentioned)[:16]
    draft.warnings_or_limitations = _dedupe(draft.warnings_or_limitations)[:16]
    return draft


def _infer_unit_body_regions(unit: dict[str, Any], draft: KnowledgeDraft) -> list[str]:
    text = " ".join(
        [
            str(unit.get("title", "")),
            str(unit.get("summary", "")),
            " ".join(str(item) for item in unit.get("mechanisms", [])),
            " ".join(str(item) for item in unit.get("execution_steps", [])),
            " ".join(str(item) for item in unit.get("cues", [])),
            " ".join(str(item) for item in unit.get("advice", [])),
            " ".join(str(item) for item in unit.get("observable_signs", [])),
        ]
    ).lower()
    inferred: list[str] = []
    for canonical, aliases in BODY_REGION_ALIASES.items():
        if any(alias in text for alias in aliases):
            inferred.append(canonical)
    if inferred:
        return _dedupe(inferred)[:6]
    return _normalize_body_regions(draft.classification.body_regions)[:6]


def _infer_primary_body_region(unit: dict[str, Any], unit_regions: list[str]) -> str:
    title_summary_text = " ".join(
        [
            str(unit.get("title", "")),
            str(unit.get("summary", "")),
        ]
    ).lower()
    for canonical in PRIMARY_REGION_PRIORITY:
        aliases = BODY_REGION_ALIASES.get(canonical, [])
        if any(alias in title_summary_text for alias in aliases):
            return canonical

    if unit_regions:
        ordered_regions = sorted(
            unit_regions,
            key=lambda region: PRIMARY_REGION_PRIORITY.index(region) if region in PRIMARY_REGION_PRIORITY else len(PRIMARY_REGION_PRIORITY),
        )
        return ordered_regions[0]
    return ""


def _infer_unit_problem_layers(unit: dict[str, Any], draft: KnowledgeDraft) -> list[str]:
    text = " ".join(
        [
            str(unit.get("title", "")),
            str(unit.get("summary", "")),
            " ".join(str(item) for item in unit.get("mechanisms", [])),
            " ".join(str(item) for item in unit.get("errors_to_avoid", [])),
            " ".join(str(item) for item in unit.get("when_useful", [])),
        ]
    ).lower()
    inferred: list[str] = []
    if any(token in text for token in ["posture", "postural", "postura"]):
        inferred.append("postural")
    if any(token in text for token in ["mobility", "movilidad", "rotation", "rotacion", "rotación"]):
        inferred.append("mobility_restriction")
    if any(token in text for token in ["coordination", "control", "motor", "compensation", "compens"]):
        inferred.append("movement_coordination")
    if any(token in text for token in ["pain", "dolor", "tight", "tightness", "tension", "muscle knot"]):
        inferred.append("pain")
    if inferred:
        return _dedupe(inferred)[:4]
    return _dedupe(draft.classification.problem_layers)[:4]


def _normalize_body_regions(values: list[str]) -> list[str]:
    normalized: list[str] = []
    for value in values:
        cleaned = str(value or "").strip().lower()
        if not cleaned:
            continue
        mapped = None
        for canonical, aliases in BODY_REGION_ALIASES.items():
            if cleaned == canonical or any(alias == cleaned for alias in aliases):
                mapped = canonical
                break
        normalized.append(mapped or cleaned.replace(" ", "_"))
    return _dedupe(normalized)


def _prune_knowledge_units(source: Source, draft: KnowledgeDraft) -> list[Any]:
    max_units = 12 if (source.duration_sec or 0) <= 180 else 24
    ordered_units: list[Any] = []
    seen: set[str] = set()
    for unit in draft.knowledge_units:
        key = "|".join(
            [
                str(unit.unit_type or "").strip().lower(),
                str(unit.title or "").strip().lower(),
                str(unit.summary or "").strip().lower(),
            ]
        )
        if not key.strip("|"):
            continue
        if key in seen:
            continue
        seen.add(key)
        unit.observable_signs = _dedupe(unit.observable_signs)[:10]
        unit.mechanisms = _dedupe(unit.mechanisms)[:10]
        unit.execution_steps = _dedupe(unit.execution_steps)[:12]
        unit.cues = _dedupe(unit.cues)[:10]
        unit.breathing_cues = _dedupe(unit.breathing_cues)[:8]
        unit.errors_to_avoid = _dedupe(unit.errors_to_avoid)[:8]
        unit.when_useful = _dedupe(unit.when_useful)[:8]
        unit.when_not_useful = _dedupe(unit.when_not_useful)[:8]
        unit.retest = _dedupe(unit.retest)[:6]
        unit.advice = _dedupe(unit.advice)[:8]
        unit.timestamps = _dedupe(unit.timestamps)[:6]
        ordered_units.append(unit)
        if len(ordered_units) >= max_units:
            break
    return ordered_units
