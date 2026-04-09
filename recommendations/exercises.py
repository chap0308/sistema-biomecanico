"""Exercise recommendation helpers backed by a local protocol knowledge base."""

from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path
from typing import Any

_KNOWLEDGE_BASE_PATH = (
    Path(__file__).resolve().parent.parent / "data" / "knowledge" / "exercise_protocols.json"
)


@lru_cache(maxsize=1)
def _load_protocols() -> list[dict[str, Any]]:
    with _KNOWLEDGE_BASE_PATH.open("r", encoding="utf-8") as handle:
        payload = json.load(handle)
    return list(payload.get("protocols", []))


def recommend_exercises(deficiencies: list[str]) -> list[dict[str, Any]]:
    """Return exercise protocols that match the supplied deficiency ids.

    This is intentionally conservative: only protocols whose target ids intersect
    with the validated deficiencies are returned.
    """
    normalized_ids = {item.strip() for item in deficiencies if item and item.strip()}
    recommendations: list[dict[str, Any]] = []

    if not normalized_ids:
        return recommendations

    for protocol in _load_protocols():
        target_ids = set(protocol.get("target_deficiency_ids", []))
        matched_ids = sorted(normalized_ids.intersection(target_ids))
        if not matched_ids:
            continue

        recommendations.append(
            {
                "protocol_id": protocol["protocol_id"],
                "name": protocol["name"],
                "summary": protocol["summary"],
                "rationale": protocol["rationale"],
                "matched_deficiency_ids": matched_ids,
                "priority": protocol.get("priority", "secondary"),
                "exercise": protocol["exercise"],
                "dosage": protocol["dosage"],
                "source_videos": protocol.get("source_videos", []),
                "evidence_type": protocol.get("evidence_type", "expert_video_protocol"),
            }
        )

    recommendations.sort(
        key=lambda item: (
            len(item["matched_deficiency_ids"]),
            item["priority"] == "primary",
            item["name"],
        ),
        reverse=True,
    )
    return recommendations
