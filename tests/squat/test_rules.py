"""Tests for versioned interpretable squat rules."""

from __future__ import annotations

import json
from pathlib import Path

import pytest
from pydantic import ValidationError

from scripts.run_squat_analysis import DEFAULT_RULESET, build_parser
from src.squat.models import SquatRuleSet
from src.squat.rules import classify_squat_findings, load_squat_ruleset


def _write_rule_inputs(
    tmp_path: Path,
    *,
    case_id: str = "caso_001",
    eligible: bool = True,
    quality_status: str = "apto_para_analisis",
    trunk: tuple[float | None, ...] = (15.0, 16.0, 14.0),
    pelvis: tuple[float | None, ...] = (-10.0, -9.0, -11.0),
    left_knee: tuple[float | None, ...] = (7.0, 6.0, 8.0),
    right_knee: tuple[float | None, ...] = (-4.0, -3.0, -5.0),
    bilateral: tuple[float | None, ...] = (14.0, 13.0, 15.0),
) -> tuple[Path, Path]:
    biomechanics_path = tmp_path / "biomechanical_summary.json"
    quality_path = tmp_path / "quality_gate_summary.json"
    repetitions = []
    for index, values in enumerate(
        zip(trunk, pelvis, left_knee, right_knee, bilateral, strict=True),
        start=1,
    ):
        trunk_value, pelvis_value, left_value, right_value, difference = values
        repetitions.append(
            {
                "repetition_index": index,
                "peak_depth_frame": index * 100,
                "valid_frames_percentage": 100.0,
                "trunk_inclination_at_peak_deg": trunk_value,
                "trunk_max_abs_deg": abs(trunk_value) if trunk_value is not None else None,
                "trunk_max_abs_frame": index * 100,
                "pelvis_shift_at_peak_pct": pelvis_value,
                "pelvis_max_abs_shift_pct": (
                    abs(pelvis_value) if pelvis_value is not None else None
                ),
                "pelvis_max_abs_frame": index * 100,
                "left_knee_medial_deviation_at_peak_pct": left_value,
                "right_knee_medial_deviation_at_peak_pct": right_value,
                "left_knee_max_medial_deviation_pct": left_value,
                "right_knee_max_medial_deviation_pct": right_value,
                "bilateral_alignment_difference_at_peak_pct": difference,
                "bilateral_max_alignment_difference_pct": difference,
            }
        )
    biomechanics = {
        "schema_version": "1.0",
        "case_id": case_id,
        "stage": "variables_biomecanicas",
        "landmarks_csv": "landmarks.csv",
        "frame_phases_csv": "frame_phases.csv",
        "normalization_reference": "initial_shoulder_width",
        "initial_shoulder_width": 0.4,
        "valid_metric_frames": 300,
        "total_frames": 300,
        "repetitions": repetitions,
        "conventions": ["test"],
        "artifacts": {
            "frame_metrics_csv": "frame_metrics.csv",
            "repetition_metrics_csv": "repetition_metrics.csv",
            "metrics_plot": "metrics.png",
            "summary_json": str(biomechanics_path),
        },
    }
    quality = {
        "schema_version": "1.0",
        "case_id": case_id,
        "stage": "control_calidad_analitica",
        "status": quality_status,
        "eligible_for_analysis": eligible,
        "checks": [],
        "exclusion_reasons": [] if eligible else ["video rechazado"],
        "warnings": [],
        "artifacts": {"summary_json": str(quality_path)},
    }
    biomechanics_path.write_text(
        json.dumps(biomechanics),
        encoding="utf-8",
    )
    quality_path.write_text(json.dumps(quality), encoding="utf-8")
    return biomechanics_path, quality_path


def test_ruleset_contract_and_cli_default_are_versioned() -> None:
    ruleset = load_squat_ruleset(DEFAULT_RULESET)
    args = build_parser().parse_args(
        [
            "classify",
            "--case-id",
            "caso_001",
            "--biomechanics-summary-json",
            "biomechanics.json",
            "--quality-summary-json",
            "quality.json",
        ]
    )

    assert ruleset.ruleset_version == "0.2.0-provisional"
    assert ruleset.status == "provisional"
    assert args.ruleset == DEFAULT_RULESET


def test_classification_exports_multilabel_traceable_findings(tmp_path: Path) -> None:
    biomechanics, quality = _write_rule_inputs(tmp_path)

    result = classify_squat_findings(
        biomechanics,
        quality,
        DEFAULT_RULESET,
        case_id="caso_001",
        output_dir=tmp_path / "outputs",
    )

    assert len(result.decisions) == 12
    assert len(result.detected_findings) == 12
    decisions = {
        (decision.repetition_index, decision.finding): decision
        for decision in result.decisions
    }
    assert decisions[(1, "inclinacion_lateral_tronco")].direction == "izquierda"
    assert decisions[(1, "desplazamiento_lateral_pelvis")].direction == "derecha"
    assert decisions[(1, "valgo_dinamico_visible")].direction == "izquierda"
    assert (
        decisions[(1, "asimetria_bilateral_observable")].direction
        == "predominio_izquierdo"
    )
    assert Path(result.artifacts.rule_evidence_csv).exists()
    assert Path(result.artifacts.findings_json).exists()


