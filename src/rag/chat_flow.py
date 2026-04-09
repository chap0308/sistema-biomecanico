"""Chat-oriented orchestration helpers for image analysis and rendered replies."""

from __future__ import annotations

import json
import re
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any
from uuid import UUID

from api.schemas.image import ImageRestMultipartRequest
from detection.deficiencies import detect_rest_deficiencies
from detection.findings import detect_rest_findings
from scripts.debug_utils.plotting import save_group_metrics_csvs
from scripts.debug_utils.visualization import save_rest_phase1_overlay_image


@dataclass(slots=True)
class ChatArtifactFile:
    path: Path
    artifact_kind: str
    title: str
    metadata: dict[str, Any]


_REST_DEFICIENCY_LOCALIZATION: dict[str, dict[str, str]] = {
    "postural_shoulder_asymmetry": {
        "label": "Asimetría postural de hombros",
        "summary": "La postura en reposo sugiere una diferencia relevante en la línea de hombros.",
        "body_region": "shoulder",
    },
    "scapular_resting_asymmetry": {
        "label": "Asimetría escapular en reposo",
        "summary": "Los hallazgos combinados sugieren una presentación escapular asimétrica en reposo.",
        "body_region": "scapula",
    },
    "forward_posture_pattern": {
        "label": "Patrón postural adelantado",
        "summary": "La combinación de hallazgos sugiere una postura adelantada en el plano sagital.",
        "body_region": "thoracic_spine",
    },
    "thoracic_posture_pattern": {
        "label": "Patrón postural torácico",
        "summary": "La postura en reposo sugiere un sesgo torácico relevante que debe interpretarse con contexto clínico.",
        "body_region": "thoracic_spine",
    },
    "lateral_postural_compensation": {
        "label": "Compensación postural lateral",
        "summary": "Los hallazgos sugieren una compensación lateral multi-segmentaria en reposo.",
        "body_region": "pelvis",
    },
    "possible_scapular_winging_pattern": {
        "label": "Posible patrón de escápula alada",
        "summary": "Los hallazgos son compatibles con una posible prominencia escapular que conviene validar dinámicamente.",
        "body_region": "scapula",
    },
}


def create_chat_artifact_dir(*, conversation_id: UUID, message_id: UUID) -> Path:
    """Create the local directory used for one chat analysis run."""
    artifact_dir = Path("debug") / "chat" / str(conversation_id) / str(message_id)
    artifact_dir.mkdir(parents=True, exist_ok=True)
    return artifact_dir


def save_uploaded_group_images(
    *,
    request: ImageRestMultipartRequest,
    artifact_dir: Path,
) -> tuple[dict[str, dict[str, Path]], list[ChatArtifactFile]]:
    """Persist uploaded chat images locally so overlays and storage uploads can be produced."""
    originals_dir = artifact_dir / "originals"
    originals_dir.mkdir(parents=True, exist_ok=True)

    saved_paths: dict[str, dict[str, Path]] = {}
    artifacts: list[ChatArtifactFile] = []
    for group_name, slots in request.image_groups.items():
        saved_paths[group_name] = {}
        for slot_name, image in slots.items():
            filename = f"{group_name}_{slot_name}{Path(image.filename).suffix or '.jpg'}"
            target_path = originals_dir / filename
            target_path.write_bytes(image.payload)
            saved_paths[group_name][slot_name] = target_path
            artifacts.append(
                ChatArtifactFile(
                    path=target_path,
                    artifact_kind="image",
                    title=f"Original {group_name}/{slot_name}",
                    metadata={"group_name": group_name, "slot_name": slot_name, "artifact_role": "original"},
                )
            )
    return saved_paths, artifacts


