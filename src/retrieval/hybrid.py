"""Hybrid retrieval across evidence and derived knowledge collections."""

from __future__ import annotations

from dataclasses import dataclass
import re
import unicodedata

from src.core.settings import get_rag_settings
from src.indexing.qdrant_store import QdrantSearchResult, QdrantStore
from src.storage.supabase_store import SupabaseRagStore


@dataclass(slots=True)
class RetrievalBundle:
    quality: str
    knowledge_results: list[QdrantSearchResult]
    evidence_results: list[QdrantSearchResult]
    evidence_rows: list[dict[str, object]]


def retrieve_for_query(query: str, *, quality: str, supabase_store: SupabaseRagStore) -> RetrievalBundle:
    """Retrieve context from Qdrant according to the configured answer quality."""
    settings = get_rag_settings()
    quality = quality.lower()
    if quality not in {"low", "medium", "high"}:
        raise ValueError("quality must be one of: low, medium, high")

    knowledge_store = _build_qdrant_store(settings.qdrant_knowledge_collection)
    evidence_store = _build_qdrant_store(settings.qdrant_collection)

    knowledge_limit = 4 if quality in {"low", "medium"} else 5
    evidence_limit = 0 if quality == "low" else 2 if quality == "medium" else 4
    knowledge_pool = max(knowledge_limit * 4, 12)
    evidence_pool = max(evidence_limit * 4, 12) if evidence_limit else 0

    query_regions = _infer_query_regions(query)
    raw_knowledge_results = knowledge_store.query(query, limit=knowledge_pool)
    raw_evidence_results = evidence_store.query(query, limit=evidence_pool) if evidence_limit else []

    raw_knowledge_results = _filter_results_by_region_family(
        raw_knowledge_results,
        query_regions,
        minimum_keep=min(knowledge_limit + 1, 4),
    )
    raw_knowledge_results = _filter_results_by_focus_signal(
        raw_knowledge_results,
        query_regions,
        minimum_keep=min(knowledge_limit, 3),
    )
    if evidence_limit:
        raw_evidence_results = _filter_results_by_region_family(
            raw_evidence_results,
            query_regions,
            minimum_keep=min(evidence_limit, 2),
        )
        raw_evidence_results = _filter_results_by_focus_signal(
            raw_evidence_results,
            query_regions,
            minimum_keep=1,
        )

    knowledge_results = _rerank_and_diversify_results(
        query,
        raw_knowledge_results,
        limit=knowledge_limit,
        max_per_source=2,
    )
    evidence_results = (
        _rerank_and_diversify_results(
            query,
            raw_evidence_results,
            limit=evidence_limit,
            max_per_source=1,
        )
        if evidence_limit
        else []
    )
    evidence_rows = supabase_store.fetch_segments_by_ids([str(item.payload.get("segment_id", "")) for item in evidence_results])

    return RetrievalBundle(
        quality=quality,
        knowledge_results=knowledge_results,
        evidence_results=evidence_results,
        evidence_rows=evidence_rows,
    )


def _build_qdrant_store(collection_name: str) -> QdrantStore:
    settings = get_rag_settings()
    kwargs = {"collection_name": collection_name}
    if settings.qdrant_prefer_embedded:
        kwargs["path"] = settings.qdrant_path
    else:
        kwargs["url"] = settings.qdrant_url
        kwargs["api_key"] = settings.qdrant_api_key
    return QdrantStore(**kwargs)


