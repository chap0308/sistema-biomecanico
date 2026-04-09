"""Grounded answering over retrieved evidence and knowledge."""

from __future__ import annotations

import json
import re
from typing import Any

import requests
from pydantic import BaseModel, Field

from src.core.settings import get_rag_settings
from src.retrieval.hybrid import RetrievalBundle


class AnswerCitation(BaseModel):
    source_type: str
    title: str = ""
    source_uri: str = ""
    segment_id: str | None = None
    knowledge_unit_title: str | None = None
    timestamp_hint: str | None = None


class GroundedAnswer(BaseModel):
    answer: str
    recommended_exercises: list[str] = Field(default_factory=list)
    key_points: list[str] = Field(default_factory=list)
    cautions: list[str] = Field(default_factory=list)
    citations: list[AnswerCitation] = Field(default_factory=list)
    retrieval_quality: str
    used_collections: list[str] = Field(default_factory=list)


def answer_query(
    query: str,
    bundle: RetrievalBundle,
    *,
    backend: str | None = None,
    model_override: str | None = None,
    model_profile: str | None = None,
) -> dict[str, Any]:
    """Answer using the configured backend with graceful fallbacks."""
    settings = get_rag_settings()
    target_backend = (backend or settings.answer_backend).lower()
    resolved_model_override = _resolve_model_override(
        backend=target_backend,
        model_override=model_override,
        model_profile=model_profile,
    )

    if target_backend == "grounded":
        return _build_fallback_grounded_answer(
            query,
            bundle,
            model_name="grounded_fallback",
            error=None,
            attempted_backends=["grounded"],
        )
    if target_backend == "ollama":
        return _call_backend_with_optional_model(answer_with_ollama, query, bundle, model_override=resolved_model_override)
    if target_backend == "openai":
        return _call_backend_with_optional_model(answer_with_openai, query, bundle, model_override=resolved_model_override)
    if target_backend == "hf":
        return _call_backend_with_optional_model(answer_with_hf, query, bundle, model_override=resolved_model_override)
    if target_backend != "auto":
        raise ValueError("backend must be one of: auto, ollama, openai, hf, grounded")

    ollama_error: Exception | None = None
    try:
        ollama_result = _call_backend_with_optional_model(
            answer_with_ollama,
            query,
            bundle,
            model_override=resolved_model_override,
        )
        if ollama_result.get("answer_backend") != "grounded_fallback":
            return ollama_result
        ollama_error = RuntimeError(str(ollama_result.get("fallback_reason", "ollama fallback")))
    except Exception as exc:
        ollama_error = exc

    openai_error: Exception | None = None
    if settings.openai_api_key:
        try:
            openai_result = _call_backend_with_optional_model(
                answer_with_openai,
                query,
                bundle,
                model_override=resolved_model_override,
            )
            if openai_result.get("answer_backend") != "grounded_fallback":
                return openai_result
            openai_error = RuntimeError(str(openai_result.get("fallback_reason", "openai fallback")))
        except Exception as exc:
            openai_error = exc

    hf_error: Exception | None = None
    if settings.hf_token:
        try:
            hf_result = _call_backend_with_optional_model(
                answer_with_hf,
                query,
                bundle,
                model_override=resolved_model_override,
            )
            if hf_result.get("answer_backend") != "grounded_fallback":
                return hf_result
            hf_error = RuntimeError(str(hf_result.get("fallback_reason", "hf fallback")))
        except Exception as exc:
            hf_error = exc

    pieces = []
    if ollama_error is not None:
        pieces.append(f"Ollama failed: {ollama_error}")
    if openai_error is not None:
        pieces.append(f"OpenAI failed: {openai_error}")
    if hf_error is not None:
        pieces.append(f"HF failed: {hf_error}")
    combined_error = RuntimeError("; ".join(pieces)) if pieces else None
    return _build_fallback_grounded_answer(
        query,
        bundle,
        model_name="auto_fallback:ollama_then_openai_then_hf",
        error=combined_error,
        attempted_backends=["ollama", "openai", "hf", "grounded"],
    )


def answer_with_hf(query: str, bundle: RetrievalBundle, *, model_override: str | None = None) -> dict[str, Any]:
    """Generate a grounded answer from retrieved context using Hugging Face chat completion."""
    settings = get_rag_settings()
    target_model = model_override or settings.hf_answer_model
    prompt_context = _build_context_payload(query, bundle)
    messages = [
        {
            "role": "system",
            "content": (
                "You answer biomechanics and corrective-exercise questions using only the retrieved context. "
                "Respond in Spanish if the user's question is in Spanish. "
                "Prefer plain language when the user describes symptoms in non-technical terms. "
                "If the evidence is limited, say so clearly. "
                "Never invent diagnoses. Suggest possibilities conservatively. "
                "Keep the answer concise. "
                "Return 1-2 short paragraphs, up to 4 key points, up to 4 exercises, and short cautions only. "
                "Do not expose raw retrieval prefixes such as 'Segment 22.5-24.3s:' or similar labels. "
                "Return strict JSON matching the schema."
            ),
        },
        {
            "role": "user",
            "content": (
                "Answer the user's question using the retrieved context. "
                "Use the knowledge units first and the evidence segments as support.\n\n"
                f"{json.dumps(prompt_context, ensure_ascii=False)}"
            ),
        },
    ]
    response_format = {
        "type": "json_schema",
        "json_schema": {
            "name": "grounded_answer",
            "schema": GroundedAnswer.model_json_schema(),
            "strict": True,
        },
    }
    last_error: Exception | None = None
    for max_tokens in (900, 1600):
        try:
            raw = _call_hf_chat(
                api_key=settings.hf_token or "",
                model=target_model,
                router_url=settings.hf_router_url,
                timeout_sec=settings.hf_timeout_sec,
                messages=messages,
                response_format=response_format,
                max_tokens=max_tokens,
            )
            payload = _parse_grounded_answer(
                raw=raw,
                bundle=bundle,
                model_name=target_model,
                answer_backend="hf",
            )
            payload = _maybe_translate_hf_payload_to_spanish(
                payload=payload,
                query=query,
                api_key=settings.hf_token or "",
                model=target_model,
                router_url=settings.hf_router_url,
                timeout_sec=settings.hf_timeout_sec,
            )
            return payload
        except Exception as exc:
            last_error = exc
    return _build_fallback_grounded_answer(
        query,
        bundle,
        model_name=target_model,
        error=last_error,
        attempted_backends=["hf", "grounded"],
    )