def generate_static_debug_artifacts(
    *,
    request: ImageRestMultipartRequest,
    analysis_payload: dict[str, Any],
    saved_input_paths: dict[str, dict[str, Path]],
    artifact_dir: Path,
) -> list[ChatArtifactFile]:
    """Generate overlay images and artifact files for the MVP chat image flow."""
    groups = analysis_payload.get("groups", {})
    overlays_dir = artifact_dir / "overlays"
    overlays_dir.mkdir(parents=True, exist_ok=True)

    artifacts: list[ChatArtifactFile] = []
    rest_group = groups.get("rest_phase1")
    if isinstance(rest_group, dict):
        for view_name in ("front", "side", "back"):
            source_path = saved_input_paths.get("rest_phase1", {}).get(view_name)
            if source_path is None:
                continue
            output_path = overlays_dir / f"rest_phase1_{view_name}_overlay.png"
            save_rest_phase1_overlay_image(source_path, rest_group, view_name, output_path, overlay_mode="readable")
            artifacts.append(
                ChatArtifactFile(
                    path=output_path,
                    artifact_kind="debug_image",
                    title=f"Debug rest_phase1 {view_name}",
                    metadata={"group_name": "rest_phase1", "slot_name": view_name, "artifact_role": "debug_overlay"},
                )
            )

    csv_artifacts = save_group_metrics_csvs(groups, artifact_dir / "csv")
    for csv_path in csv_artifacts:
        artifacts.append(
            ChatArtifactFile(
                path=csv_path,
                artifact_kind="document",
                title=csv_path.stem.replace("_", " "),
                metadata={"artifact_role": "metrics_csv"},
            )
        )

    response_json_path = artifact_dir / "response.json"
    response_json_path.write_text(json.dumps(analysis_payload, indent=2, ensure_ascii=False), encoding="utf-8")
    artifacts.append(
        ChatArtifactFile(
            path=response_json_path,
            artifact_kind="document",
            title="Static image analysis response",
            metadata={"artifact_role": "response_json"},
        )
    )
    return artifacts