def _rerank_and_diversify_results(
    query: str,
    results: list[QdrantSearchResult],
    *,
    limit: int,
    max_per_source: int,
) -> list[QdrantSearchResult]:
    """Boost body-region alignment and avoid over-concentrating all context in one source."""
    if not results or limit <= 0:
        return []

    query_terms = _tokenize_query(query)
    query_regions = _infer_query_regions(query)
    query_region_family = _expand_region_family(query_regions)
    strong_focus_regions = _expand_strong_focus_regions(query_regions)
    strong_focus_phrase = _has_strong_shoulder_scapula_phrase(query)
    strong_pelvis_phrase = _has_strong_pelvis_phrase(query)
    strong_foot_phrase = _has_strong_foot_phrase(query)
    strong_jaw_phrase = _has_strong_jaw_phrase(query)

    scored: list[tuple[float, QdrantSearchResult]] = []
    for result in results:
        payload = dict(result.payload)
        score = result.score

        body_regions = [str(item).strip().lower() for item in payload.get("body_regions", [])]
        primary_body_region = str(payload.get("primary_body_region", "")).strip().lower()
        title = str(payload.get("knowledge_unit_title", "")).strip()
        if not title:
            title = str(payload.get("title", "")).strip()
        summary = str(payload.get("knowledge_unit_summary", "")).strip()
        segment_summary = str(payload.get("segment_summary", "")).strip()
        topics = " ".join(str(item) for item in payload.get("topics", []))
        keywords = " ".join(str(item) for item in payload.get("keywords", []))
        problem_layers = " ".join(str(item) for item in payload.get("problem_layers", []))

        haystack = " ".join(
            [
                title,
                summary,
                segment_summary,
                primary_body_region,
                " ".join(body_regions),
                problem_layers,
                topics,
                keywords,
            ]
        )
        haystack_normalized = _normalize_text(haystack)
        title_summary_text = _normalize_text(f"{title} {summary}")

        overlap = sum(1 for term in query_terms if term and term in haystack_normalized)
        if overlap:
            score += min(0.07 * overlap, 0.35)

        if query_regions:
            region_matches = sum(1 for region in query_regions if region in body_regions)
            if region_matches:
                score += min(0.18 * region_matches, 0.36)
            elif body_regions:
                score -= 0.16

            if primary_body_region and primary_body_region in query_regions:
                score += 0.28
            elif primary_body_region and primary_body_region in strong_focus_regions:
                score += 0.18
            elif primary_body_region and primary_body_region in query_region_family:
                score += 0.06
            elif primary_body_region:
                score -= 0.10

            if _text_mentions_region_family(title_summary_text, query_region_family):
                score += 0.14

            broad_region_count = len(body_regions)
            if broad_region_count >= 5 and not _text_mentions_region_family(title_summary_text, query_region_family):
                score -= 0.20
            elif broad_region_count >= 4 and primary_body_region not in query_region_family:
                score -= 0.10

            if _is_generic_knowledge_title(title) and not _text_mentions_region_family(title_summary_text, query_region_family):
                score -= 0.24

        if strong_focus_phrase:
            if primary_body_region in {"shoulder", "scapula"}:
                score += 0.30
            elif primary_body_region in {"rib_cage", "thoracic_spine", "upper_back"}:
                score += 0.12
            elif primary_body_region in {"pelvis", "foot", "ankle", "jaw"}:
                score -= 0.28

            if any(alias in title_summary_text for alias in ("omoplato", "escapula", "scapula", "hombro", "shoulder", "pectoral", "pecho", "chest")):
                score += 0.14

        if strong_pelvis_phrase:
            if primary_body_region in {"pelvis", "core"}:
                score += 0.26
            elif primary_body_region in {"rib_cage", "thoracic_spine"}:
                score += 0.08
            elif primary_body_region in {"shoulder", "scapula", "foot", "ankle", "jaw"}:
                score -= 0.24

            if any(
                alias in title_summary_text
                for alias in (
                    "pelvis",
                    "pelvic",
                    "cadera",
                    "hip",
                    "swayback",
                    "anterior pelvic tilt",
                    "anteversion pelvica",
                    "inclinacion pelvica anterior",
                    "flexor",
                    "psoas",
                )
            ):
                score += 0.12

        if strong_foot_phrase:
            if primary_body_region in {"foot", "ankle", "lower_leg"}:
                score += 0.28
            elif primary_body_region in {"pelvis", "shoulder", "scapula", "jaw"}:
                score -= 0.26

            if any(
                alias in title_summary_text
                for alias in (
                    "foot",
                    "pie",
                    "plantar",
                    "arch",
                    "arco",
                    "pronation",
                    "pronacion",
                    "dorsiflex",
                    "ankle",
                    "tobillo",
                    "flat feet",
                    "flat foot",
                    "pes planus",
                    "medial collapse",
                    "colapso medial",
                )
            ):
                score += 0.16
            elif primary_body_region == "foot":
                score -= 0.24

        if strong_jaw_phrase:
            if primary_body_region in {"jaw", "neck"}:
                score += 0.30
            elif primary_body_region in {"upper_back", "shoulder"}:
                score += 0.08
            elif primary_body_region in {"pelvis", "foot", "ankle"}:
                score -= 0.24

            if any(
                alias in title_summary_text
                for alias in (
                    "jaw",
                    "tmj",
                    "mandibula",
                    "mandible",
                    "mordida",
                    "bite",
                    "mastic",
                    "quijada",
                    "cuello",
                    "neck",
                    "scm",
                    "temporomandibular",
                )
            ):
                score += 0.18
            elif primary_body_region == "jaw":
                score -= 0.18

        knowledge_unit_type = str(payload.get("knowledge_unit_type", "")).strip().lower()
        if knowledge_unit_type == "corrective_exercise":
            score += 0.05
        elif knowledge_unit_type == "educational_point" and (
            strong_focus_phrase or strong_pelvis_phrase or strong_foot_phrase or strong_jaw_phrase
        ):
            score -= 0.04

        scored.append((score, result))

    scored.sort(key=lambda item: item[0], reverse=True)
    selected: list[QdrantSearchResult] = []
    per_source: dict[str, int] = {}
    for boosted_score, result in scored:
        payload = dict(result.payload)
        source_key = str(payload.get("source_id") or payload.get("source_uri") or result.point_id)
        if per_source.get(source_key, 0) >= max_per_source:
            continue
        selected.append(QdrantSearchResult(point_id=result.point_id, score=boosted_score, payload=result.payload))
        per_source[source_key] = per_source.get(source_key, 0) + 1
        if len(selected) >= limit:
            break

    return selected