def test_rules_preserve_inconclusive_band_and_missing_values(tmp_path: Path) -> None:
    biomechanics, quality = _write_rule_inputs(
        tmp_path,
        trunk=(10.0, 10.5, None),
        pelvis=(0.0, 0.5, -0.5),
        left_knee=(3.0, 3.5, None),
        right_knee=(-4.0, -3.0, None),
        bilateral=(9.0, 10.0, None),
    )

    result = classify_squat_findings(
        biomechanics,
        quality,
        DEFAULT_RULESET,
        case_id="caso_001",
        output_dir=tmp_path / "outputs",
    )

    decisions = {
        (decision.repetition_index, decision.finding): decision
        for decision in result.decisions
    }
    assert decisions[(1, "inclinacion_lateral_tronco")].status == "no_concluyente"
    assert decisions[(1, "desplazamiento_lateral_pelvis")].status == "ausente"
    assert decisions[(1, "valgo_dinamico_visible")].status == "no_concluyente"
    assert decisions[(1, "asimetria_bilateral_observable")].status == "no_concluyente"


def test_signed_rules_classify_each_repetition_independently(
    tmp_path: Path,
) -> None:
    biomechanics, quality = _write_rule_inputs(
        tmp_path,
        trunk=(15.0, -15.0, 0.0),
        pelvis=(10.0, -10.0, 0.0),
    )

    result = classify_squat_findings(
        biomechanics,
        quality,
        DEFAULT_RULESET,
        case_id="caso_001",
        output_dir=tmp_path / "outputs",
    )

    decisions = {
        (decision.repetition_index, decision.finding): decision
        for decision in result.decisions
    }
    assert decisions[(1, "inclinacion_lateral_tronco")].direction == "izquierda"
    assert decisions[(2, "inclinacion_lateral_tronco")].direction == "derecha"
    assert decisions[(3, "inclinacion_lateral_tronco")].status == "ausente"
    assert decisions[(1, "desplazamiento_lateral_pelvis")].direction == "izquierda"
    assert decisions[(2, "desplazamiento_lateral_pelvis")].direction == "derecha"
    assert decisions[(3, "desplazamiento_lateral_pelvis")].status == "ausente"


def test_valgus_rule_can_report_bilateral_presence(tmp_path: Path) -> None:
    biomechanics, quality = _write_rule_inputs(
        tmp_path,
        left_knee=(7.0, 8.0, 7.5),
        right_knee=(6.0, 7.0, 6.5),
    )

    result = classify_squat_findings(
        biomechanics,
        quality,
        DEFAULT_RULESET,
        case_id="caso_001",
        output_dir=tmp_path / "outputs",
    )

    valgus = next(
        decision
        for decision in result.decisions
        if decision.finding == "valgo_dinamico_visible"
    )
    assert valgus.status == "presente"
    assert valgus.direction == "bilateral"


def test_classification_rejects_ineligible_or_mismatched_cases(
    tmp_path: Path,
) -> None:
    biomechanics, quality = _write_rule_inputs(
        tmp_path,
        eligible=False,
        quality_status="no_apto_para_analisis",
    )
    with pytest.raises(ValueError, match="quality gate rejected"):
        classify_squat_findings(
            biomechanics,
            quality,
            DEFAULT_RULESET,
            case_id="caso_001",
            output_dir=tmp_path / "outputs",
        )

    biomechanics, quality = _write_rule_inputs(tmp_path, case_id="otro_caso")
    with pytest.raises(ValueError, match="case_id must match"):
        classify_squat_findings(
            biomechanics,
            quality,
            DEFAULT_RULESET,
            case_id="caso_001",
            output_dir=tmp_path / "outputs",
        )


def test_ruleset_rejects_missing_rules_and_overlapping_bands(
    tmp_path: Path,
) -> None:
    missing_path = tmp_path / "missing.json"
    missing_path.write_text(
        json.dumps(
            {
                "schema_version": "1.0",
                "ruleset_version": "test",
                "status": "provisional",
                "calibration_basis": [],
                "rules": {},
            }
        ),
        encoding="utf-8",
    )
    with pytest.raises(ValueError, match="missing required rules"):
        load_squat_ruleset(missing_path)

    with pytest.raises(ValidationError, match="absent_max must be lower"):
        SquatRuleSet.model_validate(
            {
                "ruleset_version": "test",
                "status": "provisional",
                "calibration_basis": [],
                "rules": {
                    "invalid": {
                        "metric": "x",
                        "absent_max": 5.0,
                        "present_min": 5.0,
                        "unit": "x",
                    }
                },
            }
        )