def answer_with_ollama(query: str, bundle: RetrievalBundle, *, model_override: str | None = None) -> dict[str, Any]:
    """Generate a grounded answer from retrieved context using an Ollama-served local model."""
    settings = get_rag_settings()
    target_model = model_override or settings.ollama_answer_model
    prompt_context = _build_context_payload(query, bundle)
    messages = [
        {
            "role": "system",
            "content": (
                "You answer biomechanics and corrective-exercise questions using only the retrieved context. "
                "Respond in Spanish if the user's question is in Spanish. "
                "Prefer plain language when the user describes symptoms in non-technical terms. "
                "If the evidence is limited, say so clearly. "
                "Never invent diagnoses. Suggest possibilities conservatively. "
                "Keep the answer concise. "
                "Do not expose raw retrieval prefixes such as 'Segment 22.5-24.3s:' or similar labels. "
                "Return strict JSON matching the schema."
            ),
        },
        {
            "role": "user",
            "content": (
                "Answer the user's question using the retrieved context. "
                "Use the knowledge units first and the evidence segments as support.\n\n"
                f"{json.dumps(prompt_context, ensure_ascii=False)}"
            ),
        },
    ]
    last_error: Exception | None = None
    for schema_mode in ("schema", "json"):
        try:
            raw = _call_ollama_chat(
                base_url=settings.ollama_base_url,
                model=target_model,
                timeout_sec=settings.ollama_timeout_sec,
                messages=messages,
                schema_mode=schema_mode,
            )
            payload = _parse_grounded_answer(
                raw=raw,
                bundle=bundle,
                model_name=target_model,
                answer_backend="ollama",
            )
            return payload
        except Exception as exc:
            last_error = exc
    return _build_fallback_grounded_answer(
        query,
        bundle,
        model_name=target_model,
        error=last_error,
        attempted_backends=["ollama", "grounded"],
    )


def answer_with_openai(query: str, bundle: RetrievalBundle, *, model_override: str | None = None) -> dict[str, Any]:
    """Generate a grounded answer from retrieved context using OpenAI chat completions."""
    settings = get_rag_settings()
    api_key = settings.openai_api_key
    target_model = model_override or settings.openai_answer_model
    if not api_key:
        return _build_fallback_grounded_answer(
            query,
            bundle,
            model_name=target_model,
            error=RuntimeError("OpenAI API key is not configured."),
            attempted_backends=["openai", "grounded"],
        )

    prompt_context = _build_context_payload(query, bundle)
    messages = [
        {
            "role": "system",
            "content": (
                "You answer biomechanics and corrective-exercise questions using only the retrieved context. "
                "Respond in Spanish if the user's question is in Spanish. "
                "Prefer plain language when the user describes symptoms in non-technical terms. "
                "If the evidence is limited, say so clearly. "
                "Never invent diagnoses. Suggest possibilities conservatively. "
                "Keep the answer concise. "
                "Do not expose raw retrieval prefixes such as 'Segment 22.5-24.3s:' or similar labels. "
                "Return strict JSON matching the schema."
            ),
        },
        {
            "role": "user",
            "content": (
                "Answer the user's question using the retrieved context. "
                "Use the knowledge units first and the evidence segments as support.\n\n"
                f"{json.dumps(prompt_context, ensure_ascii=False)}"
            ),
        },
    ]
    response_format = {
        "type": "json_schema",
        "json_schema": {
            "name": "grounded_answer",
            "schema": GroundedAnswer.model_json_schema(),
            "strict": True,
        },
    }
    last_error: Exception | None = None
    for max_tokens in (700, 1100):
        try:
            raw = _call_openai_chat(
                api_key=api_key,
                model=target_model,
                base_url=settings.openai_base_url,
                timeout_sec=settings.openai_timeout_sec,
                messages=messages,
                response_format=response_format,
                max_tokens=max_tokens,
            )
            return _parse_grounded_answer(
                raw=raw,
                bundle=bundle,
                model_name=target_model,
                answer_backend="openai",
            )
        except Exception as exc:
            last_error = exc
    return _build_fallback_grounded_answer(
        query,
        bundle,
        model_name=target_model,
        error=last_error,
        attempted_backends=["openai", "grounded"],
    )