def _tokenize_query(query: str) -> list[str]:
    normalized = _normalize_text(query)
    base_tokens = [token for token in re.findall(r"[a-z_]{3,}", normalized) if token]
    expanded = list(base_tokens)
    expanded.extend(_infer_query_regions(query))
    expanded.extend(_expand_query_domain_terms(query))
    return list(dict.fromkeys(expanded))


def _infer_query_regions(query: str) -> list[str]:
    text = _normalize_text(query)
    matches: list[str] = []
    region_map = {
        "scapula": ["omoplato", "escapula", "scapula", "scapular", "winging", "shoulder blade"],
        "shoulder": ["hombro", "shoulder", "deltoid", "deltoides", "rotator cuff", "manguito rotador", "overhead", "brazo derecho", "brazo izquierdo"],
        "neck": ["cuello", "neck", "cervical", "scm", "esternocleidomastoideo", "trapecio", "trapecios"],
        "upper_back": ["espalda alta", "upper back", "trapecio", "trapecios"],
        "thoracic_spine": ["toracica", "thoracic", "dorsal"],
        "pelvis": [
            "pelvis",
            "pelvica",
            "anteversion pelvica",
            "retroversion pelvica",
            "inclinacion pelvica anterior",
            "inclinacion pelvica posterior",
            "cadera",
            "hip",
            "swayback",
            "anterior pelvic tilt",
            "posterior pelvic tilt",
            "apt",
            "butt wink",
            "lordosis",
            "hip flexor",
            "piriformis",
            "ql",
            "quadratus lumborum",
            "flexores de cadera",
            "flexor de cadera",
            "psoas",
        ],
        "rib_cage": ["costillas", "rib", "ribcage", "caja toracica", "pecho", "pectoral", "chest", "sternum", "esternon"],
        "foot": [
            "foot",
            "arco",
            "arch",
            "planta del pie",
            "flat foot",
            "flat feet",
            "pes planus",
            "pronation",
            "pronacion",
            "medial arch",
            "medial collapse",
            "colapso medial",
        ],
        "ankle": ["tobillo", "ankle", "dorsiflexion", "supination", "supinacion"],
        "jaw": ["mandibula", "mandibular", "jaw", "tmj", "bite", "mordida", "temporomandibular", "masticar", "quijada", "bruxismo"],
    }
    for region, aliases in region_map.items():
        if any(_contains_alias(text, alias) for alias in aliases):
            matches.append(region)

    if (
        _contains_alias(text, "pie")
        and not _contains_alias(text, "de pie")
        and not _contains_alias(text, "estar de pie")
    ):
        matches.append("foot")

    if any(
        phrase in text
        for phrase in (
            "tocar mi omoplato contrario",
            "tocar el omoplato contrario",
            "alcanzar el omoplato contrario",
            "mano detras de la espalda",
            "brazo detras de la espalda",
        )
    ):
        matches.extend(["shoulder", "scapula", "rib_cage"])
    if "pecho" in text and ("brazo" in text or "hombro" in text or "omoplato" in text):
        matches.extend(["rib_cage", "shoulder", "scapula"])

    return list(dict.fromkeys(matches))


