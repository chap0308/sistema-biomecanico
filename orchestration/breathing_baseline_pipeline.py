"""Breathing baseline pipeline integrated into the mandatory rest baseline."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import tempfile

from biomechanics.specialty_metrics import (
    IsaMeasurement,
    RibFlareStaticMeasurement,
    ThoracicAbdominalFrameMeasurement,
    compute_infra_sternal_angle_placeholder,
    compute_rib_flare_dynamic_metrics,
    compute_thoracic_abdominal_dynamic_metrics,
    estimate_static_infrasternal_angle,
    estimate_static_rib_flare,
    estimate_thoracic_abdominal_frame,
    summarize_dynamic_infrasternal_angle,
)
from orchestration.rest_temporal import sample_indexed_video_frames
from pose.mediapipe_pose import MediaPipePoseExtractor, PoseExtractionError


@dataclass(slots=True)
class BreathingBaselinePipeline:
    """Analyze the mandatory breathing video for thoracic-baseline integration."""

    pose_extractor: MediaPipePoseExtractor
    pipeline_version: str = "breathing-baseline-v1"

    def analyze_video_bytes(
        self,
        video_bytes: bytes,
        *,
        filename: str,
        include_placeholders: bool,
        aggregation: str,
        frame_step: int,
        max_frames: int,
        reject_outliers: bool,
    ) -> dict[str, object]:
        """Persist the upload temporarily and analyze it as the breathing baseline block."""
        suffix = Path(filename).suffix or ".mp4"
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp_file:
            tmp_file.write(video_bytes)
            tmp_path = Path(tmp_file.name)
        try:
            return self.analyze_video_path(
                tmp_path,
                include_placeholders=include_placeholders,
                aggregation=aggregation,
                frame_step=frame_step,
                max_frames=max_frames,
                reject_outliers=reject_outliers,
            )
        finally:
            tmp_path.unlink(missing_ok=True)

    def analyze_video_path(
        self,
        video_path: str | Path,
        *,
        include_placeholders: bool,
        aggregation: str,
        frame_step: int,
        max_frames: int,
        reject_outliers: bool,
    ) -> dict[str, object]:
        """Analyze a breathing video and summarize dynamic thoracic metrics over sampled frames."""
        indexed_frames = sample_indexed_video_frames(Path(video_path), max_frames=max_frames, frame_step=frame_step)
        if not indexed_frames:
            raise PoseExtractionError(f"No readable frames were sampled from video: {video_path}")

        successful_frames = []
        isa_frame_measurements: list[IsaMeasurement] = []
        rib_frame_measurements: list[RibFlareStaticMeasurement] = []
        thoracic_abdominal_frame_measurements: list[ThoracicAbdominalFrameMeasurement] = []
        failures = 0
        last_error: Exception | None = None
        for sampled_frame_index, frame in indexed_frames:
            try:
                pose_result = self.pose_extractor.extract_from_image_array(frame)
                successful_frames.append(pose_result)

                isa_measurement = estimate_static_infrasternal_angle(frame, pose_result=pose_result)
                isa_measurement.frame_index = sampled_frame_index
                isa_frame_measurements.append(isa_measurement)

                rib_measurement = estimate_static_rib_flare(frame, pose_result=pose_result)
                rib_measurement.frame_index = sampled_frame_index
                rib_frame_measurements.append(rib_measurement)

                thoracic_abdominal_measurement = estimate_thoracic_abdominal_frame(
                    frame,
                    pose_result=pose_result,
                    isa_measurement=isa_measurement,
                )
                thoracic_abdominal_measurement.frame_index = sampled_frame_index
                thoracic_abdominal_frame_measurements.append(thoracic_abdominal_measurement)
            except PoseExtractionError as exc:
                failures += 1
                last_error = exc

        if not successful_frames:
            if last_error is not None:
                raise PoseExtractionError(str(last_error)) from last_error
            raise PoseExtractionError("No valid pose detections were produced from the breathing video.")

        isa_summary = summarize_dynamic_infrasternal_angle(
            isa_frame_measurements,
            total_frame_count=len(indexed_frames),
            reject_outliers=reject_outliers,
        )
        rib_summary = compute_rib_flare_dynamic_metrics(
            rib_frame_measurements,
            total_frame_count=len(indexed_frames),
            reject_outliers=reject_outliers,
        )
        thoracic_abdominal_summary = compute_thoracic_abdominal_dynamic_metrics(
            thoracic_abdominal_frame_measurements,
            total_frame_count=len(indexed_frames),
            reject_outliers=reject_outliers,
        )
        metadata = successful_frames[0].metadata
        notes = [
            "Static thoracic metrics remain structural references while the breathing video provides the functional thoracic excursion.",
            *isa_summary.quality_notes,
            *[note for note in rib_summary.quality_notes if note not in isa_summary.quality_notes],
            *[
                note
                for note in thoracic_abdominal_summary.quality_notes
                if note not in isa_summary.quality_notes and note not in rib_summary.quality_notes
            ],
        ]
        metrics = self._build_dynamic_metrics(
            isa_summary,
            rib_summary,
            thoracic_abdominal_summary,
            include_placeholders=include_placeholders,
        )
        time_series = self._build_time_series(
            isa_measurements=isa_frame_measurements,
            rib_measurements=rib_frame_measurements,
            thoracic_abdominal_measurements=thoracic_abdominal_frame_measurements,
        )
        key_frames = self._build_key_frames(
            isa_summary=isa_summary,
            rib_summary=rib_summary,
            thoracic_abdominal_summary=thoracic_abdominal_summary,
        )
        ready_for_clinical_decision = isa_summary.dynamic_delta is not None and isa_summary.confidence >= 0.55
        thoracic_state = "dynamic_isa_available" if ready_for_clinical_decision else "dynamic_isa_low_confidence"
        return {
            "status": "success",
            "pose": {
                "detected": True,
                "detector": metadata.detector,
                "image_width": metadata.image_width,
                "image_height": metadata.image_height,
                "landmark_count": metadata.landmark_count,
                "relevant_landmark_count": metadata.relevant_landmark_count,
                "min_visibility": min(result.metadata.min_visibility for result in successful_frames),
                "input_frame_count": len(indexed_frames),
                "successful_frame_count": len(successful_frames),
                "failed_frame_count": failures,
                "aggregation": aggregation,
                "outlier_rejection": reject_outliers,
                "notes": notes,
            },
            "metrics": metrics,
            "signals": {
                "thoracic_state": thoracic_state,
                "isa_source_of_truth": "breathing_video",
                "static_isa_role": "reference_only",
                "ready_for_clinical_decision": ready_for_clinical_decision,
                "confidence": isa_summary.confidence,
                "rib_flare_confidence": rib_summary.confidence,
                "thoracic_abdominal_confidence": thoracic_abdominal_summary.confidence,
                "valid_frame_count": isa_summary.valid_frame_count,
                "total_frame_count": isa_summary.total_frame_count,
                "notes": notes,
            },
            "time_series": time_series,
            "key_frames": key_frames,
        }

    def _build_dynamic_metrics(
        self,
        isa_summary,
        rib_summary,
        thoracic_abdominal_summary,
        *,
        include_placeholders: bool,
    ) -> dict[str, object]:
        return {
            "isa": self._serialize_dynamic_isa_metrics(isa_summary, include_placeholders=include_placeholders),
            "rib_flare": self._serialize_dynamic_rib_flare_metrics(
                rib_summary,
                include_placeholders=include_placeholders,
            ),
            "thoracic_abdominal": self._serialize_dynamic_thoracic_abdominal_metrics(
                thoracic_abdominal_summary,
                include_placeholders=include_placeholders,
            ),
        }

    def _serialize_dynamic_isa_metrics(self, summary, *, include_placeholders: bool) -> dict[str, dict[str, object]]:
        metrics: dict[str, dict[str, object]] = {}
        if summary.max_inhalation is not None or include_placeholders:
            metrics["max_inhalation"] = self._serialize_dynamic_metric(
                name="isa_max_inhalation",
                measurement=summary.max_inhalation,
                summary=summary,
            )
        if summary.min_exhalation is not None or include_placeholders:
            metrics["min_exhalation"] = self._serialize_dynamic_metric(
                name="isa_min_exhalation",
                measurement=summary.min_exhalation,
                summary=summary,
            )
        if summary.dynamic_delta is not None or include_placeholders:
            metrics["dynamic_delta"] = self._serialize_dynamic_delta(summary)
        return metrics

    def _serialize_dynamic_metric(self, *, name: str, measurement, summary) -> dict[str, object]:
        placeholder = compute_infra_sternal_angle_placeholder(name=name)
        if measurement is None or measurement.angle_degrees is None:
            return {
                "name": placeholder.name,
                "value": None,
                "plane": placeholder.plane,
                "unit": placeholder.unit,
                "measurement_type": "specialty_metric",
                "priority": placeholder.priority,
                "status": "placeholder",
                "notes": summary.quality_notes,
                "confidence": summary.confidence,
                "quality_notes": summary.quality_notes,
                "landmarks": None,
                "frame_index": None,
            }
        payload = {
            "name": name,
            "value": measurement.angle_degrees,
            "plane": placeholder.plane,
            "unit": placeholder.unit,
            "measurement_type": "specialty_metric",
            "priority": placeholder.priority,
            "status": measurement.status,
            "notes": measurement.quality_notes,
            "confidence": summary.confidence,
            "quality_notes": measurement.quality_notes,
            "landmarks": None,
            "frame_index": measurement.frame_index,
        }
        if measurement.landmarks is not None:
            payload["landmarks"] = self._serialize_landmarks(measurement.landmarks)
        return payload

    def _serialize_dynamic_delta(self, summary) -> dict[str, object]:
        placeholder = compute_infra_sternal_angle_placeholder(name="isa_dynamic_delta")
        if summary.dynamic_delta is None:
            return {
                "name": placeholder.name,
                "value": None,
                "plane": placeholder.plane,
                "unit": placeholder.unit,
                "measurement_type": "specialty_metric",
                "priority": placeholder.priority,
                "status": "placeholder",
                "notes": summary.quality_notes,
                "confidence": summary.confidence,
                "quality_notes": summary.quality_notes,
                "landmarks": None,
                "frame_index": None,
            }
        return {
            "name": "isa_dynamic_delta",
            "value": summary.dynamic_delta,
            "plane": placeholder.plane,
            "unit": placeholder.unit,
            "measurement_type": "specialty_metric",
            "priority": placeholder.priority,
            "status": "computed" if summary.confidence >= 0.55 else "low_confidence",
            "notes": summary.quality_notes,
            "confidence": summary.confidence,
            "quality_notes": summary.quality_notes,
            "landmarks": None,
            "frame_index": None,
        }

    def _serialize_dynamic_rib_flare_metrics(self, summary, *, include_placeholders: bool) -> dict[str, dict[str, object]]:
        metrics: dict[str, dict[str, object]] = {}
        definitions = {
            "dynamic_asymmetry": ("rib_flare_dynamic_asymmetry", summary.dynamic_asymmetry, "score"),
            "excursion_left": ("rib_flare_excursion_left", summary.excursion_left, "score"),
            "excursion_right": ("rib_flare_excursion_right", summary.excursion_right, "score"),
            "persistence_exhalation": ("rib_flare_persistence_exhalation", summary.persistence_exhalation, "score"),
        }
        for output_name, (metric_name, value, unit) in definitions.items():
            if value is None and not include_placeholders:
                continue
            metrics[output_name] = {
                "name": metric_name,
                "value": value,
                "plane": "frontal",
                "unit": unit,
                "measurement_type": "specialty_metric",
                "priority": "P1",
                "status": ("computed" if summary.confidence >= 0.55 else "low_confidence") if value is not None else "placeholder",
                "notes": summary.quality_notes,
                "confidence": summary.confidence,
                "quality_notes": summary.quality_notes,
                "landmarks": None,
                "frame_index": summary.exhalation_frame_index if output_name == "persistence_exhalation" else None,
            }

        return metrics

    def _serialize_dynamic_thoracic_abdominal_metrics(self, summary, *, include_placeholders: bool) -> dict[str, dict[str, object]]:
        metrics: dict[str, dict[str, object]] = {}
        definitions = {
            "dissociation_score": ("thoracic_abdominal_dissociation_score", summary.dissociation_score, "score"),
            "phase_offset": ("thoracic_abdominal_phase_offset", summary.phase_offset, "ratio"),
            "amplitude_ratio": ("thoracic_abdominal_amplitude_ratio", summary.amplitude_ratio, "ratio"),
            "exhalation_mismatch": ("thoracic_abdominal_exhalation_mismatch", summary.exhalation_mismatch, "score"),
            "upper_abdominal_excursion": ("upper_abdominal_excursion", summary.upper_abdominal_excursion, "ratio"),
            "lower_thoracic_excursion": ("lower_thoracic_excursion", summary.lower_thoracic_excursion, "ratio"),
        }
        for output_name, (metric_name, value, unit) in definitions.items():
            if value is None and not include_placeholders:
                continue
            metrics[output_name] = {
                "name": metric_name,
                "value": value,
                "plane": "frontal",
                "unit": unit,
                "measurement_type": "specialty_metric" if value is not None else "placeholder",
                "priority": "P1",
                "status": ("computed" if summary.confidence >= 0.55 else "low_confidence") if value is not None else "placeholder",
                "notes": summary.quality_notes,
                "confidence": summary.confidence if value is not None else 0.0,
                "quality_notes": summary.quality_notes,
                "landmarks": None,
                "frame_index": summary.exhalation_frame_index if output_name == "exhalation_mismatch" else None,
            }
        return metrics

    def _build_time_series(
        self,
        *,
        isa_measurements: list[IsaMeasurement],
        rib_measurements: list[RibFlareStaticMeasurement],
        thoracic_abdominal_measurements: list[ThoracicAbdominalFrameMeasurement],
    ) -> list[dict[str, object]]:
        series_by_frame: dict[int, dict[str, object]] = {}

        for measurement in isa_measurements:
            if measurement.frame_index is None:
                continue
            entry = series_by_frame.setdefault(measurement.frame_index, {"frame_index": measurement.frame_index})
            entry["isa"] = measurement.angle_degrees
            entry["isa_status"] = measurement.status
            entry["isa_confidence"] = measurement.confidence
            entry["landmarks"] = self._serialize_landmarks(measurement.landmarks) if measurement.landmarks is not None else None

        for measurement in rib_measurements:
            if measurement.frame_index is None:
                continue
            entry = series_by_frame.setdefault(measurement.frame_index, {"frame_index": measurement.frame_index})
            entry["rib_flare_score"] = measurement.rib_flare_presence_score
            entry["left_costal_margin_angle"] = measurement.left_costal_margin_angle
            entry["right_costal_margin_angle"] = measurement.right_costal_margin_angle
            entry["costal_projection_index"] = measurement.costal_projection_index
            entry["rib_flare_status"] = measurement.status
            entry["rib_flare_confidence"] = measurement.confidence
            if entry.get("landmarks") is None and measurement.landmarks is not None:
                entry["landmarks"] = self._serialize_landmarks(measurement.landmarks)

        thoracic_values = [
            float(measurement.thoracic_width_proxy)
            for measurement in thoracic_abdominal_measurements
            if measurement.thoracic_width_proxy is not None
        ]
        abdominal_values = [
            float(measurement.upper_abdominal_width_proxy)
            for measurement in thoracic_abdominal_measurements
            if measurement.upper_abdominal_width_proxy is not None
        ]
        thoracic_min = min(thoracic_values) if thoracic_values else None
        thoracic_range = (max(thoracic_values) - thoracic_min) if thoracic_values and thoracic_min is not None else None
        abdominal_min = min(abdominal_values) if abdominal_values else None
        abdominal_range = (max(abdominal_values) - abdominal_min) if abdominal_values and abdominal_min is not None else None

        for measurement in thoracic_abdominal_measurements:
            if measurement.frame_index is None:
                continue
            entry = series_by_frame.setdefault(measurement.frame_index, {"frame_index": measurement.frame_index})
            entry["lower_thoracic_width_proxy"] = measurement.thoracic_width_proxy
            entry["upper_abdominal_width_proxy"] = measurement.upper_abdominal_width_proxy
            thoracic_signal = self._normalize_signal(measurement.thoracic_width_proxy, thoracic_min, thoracic_range)
            abdominal_signal = self._normalize_signal(measurement.upper_abdominal_width_proxy, abdominal_min, abdominal_range)
            entry["lower_thoracic_excursion"] = thoracic_signal
            entry["upper_abdominal_excursion"] = abdominal_signal
            entry["thoracic_abdominal_dissociation"] = (
                abs(thoracic_signal - abdominal_signal)
                if thoracic_signal is not None and abdominal_signal is not None
                else None
            )
            entry["thoracic_abdominal_status"] = measurement.status
            entry["thoracic_abdominal_confidence"] = measurement.confidence

        return [series_by_frame[index] for index in sorted(series_by_frame)]

    def _build_key_frames(self, *, isa_summary, rib_summary, thoracic_abdominal_summary) -> dict[str, int | None]:
        return {
            "max_inhalation_frame": isa_summary.max_inhalation.frame_index if isa_summary.max_inhalation is not None else None,
            "max_exhalation_frame": isa_summary.min_exhalation.frame_index if isa_summary.min_exhalation is not None else thoracic_abdominal_summary.exhalation_frame_index,
            "rib_flare_persistence_frame": rib_summary.exhalation_frame_index,
            "thoracic_abdominal_exhalation_frame": thoracic_abdominal_summary.exhalation_frame_index,
        }

    def _normalize_signal(
        self,
        value: float | None,
        minimum: float | None,
        value_range: float | None,
    ) -> float | None:
        if value is None or minimum is None or value_range is None:
            return None
        if value_range <= 1e-6:
            return 0.0
        return float((value - minimum) / value_range)

    def _serialize_landmarks(self, landmarks) -> dict[str, object]:
        if landmarks is None:
            return None
        return {
            "left_costal_margin": {
                "x": landmarks.left_costal_margin.x,
                "y": landmarks.left_costal_margin.y,
            },
            "substernal_vertex": {
                "x": landmarks.substernal_vertex.x,
                "y": landmarks.substernal_vertex.y,
            },
            "right_costal_margin": {
                "x": landmarks.right_costal_margin.x,
                "y": landmarks.right_costal_margin.y,
            },
        }