def _parse_grounded_answer(
    *,
    raw: str,
    bundle: RetrievalBundle,
    model_name: str,
    answer_backend: str,
) -> dict[str, Any]:
    try:
        parsed = GroundedAnswer.model_validate_json(raw)
    except Exception:
        payload = _load_answer_payload(raw)
        normalized = _normalize_answer_payload(payload, bundle=bundle)
        parsed = GroundedAnswer.model_validate(normalized)
    payload = parsed.model_dump(mode="json")
    if not str(payload.get("answer", "")).strip():
        fallback_from_keys = next(
            (str(item).strip() for item in payload.get("key_points", []) if str(item).strip()),
            "",
        )
        if fallback_from_keys:
            payload["answer"] = fallback_from_keys
    payload = _clean_answer_payload_texts(payload)
    payload["retrieval_quality"] = bundle.quality
    payload["used_collections"] = _used_collections(bundle)
    payload["model_used"] = model_name
    payload["answer_backend"] = answer_backend
    return payload


def _call_backend_with_optional_model(
    backend_fn: Any,
    query: str,
    bundle: RetrievalBundle,
    *,
    model_override: str | None,
) -> dict[str, Any]:
    try:
        return backend_fn(query, bundle, model_override=model_override)
    except TypeError as exc:
        if "model_override" not in str(exc):
            raise
        return backend_fn(query, bundle)


def _resolve_model_override(
    *,
    backend: str,
    model_override: str | None,
    model_profile: str | None,
) -> str | None:
    if model_override:
        return model_override
    if not model_profile:
        return None
    settings = get_rag_settings()
    profile = model_profile.strip().lower()
    if backend == "hf":
        if profile == "balanced":
            return settings.hf_answer_model_balanced
        if profile == "cheap":
            return settings.hf_answer_model_cheap
    return None


def _build_context_payload(query: str, bundle: RetrievalBundle) -> dict[str, Any]:
    knowledge_items = []
    for item in bundle.knowledge_results:
        payload = dict(item.payload)
        knowledge_items.append(
            {
                "score": item.score,
                "knowledge_unit_title": payload.get("knowledge_unit_title", ""),
                "knowledge_unit_type": payload.get("knowledge_unit_type", ""),
                "summary": payload.get("knowledge_unit_summary", ""),
                "execution_steps": payload.get("execution_steps", []),
                "cues": payload.get("cues", []),
                "errors_to_avoid": payload.get("errors_to_avoid", []),
                "when_useful": payload.get("when_useful", []),
                "when_not_useful": payload.get("when_not_useful", []),
                "retest": payload.get("retest", []),
                "advice": payload.get("advice", []),
                "body_regions": payload.get("body_regions", []),
                "problem_layers": payload.get("problem_layers", []),
                "source_uri": payload.get("source_uri", ""),
                "timestamp_hint": ", ".join(payload.get("timestamps_raw", [])),
            }
        )

    evidence_items = []
    for row in bundle.evidence_rows:
        evidence_items.append(
            {
                "segment_id": row.get("segment_id"),
                "start_sec": row.get("start_sec"),
                "end_sec": row.get("end_sec"),
                "segment_summary": row.get("segment_summary"),
                "transcript": _truncate(str(row.get("transcript", "")), 600),
                "ocr_text": _truncate(str(row.get("ocr_text", "")), 180),
                "visual_description": _truncate(str(row.get("visual_description", "")), 220),
                "topics": row.get("topics", []),
                "keywords": row.get("keywords", []),
                "payload": row.get("payload", {}),
            }
        )

    return {
        "query": query,
        "retrieval_quality": bundle.quality,
        "knowledge_collection": "video_knowledge_units_v1",
        "evidence_collection": "video_segments_v1",
        "knowledge_items": knowledge_items,
        "evidence_items": evidence_items,
    }


def _call_hf_chat(
    *,
    api_key: str,
    model: str,
    router_url: str,
    timeout_sec: int,
    messages: list[dict[str, Any]],
    response_format: dict[str, Any],
    max_tokens: int,
) -> str:
    body = {
        "model": model,
        "messages": messages,
        "response_format": response_format,
        "temperature": 0.2,
        "max_tokens": max_tokens,
    }
    response = requests.post(
        router_url,
        headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
        json=body,
        timeout=timeout_sec,
    )
    try:
        response.raise_for_status()
    except requests.HTTPError as exc:
        if _supports_json_object_fallback(exc):
            retry_body = dict(body)
            retry_body["response_format"] = {"type": "json_object"}
            response = requests.post(
                router_url,
                headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
                json=retry_body,
                timeout=timeout_sec,
            )
            response.raise_for_status()
        else:
            raise

    content = response.json()["choices"][0]["message"]["content"]
    return _strip_think_blocks(content)


def _call_openai_chat(
    *,
    api_key: str,
    model: str,
    base_url: str,
    timeout_sec: int,
    messages: list[dict[str, Any]],
    response_format: dict[str, Any],
    max_tokens: int,
) -> str:
    body = {
        "model": model,
        "messages": messages,
        "response_format": response_format,
        "temperature": 0.2,
        "max_tokens": max_tokens,
    }
    response = requests.post(
        base_url,
        headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
        json=body,
        timeout=timeout_sec,
    )
    response.raise_for_status()
    content = response.json()["choices"][0]["message"]["content"]
    return _strip_think_blocks(content)