def _expand_query_domain_terms(query: str) -> list[str]:
    text = _normalize_text(query)
    expansions: list[str] = []
    concept_map = {
        "swayback": ["pelvis", "rib_cage", "posture", "stacked", "breathing"],
        "anterior pelvic tilt": ["pelvis", "hip_flexor", "rib_cage", "lordosis"],
        "inclinacion pelvica anterior": ["pelvis", "hip_flexor", "rib_cage", "lordosis"],
        "anteversion pelvica": ["pelvis", "hip_flexor", "lordosis"],
        "retroversion pelvica": ["pelvis", "glutes", "hamstrings"],
        "apt": ["pelvis", "hip_flexor", "lordosis"],
        "butt wink": ["pelvis", "hip", "squat", "mobility"],
        "flexores de cadera": ["pelvis", "hip_flexor", "psoas"],
        "psoas": ["pelvis", "hip_flexor", "rib_cage"],
        "flat foot": ["foot", "arch", "pronation"],
        "flat feet": ["foot", "arch", "pronation"],
        "pes planus": ["foot", "arch", "pronation"],
        "pronation": ["foot", "ankle", "arch"],
        "colapso medial": ["foot", "ankle", "arch"],
        "dorsiflexion": ["ankle", "foot", "mobility"],
        "dorsiflexion de tobillo": ["ankle", "foot", "mobility"],
        "dolor en la planta del pie": ["foot", "plantar", "arch"],
        "pie plano funcional": ["foot", "arch", "pronation"],
        "tmj": ["jaw", "neck", "bite"],
        "mandibula": ["jaw", "neck", "tmj"],
        "mordida": ["jaw", "neck", "bite"],
        "masticar": ["jaw", "neck", "tmj"],
        "bruxismo": ["jaw", "neck", "tmj"],
        "tmj": ["jaw", "neck", "bite"],
        "bite": ["jaw", "neck", "tmj"],
        "scapular winging": ["scapula", "shoulder", "rib_cage"],
        "escapula alada": ["scapula", "shoulder", "rib_cage"],
        "tocar mi omoplato contrario": ["shoulder", "scapula", "internal_rotation", "behind_back_reach", "rib_cage"],
        "mano detras de la espalda": ["shoulder", "scapula", "internal_rotation", "behind_back_reach"],
        "pecho": ["rib_cage", "pectoral", "thoracic_spine", "shoulder"],
    }
    for phrase, tokens in concept_map.items():
        if _contains_alias(text, phrase):
            expansions.extend(tokens)
    return expansions