def build_rest_phase1_findings_and_deficiencies(
    analysis_payload: dict[str, Any],
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    """Build formal threshold-based findings and deficiencies for rest_phase1 only."""
    groups = analysis_payload.get("groups", {})
    rest_group = groups.get("rest_phase1")
    if not isinstance(rest_group, dict):
        return [], []

    findings_payload: list[dict[str, Any]] = []
    deficiencies_payload: list[dict[str, Any]] = []
    seen_deficiencies: set[tuple[str, str]] = set()

    for view_name, view_payload in (rest_group.get("metrics_by_view") or {}).items():
        metrics = view_payload.get("metrics", {})
        if not isinstance(metrics, dict):
            continue

        findings = detect_rest_findings(metrics, view=view_name)
        for finding in findings.items:
            serialized = asdict(finding)
            serialized["source_group"] = "rest_phase1"
            findings_payload.append(serialized)

        deficiencies = detect_rest_deficiencies(findings.items, view=view_name)
        for deficiency in deficiencies.items:
            key = (deficiency.id, deficiency.view)
            if key in seen_deficiencies:
                continue
            seen_deficiencies.add(key)
            localized = _REST_DEFICIENCY_LOCALIZATION.get(
                deficiency.id,
                {"label": deficiency.label, "summary": deficiency.summary, "body_region": "thoracic_spine"},
            )
            deficiencies_payload.append(
                {
                    **asdict(deficiency),
                    "label": localized["label"],
                    "summary": localized["summary"],
                    "source_group": "rest_phase1",
                    "body_region": localized["body_region"],
                    "related_metrics": [],
                }
            )

    return findings_payload, deficiencies_payload


def build_chat_deficiencies_from_static_analysis(analysis_payload: dict[str, Any]) -> list[dict[str, Any]]:
    """Return the chat-facing deficiency list from the formal rest_phase1 detector path."""
    _, deficiencies = build_rest_phase1_findings_and_deficiencies(analysis_payload)
    return deficiencies


def summarize_deficiencies_for_query(deficiencies: list[dict[str, Any]]) -> str:
    """Render deficiencies as compact text for RAG query augmentation."""
    if not deficiencies:
        return ""
    parts: list[str] = []
    seen: set[tuple[str, str]] = set()
    for deficiency in deficiencies[:10]:
        label = str(deficiency.get("label", "")).strip()
        summary = str(deficiency.get("summary", "")).strip()
        severity = str(deficiency.get("severity", "")).strip()
        view = _view_label(str(deficiency.get("view", "")).strip())
        dedupe_key = (label, view)
        if dedupe_key in seen:
            continue
        seen.add(dedupe_key)
        label_with_view = f"{view}: {label}" if view and label else label
        if label_with_view and summary:
            parts.append(f"{label_with_view} ({severity}): {summary}")
        elif label:
            parts.append(label_with_view)
    return "\n".join(parts)


def build_chat_query(
    *,
    user_message: str,
    deficiencies: list[dict[str, Any]],
    analysis_jobs: list[dict[str, Any]] | None = None,
) -> str:
    """Compose the text sent to retrieval + answering."""
    pieces = [user_message.strip()]
    deficiency_summary = summarize_deficiencies_for_query(deficiencies)
    if deficiency_summary:
        pieces.append("Deficiencias detectadas por análisis de imágenes:")
        pieces.append(deficiency_summary)
    return "\n\n".join(piece for piece in pieces if piece)


def build_rendered_blocks(
    *,
    answer_payload: dict[str, Any],
    deficiencies: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    """Build UI-friendly assistant blocks for the chat frontend."""
    blocks: list[dict[str, Any]] = []
    if deficiencies:
        blocks.append(
            {
                "type": "list",
                "title": "Deficiencias detectadas",
                "items": [
                    _render_deficiency_item(item)
                    for item in deficiencies[:6]
                    if item.get("label") and item.get("summary")
                ],
            }
        )
    answer_text = str(answer_payload.get("answer", "")).strip()
    if answer_text:
        blocks.append({"type": "section", "title": "Diagnóstico funcional orientativo", "content": answer_text})
    key_points = [str(item).strip() for item in answer_payload.get("key_points", []) if str(item).strip()]
    if key_points:
        blocks.append({"type": "list", "title": "Puntos clave", "items": key_points[:6]})
    exercises = [str(item).strip() for item in answer_payload.get("recommended_exercises", []) if str(item).strip()]
    if exercises:
        blocks.append({"type": "list", "title": "Ejercicios sugeridos", "items": exercises[:6]})
    cautions = [str(item).strip() for item in answer_payload.get("cautions", []) if str(item).strip()]
    if cautions:
        blocks.append({"type": "list", "title": "Advertencias", "items": cautions[:6]})
    citations = answer_payload.get("citations", [])
    if citations:
        citation_lines = []
        for item in citations[:6]:
            if not isinstance(item, dict):
                continue
            title = str(item.get("title") or item.get("knowledge_unit_title") or "Fuente").strip()
            title = _clean_surface_text(title)
            source_uri = str(item.get("source_uri", "")).strip()
            timestamp_hint = str(item.get("timestamp_hint", "")).strip()
            line = title
            if source_uri:
                line += f" - {source_uri}"
            if timestamp_hint:
                line += f" ({timestamp_hint})"
            citation_lines.append(line)
        if citation_lines:
            blocks.append({"type": "list", "title": "Fuentes relacionadas", "items": citation_lines})
    return blocks


def debug_public_url_for_path(path: Path) -> str:
    """Map a local debug artifact path to the mounted FastAPI static URL."""
    debug_root = Path("debug").resolve()
    relative_path = path.resolve().relative_to(debug_root)
    return f"/debug-assets/{relative_path.as_posix()}"


def _render_deficiency_item(item: dict[str, Any]) -> str:
    view = _view_label(str(item.get("view", "")).strip())
    label = str(item.get("label", "")).strip()
    summary = str(item.get("summary", "")).strip()
    prefix = f"{view}: " if view else ""
    return f"{prefix}{label}: {summary}"


def _view_label(view: str) -> str:
    mapping = {
        "front": "Vista frontal",
        "side": "Vista lateral",
        "back": "Vista posterior",
    }
    return mapping.get(view, "")


def _clean_surface_text(text: str) -> str:
    cleaned = text.strip()
    cleaned = cleaned.removeprefix("Corrective Exercise:").strip()
    cleaned = cleaned.removeprefix("Educational Point:").strip()
    cleaned = cleaned.removeprefix("Key Insight:").strip()
    cleaned = cleaned.removeprefix("Practical Advice:").strip()
    cleaned = cleaned.removeprefix("Mechanism:").strip()
    cleaned = cleaned.removeprefix("Warning:").strip()
    cleaned = cleaned.removeprefix("Test:").strip()
    cleaned = cleaned.removeprefix("Exercise:").strip()
    cleaned = cleaned.removeprefix("Cue:").strip()
    cleaned = cleaned.removeprefix("Advice:").strip()
    cleaned = cleaned.removeprefix("Observation:").strip()
    cleaned = cleaned.removeprefix("Protocol:").strip()
    cleaned = cleaned.removeprefix("Recommendation:").strip()
    cleaned = cleaned.removeprefix("Finding:").strip()
    cleaned = cleaned.removeprefix("Insight:").strip()
    cleaned = cleaned.removeprefix("Summary:").strip()
    cleaned = cleaned.removeprefix("Segment").strip()
    cleaned = cleaned.lstrip(":").strip()
    cleaned = re.sub(r"^\d+(\.\d+)?-\d+(\.\d+)?s:\s*", "", cleaned)
    return cleaned.strip()