def _call_ollama_chat(
    *,
    base_url: str,
    model: str,
    timeout_sec: int,
    messages: list[dict[str, Any]],
    schema_mode: str,
) -> str:
    format_value: object
    if schema_mode == "schema":
        format_value = GroundedAnswer.model_json_schema()
    else:
        format_value = "json"

    response = requests.post(
        f"{base_url.rstrip('/')}/api/chat",
        headers={"Content-Type": "application/json"},
        json={
            "model": model,
            "messages": messages,
            "stream": False,
            "format": format_value,
            "options": {"temperature": 0.2},
        },
        timeout=timeout_sec,
    )
    response.raise_for_status()
    payload = response.json()
    return _strip_think_blocks(payload["message"]["content"])


def _supports_json_object_fallback(exc: requests.HTTPError) -> bool:
    if exc.response is None:
        return False
    text = exc.response.text.lower()
    return exc.response.status_code == 400 and "response format `json_schema`" in text


def _strip_think_blocks(text: str) -> str:
    return re.sub(r"<think>.*?</think>\s*", "", text, flags=re.DOTALL).strip()


def _truncate(text: str, max_len: int) -> str:
    text = text.strip()
    if len(text) <= max_len:
        return text
    return text[: max_len - 1].rstrip() + "..."


def _load_answer_payload(raw: str) -> dict[str, Any]:
    payload = json.loads(raw)
    if isinstance(payload, dict) and "choices" in payload:
        try:
            content = payload["choices"][0]["message"]["content"]
            return _load_answer_payload(content)
        except Exception:
            return payload
    if not isinstance(payload, dict):
        raise ValueError("Model response did not decode to a JSON object.")
    return payload


def _normalize_answer_payload(payload: dict[str, Any], *, bundle: RetrievalBundle) -> dict[str, Any]:
    """Coerce model-specific JSON shapes into the canonical GroundedAnswer schema."""
    if _looks_like_grounded_answer(payload):
        normalized = dict(payload)
        normalized.setdefault("retrieval_quality", bundle.quality)
        normalized.setdefault("citations", _default_citations_from_bundle(bundle))
        return normalized

    answer_field = payload.get("answer")
    if isinstance(answer_field, dict):
        return _normalize_nested_answer_payload(answer_field, bundle=bundle)
    if isinstance(answer_field, str):
        return {
            "answer": answer_field.strip(),
            "recommended_exercises": _default_recommended_exercises_from_bundle(bundle),
            "key_points": _default_key_points_from_bundle(bundle),
            "cautions": _default_cautions_from_bundle(bundle),
            "citations": _default_citations_from_bundle(bundle),
            "retrieval_quality": bundle.quality,
        }
    if "assessment" in payload:
        return _normalize_assessment_payload(payload, bundle=bundle)
    if "diagnosis" in payload or "mechanism" in payload:
        return _normalize_nested_answer_payload(payload, bundle=bundle)
    raise ValueError("Unrecognized answer JSON shape from model output.")


def _looks_like_grounded_answer(payload: dict[str, Any]) -> bool:
    return isinstance(payload.get("answer"), str) and (
        "recommended_exercises" in payload
        or "key_points" in payload
        or "cautions" in payload
        or "citations" in payload
    )


def _normalize_nested_answer_payload(payload: dict[str, Any], *, bundle: RetrievalBundle) -> dict[str, Any]:
    summary = str(payload.get("summary", "")).strip()
    diagnosis = str(payload.get("diagnosis", "")).strip()
    mechanism = str(payload.get("mechanism", "")).strip()
    answer_parts = [part for part in [summary, diagnosis, mechanism] if part]
    corrective_plan = payload.get("corrective_plan", []) or []
    recommended_exercises: list[str] = []
    key_points: list[str] = []
    direct_key_points = payload.get("key_points", []) or []
    direct_exercises = payload.get("exercises", []) or []
    direct_cautions = payload.get("cautions", []) or payload.get("avoid", []) or []
    for item in corrective_plan:
        if not isinstance(item, dict):
            continue
        exercise = str(item.get("exercise", "")).strip()
        purpose = str(item.get("purpose", "")).strip()
        execution = str(item.get("execution", "")).strip()
        if exercise:
            recommended_exercises.append(exercise)
        if purpose:
            key_points.append(purpose)
        if execution:
            key_points.append(execution)
    for item in payload.get("evidence_support", []) or []:
        text = str(item).strip()
        if text:
            key_points.append(text)
    for item in direct_key_points:
        text = str(item).strip()
        if text:
            key_points.append(text)
    for item in direct_exercises:
        if isinstance(item, dict):
            exercise_name = str(item.get("name") or item.get("title") or item.get("exercise") or "").strip()
            exercise_description = str(item.get("description") or item.get("summary") or "").strip()
            if exercise_name:
                recommended_exercises.append(exercise_name)
            if exercise_description:
                key_points.append(exercise_description)
            continue
        text = str(item).strip()
        if text:
            recommended_exercises.append(text)
    cautions = [str(item).strip() for item in direct_cautions if str(item).strip()]
    if not answer_parts and key_points:
        answer_parts.append(key_points[0])
    return {
        "answer": " ".join(answer_parts).strip(),
        "recommended_exercises": _dedupe_preserve_order(recommended_exercises)[:4]
        or _default_recommended_exercises_from_bundle(bundle),
        "key_points": _dedupe_preserve_order(key_points)[:4] or _default_key_points_from_bundle(bundle),
        "cautions": _dedupe_preserve_order(cautions)[:4] or _default_cautions_from_bundle(bundle),
        "citations": _default_citations_from_bundle(bundle),
        "retrieval_quality": bundle.quality,
    }


