"""Helpers for assigning provider/quality metadata to knowledge drafts."""

from __future__ import annotations


def infer_analysis_metadata(analysis_origin: str) -> tuple[str, str]:
    """Infer provider and quality tier from one analysis origin label."""
    origin = (analysis_origin or "").strip().lower()
    if "hf_error_fallback" in origin or "hf_unavailable_fallback" in origin:
        return "local_fallback", "fallback"
    if "heuristic" in origin or "local_level1" in origin:
        return "local_fallback", "fallback"
    if "gemini" in origin:
        return "gemini", "premium"
    if "gpt-oss" in origin or "hf_structured" in origin or "openai/gpt-oss" in origin:
        return "hf_structured", "standard"
    return "unknown", "standard"