def _filter_results_by_region_family(
    results: list[QdrantSearchResult],
    query_regions: list[str],
    *,
    minimum_keep: int,
) -> list[QdrantSearchResult]:
    if not results or not query_regions:
        return results
    allowed = _expand_region_family(query_regions)
    matched: list[QdrantSearchResult] = []
    for result in results:
        payload = dict(result.payload)
        body_regions = {str(item).strip().lower() for item in payload.get("body_regions", []) if str(item).strip()}
        primary_body_region = str(payload.get("primary_body_region", "")).strip().lower()
        if body_regions & allowed or primary_body_region in allowed:
            matched.append(result)
    return matched if len(matched) >= minimum_keep else results


def _expand_region_family(query_regions: list[str]) -> set[str]:
    families = {
        "shoulder": {"shoulder", "scapula", "upper_back", "thoracic_spine", "rib_cage", "neck"},
        "scapula": {"scapula", "shoulder", "upper_back", "thoracic_spine", "rib_cage", "neck"},
        "upper_back": {"upper_back", "scapula", "shoulder", "thoracic_spine", "rib_cage", "neck"},
        "thoracic_spine": {"thoracic_spine", "upper_back", "rib_cage", "scapula", "shoulder"},
        "neck": {"neck", "shoulder", "scapula", "upper_back", "jaw"},
        "pelvis": {"pelvis", "core", "rib_cage", "thoracic_spine"},
        "rib_cage": {"rib_cage", "thoracic_spine", "upper_back", "scapula", "shoulder", "core", "pelvis"},
        "core": {"core", "rib_cage", "pelvis"},
        "foot": {"foot", "ankle", "lower_leg"},
        "ankle": {"ankle", "foot", "lower_leg"},
        "lower_leg": {"lower_leg", "ankle", "foot"},
        "jaw": {"jaw", "neck", "upper_back", "shoulder"},
    }
    expanded: set[str] = set()
    for region in query_regions:
        expanded.update(families.get(region, {region}))
    return expanded


def _expand_strong_focus_regions(query_regions: list[str]) -> set[str]:
    strong_families = {
        "shoulder": {"shoulder", "scapula", "upper_back", "thoracic_spine"},
        "scapula": {"scapula", "shoulder", "upper_back", "thoracic_spine"},
        "upper_back": {"upper_back", "scapula", "shoulder", "thoracic_spine"},
        "thoracic_spine": {"thoracic_spine", "upper_back", "scapula", "shoulder"},
        "neck": {"neck", "jaw", "shoulder", "upper_back"},
        "pelvis": {"pelvis", "core", "rib_cage", "thoracic_spine"},
        "rib_cage": {"rib_cage", "thoracic_spine", "upper_back", "scapula", "shoulder"},
        "core": {"core", "pelvis", "rib_cage"},
        "foot": {"foot", "ankle", "lower_leg"},
        "ankle": {"ankle", "foot", "lower_leg"},
        "lower_leg": {"lower_leg", "ankle", "foot"},
        "jaw": {"jaw", "neck", "upper_back"},
    }
    expanded: set[str] = set()
    for region in query_regions:
        expanded.update(strong_families.get(region, {region}))
    return expanded


def _filter_results_by_focus_signal(
    results: list[QdrantSearchResult],
    query_regions: list[str],
    *,
    minimum_keep: int,
) -> list[QdrantSearchResult]:
    if not results or not query_regions:
        return results
    region_family = _expand_region_family(query_regions)
    strong_focus_regions = _expand_strong_focus_regions(query_regions)
    focused: list[QdrantSearchResult] = []
    for result in results:
        payload = dict(result.payload)
        primary_body_region = str(payload.get("primary_body_region", "")).strip().lower()
        title_summary_text = _normalize_text(
            " ".join(
                [
                    str(payload.get("knowledge_unit_title", "")),
                    str(payload.get("knowledge_unit_summary", "")),
                    str(payload.get("segment_summary", "")),
                ]
            )
        )
        if primary_body_region in strong_focus_regions or _text_mentions_region_family(title_summary_text, region_family):
            focused.append(result)
    return focused if len(focused) >= minimum_keep else results


def _text_mentions_region_family(text: str, region_family: set[str]) -> bool:
    if not text or not region_family:
        return False
    for region in region_family:
        aliases = _region_aliases(region)
        if any(_contains_alias(text, alias) for alias in aliases):
            return True
    return False