def _normalize_assessment_payload(payload: dict[str, Any], *, bundle: RetrievalBundle) -> dict[str, Any]:
    assessment = payload.get("assessment", {}) or {}
    if not isinstance(assessment, dict):
        assessment = {}
    title = str(assessment.get("title", "")).strip()
    summary = str(assessment.get("summary", "")).strip()
    answer_parts: list[str] = []
    if title and summary:
        answer_parts.append(f"{title}: {summary}")
    elif summary:
        answer_parts.append(summary)

    possible_causes = payload.get("possible_causes", []) or []
    cause_summaries: list[str] = []
    for item in possible_causes:
        if not isinstance(item, dict):
            continue
        cause_title = str(item.get("title", "")).strip()
        cause_summary = str(item.get("summary", "")).strip()
        if cause_title and cause_summary:
            cause_summaries.append(f"{cause_title}: {cause_summary}")
        elif cause_summary:
            cause_summaries.append(cause_summary)
    if cause_summaries:
        answer_parts.append("Posibles factores relevantes: " + " ".join(cause_summaries[:2]))

    recommended_exercises = payload.get("recommended_exercises", []) or []
    exercise_titles: list[str] = []
    key_points: list[str] = []
    cautions: list[str] = []
    for item in recommended_exercises:
        if not isinstance(item, dict):
            text = str(item).strip()
            if text:
                exercise_titles.append(text)
            continue
        exercise_title = str(item.get("title", "")).strip()
        exercise_summary = str(item.get("summary", "")).strip()
        if exercise_title:
            exercise_titles.append(exercise_title)
        if exercise_summary:
            key_points.append(exercise_summary)
        for step in item.get("steps", []) or []:
            step_text = str(step).strip()
            if step_text:
                key_points.append(step_text)
        for cue in item.get("cues", []) or []:
            cue_text = str(cue).strip()
            if cue_text:
                key_points.append(cue_text)
        for caution in item.get("errors_to_avoid", []) or []:
            caution_text = str(caution).strip()
            if caution_text:
                cautions.append(caution_text)

    for item in assessment.get("when_useful", []) or []:
        text = str(item).strip()
        if text:
            key_points.append(text)

    postural_considerations = payload.get("postural_considerations")
    if isinstance(postural_considerations, str) and postural_considerations.strip():
        key_points.append(postural_considerations.strip())
    elif isinstance(postural_considerations, list):
        for item in postural_considerations:
            text = str(item).strip()
            if text:
                key_points.append(text)

    return {
        "answer": " ".join(answer_parts).strip(),
        "recommended_exercises": _dedupe_preserve_order(exercise_titles)[:4]
        or _default_recommended_exercises_from_bundle(bundle),
        "key_points": _dedupe_preserve_order(key_points)[:4] or _default_key_points_from_bundle(bundle),
        "cautions": _dedupe_preserve_order(cautions)[:4] or _default_cautions_from_bundle(bundle),
        "citations": _default_citations_from_bundle(bundle),
        "retrieval_quality": bundle.quality,
    }


def _default_recommended_exercises_from_bundle(bundle: RetrievalBundle) -> list[str]:
    return [
        str(payload.get("knowledge_unit_title", "")).strip()
        for payload in [dict(item.payload) for item in bundle.knowledge_results]
        if str(payload.get("knowledge_unit_type", "")).strip() == "corrective_exercise"
        and str(payload.get("knowledge_unit_title", "")).strip()
    ][:4]


def _default_key_points_from_bundle(bundle: RetrievalBundle) -> list[str]:
    points = [
        str(payload.get("knowledge_unit_summary", "")).strip()
        for payload in [dict(item.payload) for item in bundle.knowledge_results[:4]]
        if str(payload.get("knowledge_unit_summary", "")).strip()
    ]
    return _dedupe_preserve_order(points)[:4]


def _default_cautions_from_bundle(bundle: RetrievalBundle) -> list[str]:
    cautions = [
        str(item).strip()
        for payload in [dict(item.payload) for item in bundle.knowledge_results[:4]]
        for item in payload.get("errors_to_avoid", [])
        if str(item).strip()
    ]
    return _dedupe_preserve_order(cautions)[:4]


def _default_citations_from_bundle(bundle: RetrievalBundle) -> list[dict[str, Any]]:
    knowledge_payloads = [dict(item.payload) for item in bundle.knowledge_results[:4]]
    return [
        {
            "source_type": str(payload.get("source_type", "youtube") or "youtube"),
            "title": str(payload.get("title", "") or ""),
            "source_uri": str(payload.get("source_uri", "") or ""),
            "segment_id": payload.get("segment_id"),
            "knowledge_unit_title": payload.get("knowledge_unit_title"),
            "timestamp_hint": ", ".join(payload.get("timestamps_raw", [])) or None,
        }
        for payload in knowledge_payloads
    ]


def _dedupe_preserve_order(items: list[str]) -> list[str]:
    return list(dict.fromkeys(item for item in items if item))


