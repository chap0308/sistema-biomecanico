"""Grouped feet triptych pipeline."""

from __future__ import annotations

from dataclasses import dataclass
from math import isnan
from typing import Any

from biomechanics.foot_metrics import (
    analyze_arch_image,
    analyze_calcaneal_image,
    analyze_foot_progression_image,
)
from orchestration.image_subpipelines.common import decode_image_or_raise, serialize_metric_snapshot
from api.schemas.image import UploadedStaticImage


@dataclass(slots=True)
class FootTriptychPipeline:
    """Run contour-based heuristics over the static feet triptych."""

    def analyze(self, images: dict[str, UploadedStaticImage], *, include_placeholders: bool) -> dict[str, object]:
        """Analyze the frontal, posterior and bilateral arch images."""
        _ = include_placeholders
        processing_by_view: dict[str, dict[str, object]] = {}
        metrics: dict[str, dict[str, object]] = {}
        debug_by_view: dict[str, dict[str, object]] = {}

        front_image, front_width, front_height = decode_image_or_raise(images["front"].payload)
        back_image, back_width, back_height = decode_image_or_raise(images["back"].payload)
        left_arch_image, left_width, left_height = decode_image_or_raise(images["left_arch"].payload)
        right_arch_image, right_width, right_height = decode_image_or_raise(images["right_arch"].payload)

        processing_by_view["front"] = {
            "detected": True,
            "detector": "opencv_foot_contours",
            "image_width": front_width,
            "image_height": front_height,
            "notes": [],
        }
        processing_by_view["back"] = {
            "detected": True,
            "detector": "opencv_foot_contours",
            "image_width": back_width,
            "image_height": back_height,
            "notes": [],
        }
        processing_by_view["left_arch"] = {
            "detected": True,
            "detector": "opencv_foot_contours",
            "image_width": left_width,
            "image_height": left_height,
            "notes": [],
        }
        processing_by_view["right_arch"] = {
            "detected": True,
            "detector": "opencv_foot_contours",
            "image_width": right_width,
            "image_height": right_height,
            "notes": [],
        }

        def build_metric_payload(
            *,
            name: str,
            value: float | None,
            plane: str,
            unit: str,
            priority: str,
            status: str,
            confidence: float | None,
            quality_notes: list[str],
            classification: str | None,
            flags: list[str],
        ) -> dict[str, object]:
            return {
                "name": name,
                "value": value,
                "plane": plane,
                "unit": unit,
                "measurement_type": "proxy",
                "priority": priority,
                "status": status,
                "notes": quality_notes,
                "confidence": confidence,
                "quality_notes": quality_notes,
                "classification": classification,
                "flags": flags,
                "landmarks": None,
                "frame_index": None,
            }

        try:
            progression_analysis = analyze_foot_progression_image(front_image)
            progression = progression_analysis["metrics"]
            progression_details = progression_analysis.get("metric_details", {})
            debug_by_view["front"] = progression_analysis["debug"]
            front_notes = sorted({note for detail in progression_details.values() if isinstance(detail, dict) for note in detail.get("quality_notes", [])})
            processing_by_view["front"]["notes"] = front_notes
        except ValueError as exc:
            progression = {
                "foot_progression_angle_left": None,
                "foot_progression_angle_right": None,
            }
            progression_details = {}
            front_notes = [str(exc), "Placeholder until foot segmentation is improved."]
            processing_by_view["front"]["notes"] = front_notes
            debug_by_view["front"] = {"metrics": progression, "quality_notes": front_notes}

        try:
            calcaneal_analysis = analyze_calcaneal_image(back_image)
            calcaneal = calcaneal_analysis["metrics"]
            calcaneal_details = calcaneal_analysis.get("metric_details", {})
            debug_by_view["back"] = calcaneal_analysis["debug"]
            back_notes = sorted({note for detail in calcaneal_details.values() if isinstance(detail, dict) for note in detail.get("quality_notes", [])})
            processing_by_view["back"]["notes"] = back_notes
        except ValueError as exc:
            calcaneal = {
                "calcaneal_angle_left": None,
                "calcaneal_angle_right": None,
            }
            calcaneal_details = {}
            back_notes = [str(exc), "Placeholder until rearfoot contour isolation is improved."]
            processing_by_view["back"]["notes"] = back_notes
            debug_by_view["back"] = {"metrics": calcaneal, "quality_notes": back_notes}

        arch_results: dict[str, dict[str, Any]] = {}
        for side_name, image_array, view_key in (
            ("left", left_arch_image, "left_arch"),
            ("right", right_arch_image, "right_arch"),
        ):
            metric_name = f"arch_height_ratio_{side_name}"
            try:
                analysis = analyze_arch_image(image_array)
                arch_results[metric_name] = {
                    "value": float(analysis["metric"]),
                    "status": str(analysis.get("status", "computed")),
                    "confidence": float(analysis.get("confidence", 0.0)),
                    "quality_notes": list(analysis.get("quality_notes", [])),
                    "classification": analysis.get("classification"),
                    "flags": list(analysis.get("flags", [])),
                }
                debug_by_view[view_key] = analysis["debug"]
                processing_by_view[view_key]["notes"] = arch_results[metric_name]["quality_notes"]
            except ValueError as exc:
                notes = [str(exc), "Placeholder until lateral arch contour isolation is improved."]
                arch_results[metric_name] = {
                    "value": None,
                    "status": "placeholder",
                    "confidence": 0.0,
                    "quality_notes": notes,
                    "classification": None,
                    "flags": [],
                }
                debug_by_view[view_key] = {"metrics": {metric_name: None}, "quality_notes": notes}
                processing_by_view[view_key]["notes"] = notes

        metrics["foot_progression_angle_left"] = build_metric_payload(
            name="foot_progression_angle_left",
            value=progression.get("foot_progression_angle_left"),
            plane="transverse",
            unit="degrees",
            priority="P0" if progression.get("foot_progression_angle_left") is not None else "P1",
            status="computed" if progression.get("foot_progression_angle_left") is not None else "placeholder",
            confidence=progression_details.get("foot_progression_angle_left", {}).get("confidence"),
            quality_notes=list(progression_details.get("foot_progression_angle_left", {}).get("quality_notes", [])),
            classification=progression_details.get("foot_progression_angle_left", {}).get("classification"),
            flags=list(progression_details.get("foot_progression_angle_left", {}).get("flags", [])),
        )
        metrics["foot_progression_angle_right"] = build_metric_payload(
            name="foot_progression_angle_right",
            value=progression.get("foot_progression_angle_right"),
            plane="transverse",
            unit="degrees",
            priority="P0" if progression.get("foot_progression_angle_right") is not None else "P1",
            status="computed" if progression.get("foot_progression_angle_right") is not None else "placeholder",
            confidence=progression_details.get("foot_progression_angle_right", {}).get("confidence"),
            quality_notes=list(progression_details.get("foot_progression_angle_right", {}).get("quality_notes", [])),
            classification=progression_details.get("foot_progression_angle_right", {}).get("classification"),
            flags=list(progression_details.get("foot_progression_angle_right", {}).get("flags", [])),
        )
        metrics["calcaneal_angle_left"] = build_metric_payload(
            name="calcaneal_angle_left",
            value=calcaneal.get("calcaneal_angle_left"),
            plane="frontal",
            unit="degrees",
            priority="P0" if calcaneal.get("calcaneal_angle_left") is not None else "P1",
            status="computed" if calcaneal.get("calcaneal_angle_left") is not None else "placeholder",
            confidence=calcaneal_details.get("calcaneal_angle_left", {}).get("confidence"),
            quality_notes=list(calcaneal_details.get("calcaneal_angle_left", {}).get("quality_notes", [])),
            classification=calcaneal_details.get("calcaneal_angle_left", {}).get("classification"),
            flags=list(calcaneal_details.get("calcaneal_angle_left", {}).get("flags", [])),
        )
        metrics["calcaneal_angle_right"] = build_metric_payload(
            name="calcaneal_angle_right",
            value=calcaneal.get("calcaneal_angle_right"),
            plane="frontal",
            unit="degrees",
            priority="P0" if calcaneal.get("calcaneal_angle_right") is not None else "P1",
            status="computed" if calcaneal.get("calcaneal_angle_right") is not None else "placeholder",
            confidence=calcaneal_details.get("calcaneal_angle_right", {}).get("confidence"),
            quality_notes=list(calcaneal_details.get("calcaneal_angle_right", {}).get("quality_notes", [])),
            classification=calcaneal_details.get("calcaneal_angle_right", {}).get("classification"),
            flags=list(calcaneal_details.get("calcaneal_angle_right", {}).get("flags", [])),
        )
        for metric_name, result in arch_results.items():
            metrics[metric_name] = build_metric_payload(
                name=metric_name,
                value=result["value"],
                plane="sagittal",
                unit="ratio",
                priority="P0" if result["value"] is not None else "P1",
                status=result["status"],
                confidence=result["confidence"],
                quality_notes=result["quality_notes"],
                classification=result["classification"],
                flags=result["flags"],
            )

        confidence_overall = self._overall_confidence(metrics=metrics, processing_by_view=processing_by_view)
        foot_triptych_summary = self._build_summary(metrics=metrics, confidence_overall=confidence_overall, processing_by_view=processing_by_view)

        for view_name, debug_payload in debug_by_view.items():
            if isinstance(debug_payload, dict):
                debug_payload["metrics"] = serialize_metric_snapshot(metrics)
                debug_payload["view"] = view_name
        debug_by_view.setdefault("summary", {})["foot_triptych_summary"] = foot_triptych_summary

        return {
            "status": "success",
            "processing_by_view": processing_by_view,
            "metrics": metrics,
            "confidence_overall": confidence_overall,
            "foot_triptych_summary": foot_triptych_summary,
            "debug_by_view": debug_by_view,
        }

    @staticmethod
    def _overall_confidence(*, metrics: dict[str, dict[str, object]], processing_by_view: dict[str, dict[str, object]]) -> float:
        confidences = [
            float(metric["confidence"])
            for metric in metrics.values()
            if isinstance(metric, dict) and metric.get("confidence") is not None and metric.get("status") != "placeholder"
        ]
        if not confidences:
            return 0.0
        overall = sum(confidences) / len(confidences)
        placeholder_count = sum(1 for metric in metrics.values() if isinstance(metric, dict) and metric.get("status") == "placeholder")
        view_penalty = sum(0.03 for view in processing_by_view.values() if isinstance(view, dict) and view.get("notes"))
        overall -= 0.08 * placeholder_count
        overall -= view_penalty
        return round(max(0.0, min(0.95, overall)), 3)

    @staticmethod
    def _build_summary(
        *,
        metrics: dict[str, dict[str, object]],
        confidence_overall: float,
        processing_by_view: dict[str, dict[str, object]],
    ) -> dict[str, object]:
        def metric(name: str) -> dict[str, object]:
            payload = metrics.get(name, {})
            return payload if isinstance(payload, dict) else {}

        left_calc = metric("calcaneal_angle_left").get("classification")
        right_calc = metric("calcaneal_angle_right").get("classification")
        left_prog = metric("foot_progression_angle_left").get("classification")
        right_prog = metric("foot_progression_angle_right").get("classification")
        left_arch = metric("arch_height_ratio_left").get("classification")
        right_arch = metric("arch_height_ratio_right").get("classification")
        left_arch_value = metric("arch_height_ratio_left").get("value")
        right_arch_value = metric("arch_height_ratio_right").get("value")

        rearfoot_pattern = "undetermined"
        if left_calc and right_calc:
            rearfoot_pattern = f"left_{left_calc}_right_{right_calc}"

        progression_pattern = "neutral"
        if left_prog == right_prog and left_prog not in {None, "neutral"}:
            progression_pattern = f"bilateral_{left_prog}"
        elif left_prog not in {None, "neutral"} and right_prog not in {None, "neutral"}:
            progression_pattern = f"left_{left_prog}_right_{right_prog}"
        elif left_prog not in {None, "neutral"}:
            progression_pattern = f"left_{left_prog}"
        elif right_prog not in {None, "neutral"}:
            progression_pattern = f"right_{right_prog}"

        arch_pattern = "undetermined"
        if left_arch and right_arch:
            if left_arch == right_arch and left_arch in {"low_arch", "normal_arch", "high_arch"}:
                arch_pattern = f"bilateral_{left_arch}"
            elif isinstance(left_arch_value, (int, float)) and isinstance(right_arch_value, (int, float)) and abs(left_arch_value - right_arch_value) >= 0.02:
                higher_side = "left" if left_arch_value > right_arch_value else "right"
                arch_pattern = f"asymmetry_{higher_side}_higher_arch"
            else:
                arch_pattern = f"left_{left_arch}_right_{right_arch}"

        summary_notes = sorted(
            {
                note
                for view_payload in processing_by_view.values()
                if isinstance(view_payload, dict)
                for note in view_payload.get("notes", [])
            }
        )
        return {
            "rearfoot_pattern": rearfoot_pattern,
            "foot_progression_pattern": progression_pattern,
            "arch_pattern": arch_pattern,
            "confidence_overall": confidence_overall,
            "quality_notes": summary_notes,
        }
