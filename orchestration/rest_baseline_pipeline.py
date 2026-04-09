"""Integration pipeline for the mandatory rest baseline endpoint."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any

from api.schemas.baseline import RestBaselineMultipartRequest
from api.schemas.image import ImageRestMultipartRequest
from detection.deficiencies import detect_rest_deficiencies, detect_scapula_rest_deficiencies
from detection.findings import detect_foot_triptych_findings, detect_rest_findings, detect_scapula_rest_findings
from detection.models import Finding
from orchestration.image_pipeline import ImageRestPipeline
from orchestration.isa_video_pipeline import IsaVideoPipeline

_SEVERITY_SCORE = {"mild": 1.0, "moderate": 2.0, "severe": 3.0}


@dataclass(slots=True)
class RestBaselinePipeline:
    """Coordinate grouped static analysis plus mandatory breathing integration."""

    image_pipeline: ImageRestPipeline
    isa_video_pipeline: IsaVideoPipeline
    pipeline_version: str = "rest-baseline-v1"

    def analyze(self, request: RestBaselineMultipartRequest) -> dict[str, Any]:
        """Run the full baseline contract from grouped images plus breathing video."""
        static_groups = {
            group_name: group_payload
            for group_name, group_payload in request.image_groups.items()
            if group_name != "isa"
        }
        static_result = self.image_pipeline.analyze(
            ImageRestMultipartRequest(
                image_groups=static_groups,
                include_placeholders=request.include_placeholders,
            )
        )
        thoracic_result = self.isa_video_pipeline.analyze_components(
            isa_image=request.image_groups["isa"]["front_torso"],
            breathing_video=request.breathing_video,
            include_placeholders=request.include_placeholders,
            aggregation=request.aggregation,
            frame_step=request.frame_step,
            max_frames=request.max_frames,
            reject_outliers=request.reject_outliers,
        )

        metrics_by_group = dict(static_result["groups"])
        metrics_by_group.update(thoracic_result)
        metrics_by_group = self._rename_scapula_group(metrics_by_group)

        findings_by_group = self._build_findings_by_group(metrics_by_group)
        deficiencies_by_group = self._build_deficiencies_by_group(findings_by_group)
        integrated_findings = self._build_integrated_findings(findings_by_group)
        preliminary_deficiencies = self._build_preliminary_deficiencies(deficiencies_by_group)
        triggered_tests_next = self._build_triggered_tests(preliminary_deficiencies["items"])
        scapular_baseline = self._build_scapular_baseline(metrics_by_group, findings_by_group)

        requested_groups = [
            "scapula_rest" if group_name == "scapula" else group_name
            for group_name in request.image_groups.keys()
        ]
        requested_groups.append("breathing_video")

        return {
            "analysis_type": "rest_baseline",
            "status": "success",
            "capture_mode": "multipart_image_groups_plus_breathing_video",
            "pipeline_version": self.pipeline_version,
            "requested_groups": requested_groups,
            "metrics_by_group": metrics_by_group,
            "findings_by_group": findings_by_group,
            "deficiencies_by_group": deficiencies_by_group,
            "integrated_findings": integrated_findings,
            "preliminary_deficiencies": preliminary_deficiencies,
            "triggered_tests_next": triggered_tests_next,
            "baseline_scapular_state": scapular_baseline["baseline_scapular_state"],
            "baseline_scapular_asymmetry": scapular_baseline["baseline_scapular_asymmetry"],
            "baseline_scapular_proxy_metrics": scapular_baseline["baseline_scapular_proxy_metrics"],
            "baseline_scapula_context": scapular_baseline["baseline_scapula_context"],
        }

    @staticmethod
    def _rename_scapula_group(metrics_by_group: dict[str, Any]) -> dict[str, Any]:
        if "scapula" not in metrics_by_group:
            return metrics_by_group
        renamed = dict(metrics_by_group)
        renamed["scapula_rest"] = renamed.pop("scapula")
        return renamed

    def _build_findings_by_group(self, metrics_by_group: dict[str, Any]) -> dict[str, dict[str, object]]:
        findings_by_group: dict[str, dict[str, object]] = {}

        rest_phase1 = metrics_by_group.get("rest_phase1")
        if isinstance(rest_phase1, dict):
            rest_items: list[dict[str, object]] = []
            for view_name, view_payload in rest_phase1.get("metrics_by_view", {}).items():
                findings = detect_rest_findings(view_payload.get("metrics", {}), view=view_name)
                for item in findings.items:
                    serialized = asdict(item)
                    serialized["source_group"] = "rest_phase1"
                    rest_items.append(serialized)
            findings_by_group["rest_phase1"] = {
                "status": "completed",
                "items": rest_items,
                "ready": True,
                "baseline_flags": [],
                "severity_score": self._block_severity_score(rest_items),
            }

        scapula_rest = metrics_by_group.get("scapula_rest")
        if isinstance(scapula_rest, dict):
            scapula_findings = detect_scapula_rest_findings(scapula_rest)
            scapula_items = []
            for item in scapula_findings.items:
                serialized = asdict(item)
                serialized["source_group"] = "scapula_rest"
                scapula_items.append(serialized)
            findings_by_group["scapula_rest"] = {
                "status": "completed",
                "items": scapula_items,
                "ready": True,
                "baseline_flags": self._scapula_baseline_flags(scapula_items),
                "severity_score": self._block_severity_score(scapula_items),
            }

        foot_triptych = metrics_by_group.get("foot_triptych")
        if isinstance(foot_triptych, dict):
            foot_findings = detect_foot_triptych_findings(foot_triptych.get("metrics", {}))
            foot_items = []
            for item in foot_findings.items:
                serialized = asdict(item)
                serialized["source_group"] = "foot_triptych"
                foot_items.append(serialized)
            findings_by_group["foot_triptych"] = {
                "status": "completed",
                "items": foot_items,
                "ready": True,
                "baseline_flags": [],
                "severity_score": self._block_severity_score(foot_items),
            }

        for group_name in ("face", "isa", "breathing"):
            if group_name in metrics_by_group:
                findings_by_group[group_name] = {
                    "status": "completed",
                    "items": [],
                    "ready": True,
                    "baseline_flags": [],
                    "severity_score": 0.0,
                }

        return findings_by_group

    def _build_deficiencies_by_group(self, findings_by_group: dict[str, dict[str, object]]) -> dict[str, dict[str, object]]:
        deficiencies_by_group: dict[str, dict[str, object]] = {}

        rest_phase1_payload = findings_by_group.get("rest_phase1")
        if isinstance(rest_phase1_payload, dict):
            by_view: dict[str, list[Finding]] = {}
            for item in rest_phase1_payload.get("items", []):
                view = str(item.get("view"))
                by_view.setdefault(view, []).append(self._finding_from_payload(item))
            rest_items: list[dict[str, object]] = []
            for view, findings in by_view.items():
                deficiencies = detect_rest_deficiencies(findings, view=view)
                for deficiency in deficiencies.items:
                    serialized = asdict(deficiency)
                    serialized["source_group"] = "rest_phase1"
                    rest_items.append(serialized)
            deficiencies_by_group["rest_phase1"] = {
                "status": "completed",
                "items": rest_items,
                "ready": True,
                "baseline_flags": [],
                "severity_score": self._block_severity_score(rest_items),
            }

        scapula_payload = findings_by_group.get("scapula_rest")
        if isinstance(scapula_payload, dict):
            scapula_findings = [self._finding_from_payload(item) for item in scapula_payload.get("items", [])]
            scapula_deficiencies = detect_scapula_rest_deficiencies(scapula_findings)
            scapula_items: list[dict[str, object]] = []
            for deficiency in scapula_deficiencies.items:
                serialized = asdict(deficiency)
                serialized["source_group"] = "scapula_rest"
                scapula_items.append(serialized)
            deficiencies_by_group["scapula_rest"] = {
                "status": "completed",
                "items": scapula_items,
                "ready": True,
                "baseline_flags": self._scapula_baseline_flags(scapula_payload.get("items", [])),
                "severity_score": self._block_severity_score(scapula_items),
            }

        for group_name in ("foot_triptych", "face", "isa", "breathing"):
            if group_name in findings_by_group and group_name not in deficiencies_by_group:
                deficiencies_by_group[group_name] = {
                    "status": "completed",
                    "items": [],
                    "ready": True,
                    "baseline_flags": [],
                    "severity_score": 0.0,
                }

        return deficiencies_by_group

    def _build_integrated_findings(self, findings_by_group: dict[str, dict[str, object]]) -> dict[str, object]:
        deduped: dict[tuple[str, str], dict[str, object]] = {}
        for group_payload in findings_by_group.values():
            for item in group_payload.get("items", []):
                key = (str(item.get("id")), str(item.get("view")))
                deduped[key] = item
        sorted_items = sorted(
            deduped.values(),
            key=lambda item: (
                float(item.get("weight") or 0.0),
                _SEVERITY_SCORE.get(str(item.get("severity") or ""), 0.0),
                str(item.get("id") or ""),
            ),
            reverse=True,
        )
        return {
            "status": "completed",
            "items": sorted_items,
            "ready": True,
            "baseline_flags": [],
            "severity_score": self._block_severity_score(sorted_items),
        }

    def _build_scapular_baseline(
        self,
        metrics_by_group: dict[str, Any],
        findings_by_group: dict[str, dict[str, object]],
    ) -> dict[str, dict[str, object] | None]:
        scapula_group = metrics_by_group.get("scapula_rest")
        scapula_findings_payload = findings_by_group.get("scapula_rest", {})
        scapula_findings = scapula_findings_payload.get("items", []) if isinstance(scapula_findings_payload, dict) else []
        if not isinstance(scapula_group, dict):
            return {
                "baseline_scapular_state": None,
                "baseline_scapular_asymmetry": None,
                "baseline_scapular_proxy_metrics": None,
                "baseline_scapula_context": None,
            }

        metrics = scapula_group.get("metrics", {})
        if not isinstance(metrics, dict):
            metrics = {}

        robust_metric_names = ("scapular_elevation_difference", "scapular_symmetry_index")
        proxy_metric_names = (
            "scapula_spine_distance_left",
            "scapula_spine_distance_right",
            "scapular_internal_rotation_left",
            "scapular_internal_rotation_right",
            "scapular_upward_rotation_left",
            "scapular_upward_rotation_right",
            "winging_index",
        )
        robust_metrics = {name: metrics[name] for name in robust_metric_names if name in metrics}
        proxy_metrics = {name: metrics[name] for name in proxy_metric_names if name in metrics}
        state_confidences = [
            float(metric.get("confidence"))
            for metric in robust_metrics.values()
            if isinstance(metric, dict) and isinstance(metric.get("confidence"), (int, float))
        ]
        state_confidence = min(state_confidences) if state_confidences else None
        baseline_context = self._build_scapula_context(scapula_findings)

        return {
            "baseline_scapular_state": {
                "status": "completed",
                "summary": "Static scapular baseline established for later scapulohumeral video comparison. Robust asymmetry metrics describe the baseline state; posterior proxies provide cautious context only.",
                "use_in_dynamic_analysis": "Compare timing, left-right asymmetry, and movement change against this static baseline rather than treating proxy values as direct scapular measurements.",
                "confidence": state_confidence,
                "robust_metrics": robust_metrics,
                "supporting_findings": scapula_findings,
            },
            "baseline_scapular_asymmetry": {
                "status": "completed",
                "summary": "Static asymmetry block intended to contextualize dynamic scapulohumeral rhythm findings.",
                "metrics": robust_metrics,
                "findings": [
                    item
                    for item in scapula_findings
                    if str(item.get("id")) in {"scapular_elevation_asymmetry", "scapular_geometric_asymmetry"}
                ],
            },
            "baseline_scapular_proxy_metrics": {
                "status": "completed",
                "summary": "Posterior shoulder-girdle proxy metrics intended for cautious baseline comparison in dynamic video analysis.",
                "metrics": proxy_metrics,
                "findings": [
                    item
                    for item in scapula_findings
                    if str(item.get("id")) not in {"scapular_elevation_asymmetry", "scapular_geometric_asymmetry", "static_scapular_symmetry"}
                ],
            },
            "baseline_scapula_context": baseline_context,
        }

    def _build_preliminary_deficiencies(self, deficiencies_by_group: dict[str, dict[str, object]]) -> dict[str, object]:
        deduped: dict[tuple[str, str], dict[str, object]] = {}
        for group_payload in deficiencies_by_group.values():
            for item in group_payload.get("items", []):
                key = (str(item.get("id")), str(item.get("view")))
                deduped[key] = item
        sorted_items = sorted(
            deduped.values(),
            key=lambda item: (
                float(item.get("weight") or 0.0),
                _SEVERITY_SCORE.get(str(item.get("severity") or ""), 0.0),
                str(item.get("id") or ""),
            ),
            reverse=True,
        )
        return {
            "status": "completed",
            "items": sorted_items,
            "ready": True,
            "baseline_flags": [],
            "severity_score": self._block_severity_score(sorted_items),
        }

    def _build_triggered_tests(self, deficiencies: list[dict[str, object]]) -> dict[str, object]:
        triggered: list[dict[str, object]] = []
        seen: set[str] = set()
        deficiency_ids = {str(item.get("id")) for item in deficiencies}

        trigger_map = {
            "cervical_rotation_test": {
                "scapular_resting_asymmetry",
                "possible_scapular_winging_pattern",
                "thoracic_posture_pattern",
                "scapulothoracic_postural_asymmetry",
                "possible_scapular_instability",
                "possible_altered_scapulohumeral_rhythm",
            },
            "active_weight_shift_test": {
                "lateral_postural_compensation",
                "forward_posture_pattern",
            },
        }

        for test_type, supporting_deficiencies in trigger_map.items():
            matched = sorted(deficiency_ids.intersection(supporting_deficiencies))
            if not matched or test_type in seen:
                continue
            triggered.append(
                {
                    "test_type": test_type,
                    "reason": f"Triggered from baseline deficiencies: {', '.join(matched)}.",
                    "source": "baseline",
                    "confidence": "low",
                }
            )
            seen.add(test_type)

        return {
            "status": "completed",
            "items": triggered,
            "ready": True,
            "baseline_flags": [],
            "severity_score": 0.0,
        }

    @staticmethod
    def _finding_from_payload(item: dict[str, object]) -> Finding:
        return Finding(
            id=str(item.get("id")),
            label=str(item.get("label")),
            summary=str(item.get("summary")),
            severity=str(item.get("severity")),
            confidence=str(item.get("confidence")),
            view=str(item.get("view")),
            side=str(item.get("side")) if item.get("side") is not None else None,
            weight=float(item.get("weight")) if isinstance(item.get("weight"), (int, float)) else None,
            related_metrics=[str(metric_name) for metric_name in item.get("related_metrics", [])],
        )

    @staticmethod
    def _block_severity_score(items: list[dict[str, object]]) -> float:
        if not items:
            return 0.0
        score = 0.0
        for item in items:
            weight = float(item.get("weight") or 0.0)
            severity = _SEVERITY_SCORE.get(str(item.get("severity") or ""), 0.0)
            score += weight * severity
        return round(score, 3)

    @staticmethod
    def _scapula_baseline_flags(items: list[dict[str, object]]) -> list[str]:
        ids = {str(item.get("id")) for item in items}
        flags: list[str] = []
        if {"scapular_elevation_asymmetry", "scapular_geometric_asymmetry"}.intersection(ids):
            flags.append("baseline_scapular_asymmetry")
        if "possible_scapular_protraction_asymmetry" in ids:
            flags.append("possible_protraction_bias")
        if "possible_static_winging" in ids:
            flags.append("winging_suspected")
        if "scapular_upward_rotation_asymmetry" in ids:
            flags.append("rotation_asymmetry")
        if any(flag in ids for flag in {"scapular_elevation_asymmetry", "possible_static_winging", "scapular_upward_rotation_asymmetry"}):
            flags.append("monitor_in_dynamic_analysis")
        return flags

    @staticmethod
    def _build_scapula_context(items: list[dict[str, object]]) -> dict[str, Any]:
        ids = {str(item.get("id")): item for item in items}
        protraction = ids.get("possible_scapular_protraction_asymmetry")
        return {
            "elevation_asymmetry": "scapular_elevation_asymmetry" in ids,
            "protraction_bias": str(protraction.get("side")) if isinstance(protraction, dict) and protraction.get("side") else "none",
            "winging_suspected": "possible_static_winging" in ids,
            "rotation_asymmetry": "scapular_upward_rotation_asymmetry" in ids,
        }