def _clean_answer_payload_texts(payload: dict[str, Any]) -> dict[str, Any]:
    cleaned = dict(payload)
    cleaned["answer"] = _clean_surface_text(str(cleaned.get("answer", "")).strip())
    cleaned["recommended_exercises"] = [
        _clean_surface_text(str(item).strip())
        for item in cleaned.get("recommended_exercises", [])
        if _clean_surface_text(str(item).strip())
    ]
    cleaned["key_points"] = [
        _clean_surface_text(str(item).strip())
        for item in cleaned.get("key_points", [])
        if _clean_surface_text(str(item).strip())
    ]
    cleaned["cautions"] = [
        _clean_surface_text(str(item).strip())
        for item in cleaned.get("cautions", [])
        if _clean_surface_text(str(item).strip())
    ]
    citations: list[dict[str, Any]] = []
    for item in cleaned.get("citations", []):
        if not isinstance(item, dict):
            continue
        citation = dict(item)
        citation["title"] = _clean_surface_text(str(citation.get("title", "")).strip())
        citation["knowledge_unit_title"] = _clean_surface_text(str(citation.get("knowledge_unit_title", "")).strip())
        citations.append(citation)
    cleaned["citations"] = citations
    return cleaned


def _maybe_translate_hf_payload_to_spanish(
    *,
    payload: dict[str, Any],
    query: str,
    api_key: str,
    model: str,
    router_url: str,
    timeout_sec: int,
) -> dict[str, Any]:
    if not _query_is_probably_spanish(query):
        return payload
    translated_visible = _translate_visible_fields_to_spanish(
        payload=payload,
        api_key=api_key,
        model=model,
        router_url=router_url,
        timeout_sec=timeout_sec,
    )
    if translated_visible is not None:
        return translated_visible
    messages = [
        {
            "role": "system",
            "content": (
                "Translate and normalize the following biomechanics answer to Spanish. "
                "Keep it concise. Preserve meaning. Do not add new medical claims. "
                "Remove raw retrieval prefixes such as 'Segment 22.5-24.3s:'. "
                "Return strict JSON matching the schema."
            ),
        },
        {
            "role": "user",
            "content": json.dumps(payload, ensure_ascii=False),
        },
    ]
    response_format = {
        "type": "json_schema",
        "json_schema": {
            "name": "grounded_answer",
            "schema": GroundedAnswer.model_json_schema(),
            "strict": True,
        },
    }
    try:
        raw = _call_hf_chat(
            api_key=api_key,
            model=model,
            router_url=router_url,
            timeout_sec=timeout_sec,
            messages=messages,
            response_format=response_format,
            max_tokens=900,
        )
        try:
            translated_model = GroundedAnswer.model_validate_json(raw)
            translated = translated_model.model_dump(mode="json")
        except Exception:
            translated = _normalize_answer_payload(_load_answer_payload(raw), bundle=RetrievalBundle(quality=str(payload.get("retrieval_quality", "")), knowledge_results=[], evidence_results=[], evidence_rows=[]))
            translated = GroundedAnswer.model_validate(translated).model_dump(mode="json")
        translated["retrieval_quality"] = payload.get("retrieval_quality", "")
        translated["used_collections"] = payload.get("used_collections", [])
        translated["model_used"] = payload.get("model_used", model)
        translated["answer_backend"] = payload.get("answer_backend", "hf")
        translated["citations"] = _merge_translated_citations(
            original_citations=payload.get("citations", []),
            translated_citations=translated.get("citations", []),
        )
        return _clean_answer_payload_texts(translated)
    except Exception:
        return payload


def _used_collections(bundle: RetrievalBundle) -> list[str]:
    used_collections: list[str] = []
    if bundle.knowledge_results:
        used_collections.append("video_knowledge_units_v1")
    if bundle.evidence_results:
        used_collections.append("video_segments_v1")
    return used_collections


def _query_is_probably_spanish(query: str) -> bool:
    lowered = query.lower()
    return any(token in lowered for token in (" me ", " dolor", " pecho", " omópl", " hombro", " pierna", " rodilla", " pie", " camino", " cuando "))


def _payload_looks_english_heavy(payload: dict[str, Any]) -> bool:
    answer = str(payload.get("answer", "")).strip()
    key_points = [str(item).strip() for item in payload.get("key_points", []) if str(item).strip()]
    exercises = [str(item).strip() for item in payload.get("recommended_exercises", []) if str(item).strip()]
    cautions = [str(item).strip() for item in payload.get("cautions", []) if str(item).strip()]
    sample = " ".join([answer, *key_points[:4], *exercises[:4], *cautions[:4]]).lower()
    english_markers = (
        " your ",
        " symptoms ",
        " suggest ",
        " exercise ",
        " shoulder ",
        " upper ",
        " lower ",
        " right ",
        " left ",
        " improve ",
        " during ",
        " while ",
        " avoid ",
        " do not ",
        " lower back ",
        " walking ",
        " segment ",
        " the ",
        " this ",
        " likely ",
        " primary ",
        " backside ",
        " rib cage ",
        " posture ",
        " spine ",
        " mobility ",
        " breathing ",
        " activation ",
        " tightness ",
        " thoracic ",
        " trap ",
        " traps ",
        " rear delt ",
        " arm path ",
        " gait ",
        " stance ",
        " foot ",
        " squat ",
    )
    return sum(1 for marker in english_markers if marker in f" {sample} ") >= 2