def _region_aliases(region: str) -> list[str]:
    alias_map = {
        "scapula": ["scapula", "scapular", "escapula", "omoplato", "shoulder blade"],
        "shoulder": ["shoulder", "hombro", "deltoid", "deltoides", "brazo"],
        "neck": ["neck", "cuello", "cervical", "scm", "esternocleidomastoideo", "trapecio", "trapecios"],
        "upper_back": ["upper back", "espalda alta", "trapecio", "trapecios", "rhomboid", "romboide"],
        "thoracic_spine": ["thoracic", "toracica", "dorsal", "thorax", "torax"],
        "rib_cage": ["rib cage", "ribcage", "ribs", "costillas", "caja toracica", "pecho", "pectoral", "chest", "sternum", "esternon"],
        "core": ["core", "abdomen", "abdominal", "oblique", "obliques"],
        "pelvis": [
            "pelvis",
            "pelvic",
            "pelvica",
            "hip",
            "hips",
            "cadera",
            "caderas",
            "anteversion pelvica",
            "retroversion pelvica",
            "inclinacion pelvica anterior",
            "inclinacion pelvica posterior",
            "swayback",
            "psoas",
            "flexor de cadera",
            "flexores de cadera",
        ],
        "foot": ["foot", "pie", "feet", "plantar", "arch", "arco"],
        "ankle": ["ankle", "tobillo", "ankles"],
        "lower_leg": ["lower leg", "shin", "calf", "pantorrilla", "tibia"],
        "jaw": ["jaw", "mandibula", "mandibular", "tmj", "mordida", "masticar", "quijada", "bruxismo", "temporomandibular"],
    }
    return alias_map.get(region, [region])


def _is_generic_knowledge_title(title: str) -> bool:
    cleaned = title.strip().lower()
    generic_prefixes = (
        "corrective exercise:",
        "compensation pattern:",
        "educational point:",
        "test:",
        "advice:",
        "visual cue:",
    )
    return cleaned.startswith(generic_prefixes)


def _has_strong_shoulder_scapula_phrase(query: str) -> bool:
    text = _normalize_text(query)
    phrases = (
        "tocar mi omoplato contrario",
        "tocar el omoplato contrario",
        "mano detras de la espalda",
        "brazo detras de la espalda",
        "me duele el pecho",
    )
    return any(phrase in text for phrase in phrases)


def _has_strong_pelvis_phrase(query: str) -> bool:
    text = _normalize_text(query)
    phrases = (
        "swayback",
        "anteversion pelvica",
        "retroversion pelvica",
        "inclinacion pelvica anterior",
        "inclinacion pelvica posterior",
        "pelvis adelantada",
        "flexores de cadera",
        "flexor de cadera",
        "psoas",
    )
    return any(phrase in text for phrase in phrases)


def _has_strong_foot_phrase(query: str) -> bool:
    text = _normalize_text(query)
    phrases = (
        "pie plano funcional",
        "colapso medial",
        "pronacion",
        "arco",
        "planta del pie",
        "dorsiflexion de tobillo",
        "rigidez en el pie",
        "dolor en la planta del pie",
    )
    return any(phrase in text for phrase in phrases)


def _has_strong_jaw_phrase(query: str) -> bool:
    text = _normalize_text(query)
    phrases = (
        "tmj",
        "mandibula",
        "mordida",
        "masticar",
        "quijada",
        "bruxismo",
        "temporomandibular",
        "me truena la mandibula",
        "dolor en la mandibula",
    )
    return any(phrase in text for phrase in phrases)


def _normalize_text(text: str) -> str:
    normalized = unicodedata.normalize("NFKD", text.lower())
    return "".join(char for char in normalized if not unicodedata.combining(char))


def _contains_alias(text: str, alias: str) -> bool:
    pattern = r"\b" + re.escape(alias).replace(r"\ ", r"\s+") + r"\b"
    return re.search(pattern, text) is not None