def _text_looks_english_heavy(text: str) -> bool:
    sample = text.lower()
    english_markers = (
        " your ",
        " symptoms ",
        " suggest ",
        " exercise ",
        " shoulder ",
        " upper ",
        " lower ",
        " right ",
        " left ",
        " improve ",
        " during ",
        " while ",
        " avoid ",
        " do not ",
        " walking ",
        " the ",
        " this ",
        " likely ",
        " primary ",
        " rib cage ",
        " posture ",
        " spine ",
        " mobility ",
        " breathing ",
        " activation ",
        " tightness ",
        " thoracic ",
        " trap ",
        " traps ",
        " rear delt ",
        " arm path ",
        " gait ",
        " stance ",
        " foot ",
        " squat ",
        " optimize ",
        " optimizing ",
        " impact of ",
        " importance of ",
        " compensatory ",
        " corrective ",
        " drill ",
    )
    return sum(1 for marker in english_markers if marker in f" {sample} ") >= 2


def _translate_visible_fields_to_spanish(
    *,
    payload: dict[str, Any],
    api_key: str,
    model: str,
    router_url: str,
    timeout_sec: int,
) -> dict[str, Any] | None:
    translated = dict(payload)
    try:
        translated["answer"] = _translate_text_to_spanish_best_effort(
            text=str(payload.get("answer", "")).strip(),
            api_key=api_key,
            model=model,
            router_url=router_url,
            timeout_sec=timeout_sec,
        )
        translated["recommended_exercises"] = _translate_list_to_spanish_best_effort(
            items=payload.get("recommended_exercises", []),
            api_key=api_key,
            model=model,
            router_url=router_url,
            timeout_sec=timeout_sec,
            force=True,
        )
        translated["key_points"] = _translate_list_to_spanish_best_effort(
            items=payload.get("key_points", []),
            api_key=api_key,
            model=model,
            router_url=router_url,
            timeout_sec=timeout_sec,
            force=True,
        )
        translated["cautions"] = _translate_list_to_spanish_best_effort(
            items=payload.get("cautions", []),
            api_key=api_key,
            model=model,
            router_url=router_url,
            timeout_sec=timeout_sec,
            force=True,
        )
        translated_titles: list[str] = []
        for item in payload.get("citations", []):
            if not isinstance(item, dict):
                continue
            raw_title = str((item.get("title") or item.get("knowledge_unit_title") or "")).strip()
            translated_titles.append(
                _translate_text_to_spanish_best_effort(
                    text=raw_title,
                    api_key=api_key,
                    model=model,
                    router_url=router_url,
                    timeout_sec=timeout_sec,
                    force=True,
                )
            )
        translated["citations"] = _merge_translated_citation_titles(
            original_citations=payload.get("citations", []),
            translated_titles=translated_titles,
        )
        return _clean_answer_payload_texts(translated)
    except Exception:
        return None


def _translate_list_to_spanish_best_effort(
    *,
    items: list[Any],
    api_key: str,
    model: str,
    router_url: str,
    timeout_sec: int,
    force: bool = False,
) -> list[str]:
    translated: list[str] = []
    for item in items:
        text = str(item).strip()
        if not text:
            continue
        translated.append(
            _translate_text_to_spanish_best_effort(
                text=text,
                api_key=api_key,
                model=model,
                router_url=router_url,
                timeout_sec=timeout_sec,
                force=force,
            )
        )
    return translated


def _translate_text_to_spanish_best_effort(
    *,
    text: str,
    api_key: str,
    model: str,
    router_url: str,
    timeout_sec: int,
    force: bool = False,
) -> str:
    cleaned = text.strip()
    if not cleaned:
        return ""
    try:
        return _translate_text_to_spanish_hf(
            text=cleaned,
            api_key=api_key,
            model=model,
            router_url=router_url,
            timeout_sec=timeout_sec,
            force=force,
        )
    except Exception:
        return _clean_surface_text(cleaned)


def _merge_translated_citation_titles(*, original_citations: list[Any], translated_titles: list[Any]) -> list[dict[str, Any]]:
    merged: list[dict[str, Any]] = []
    for index, item in enumerate(original_citations):
        if not isinstance(item, dict):
            continue
        citation = dict(item)
        translated_title = str(translated_titles[index]).strip() if index < len(translated_titles) else ""
        if translated_title:
            citation["title"] = translated_title
            citation["knowledge_unit_title"] = translated_title
        merged.append(citation)
    return merged


def _merge_translated_citations(*, original_citations: list[Any], translated_citations: list[Any]) -> list[dict[str, Any]]:
    merged: list[dict[str, Any]] = []
    for index, item in enumerate(original_citations):
        if not isinstance(item, dict):
            continue
        citation = dict(item)
        translated_item = translated_citations[index] if index < len(translated_citations) and isinstance(translated_citations[index], dict) else {}
        translated_title = str(translated_item.get("title") or translated_item.get("knowledge_unit_title") or "").strip()
        if translated_title:
            citation["title"] = translated_title
            citation["knowledge_unit_title"] = translated_title
        merged.append(citation)
    return merged


def _translate_text_to_spanish_hf(
    *,
    text: str,
    api_key: str,
    model: str,
    router_url: str,
    timeout_sec: int,
    force: bool = False,
) -> str:
    cleaned = text.strip()
    if not cleaned:
        return ""
    if not force and not _text_looks_english_heavy(cleaned):
        return cleaned
    body = {
        "model": model,
        "messages": [
            {
                "role": "system",
                "content": (
                    "Translate the following biomechanics text to natural Spanish. "
                    "Preserve meaning. Do not add new claims. "
                    "Return only the Spanish translation, with no JSON, no quotes, no explanations, and no <think> blocks."
                ),
            },
            {
                "role": "user",
                "content": cleaned,
            },
        ],
        "temperature": 0.0,
        "max_tokens": 1200,
    }
    response = requests.post(
        router_url,
        headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
        json=body,
        timeout=timeout_sec,
    )
    response.raise_for_status()
    content = response.json()["choices"][0]["message"]["content"]
    translated = _strip_think_blocks(content).strip()
    return translated or cleaned


def _clean_surface_text(text: str) -> str:
    cleaned = text.strip()
    cleaned = re.sub(r"^Segment\s+\d+(\.\d+)?-\d+(\.\d+)?s:\s*", "", cleaned, flags=re.IGNORECASE)
    for prefix in (
        "Corrective Exercise:",
        "Educational Point:",
        "Key Insight:",
        "Practical Advice:",
        "Mechanism:",
        "Warning:",
        "Test:",
        "Exercise:",
        "Cue:",
        "Advice:",
        "Observation:",
        "Protocol:",
        "Recommendation:",
        "Finding:",
        "Insight:",
        "Summary:",
    ):
        if cleaned.lower().startswith(prefix.lower()):
            cleaned = cleaned[len(prefix):].strip()
    return cleaned


def _build_fallback_grounded_answer(
    query: str,
    bundle: RetrievalBundle,
    *,
    model_name: str,
    error: Exception | None,
    attempted_backends: list[str] | None = None,
) -> dict[str, Any]:
    knowledge_payloads = [dict(item.payload) for item in bundle.knowledge_results]
    top_knowledge = knowledge_payloads[0] if knowledge_payloads else {}
    recommended_exercises = [
        str(payload.get("knowledge_unit_title", "")).strip()
        for payload in knowledge_payloads
        if str(payload.get("knowledge_unit_type", "")).strip() == "corrective_exercise"
        and str(payload.get("knowledge_unit_title", "")).strip()
    ][:4]
    key_points = [
        str(payload.get("knowledge_unit_summary", "")).strip()
        for payload in knowledge_payloads[:4]
        if str(payload.get("knowledge_unit_summary", "")).strip()
    ][:4]
    cautions = list(
        dict.fromkeys(
            str(item).strip()
            for payload in knowledge_payloads[:4]
            for item in payload.get("errors_to_avoid", [])
            if str(item).strip()
        )
    )[:4]
    citations = [
        {
            "source_type": str(payload.get("source_type", "youtube") or "youtube"),
            "title": str(payload.get("title", "") or ""),
            "source_uri": str(payload.get("source_uri", "") or ""),
            "segment_id": payload.get("segment_id"),
            "knowledge_unit_title": payload.get("knowledge_unit_title"),
            "timestamp_hint": ", ".join(payload.get("timestamps_raw", [])) or None,
        }
        for payload in knowledge_payloads[:4]
    ]
    used_collections = _used_collections(bundle)
    answer_parts: list[str] = []
    if top_knowledge:
        title = str(top_knowledge.get("knowledge_unit_title", "")).strip()
        summary = str(top_knowledge.get("knowledge_unit_summary", "")).strip()
        if title and summary:
            answer_parts.append(f"Con la evidencia disponible, el recurso mas cercano es '{title}': {summary}")
        elif summary:
            answer_parts.append(f"Con la evidencia disponible, el recurso mas cercano es: {summary}")
    else:
        answer_parts.append("La base actual tiene evidencia limitada para responder con precision esa consulta.")
    if recommended_exercises:
        answer_parts.append(f"Ejercicios relacionados encontrados: {', '.join(recommended_exercises)}.")
    if error is not None:
        answer_parts.append("La respuesta se armo con un fallback grounded porque el backend configurado no devolvio un resultado valido.")
    fallback_reason, fallback_error_code = _describe_error(error)
    payload = {
        "answer": " ".join(answer_parts).strip(),
        "recommended_exercises": recommended_exercises,
        "key_points": key_points,
        "cautions": cautions,
        "citations": citations,
        "retrieval_quality": bundle.quality,
        "used_collections": used_collections,
        "model_used": f"{model_name} (fallback)",
        "answer_backend": "grounded_fallback",
        "fallback_reason": fallback_reason,
        "fallback_error_code": fallback_error_code,
        "attempted_backends": attempted_backends or [],
        "query": query,
    }
    return _clean_answer_payload_texts(payload)


def _describe_error(error: Exception | None) -> tuple[str, str]:
    if error is None:
        return "", ""
    text = str(error).strip()
    lowered = text.lower()
    response_text = ""
    response = getattr(error, "response", None)
    if response is not None:
        response_text = str(getattr(response, "text", "") or "").strip()
    combined = f"{lowered} {response_text.lower()}".strip()
    if "insufficient_quota" in combined or "exceeded your current quota" in combined:
        return response_text or text, "insufficient_quota"
    if "rate limit" in combined or "too many requests" in combined:
        return response_text or text, "rate_limited"
    if "timed out" in combined or "timeout" in combined:
        return text, "timeout"
    if "connection refused" in combined or "max retries exceeded" in combined:
        return text, "connection_error"
    return text, "unknown_error"
