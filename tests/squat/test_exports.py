"""Tests for researcher-facing Excel and PDF exports."""

from io import BytesIO

from openpyxl import load_workbook

from src.squat.comparison import (
    CaseComparison,
    DatasetPerformance,
    PerformanceMetrics,
    build_case_comparisons,
)
from src.squat.exports import build_case_excel, build_case_pdf


def _comparison() -> CaseComparison:
    rows = build_case_comparisons(
        judgments=[],
        system_decisions=[],
    )
    return CaseComparison(
        case_id="caso_export_001",
        assigned_evaluators=2,
        submitted_evaluations=0,
        patterns=rows,
        ready_for_metrics=False,
    )


def _performance() -> DatasetPerformance:
    empty = PerformanceMetrics(
        scope="general",
        included_pairs=0,
        excluded_inconclusive_pairs=4,
        true_positive=0,
        true_negative=0,
        false_positive=0,
        false_negative=0,
    )
    return DatasetPerformance(
        consolidated_cases=0,
        pending_cases=1,
        overall=empty,
        by_pattern=[],
    )


def test_excel_contains_instruments_and_analysis_sheets() -> None:
    content = build_case_excel(
        case_record={
            "created_at": "2026-07-29T08:45:46.624700Z",
            "registration": {
                "case": {
                    "case_id": "caso_export_001",
                    "participant_code": "P-001",
                    "participant_age": 28,
                    "participant_sex": "femenino",
                    "view": "anterior",
                    "plane": "frontal",
                    "load_condition": "sin_carga_externa",
                },
                "video": {
                    "path": "video.mp4",
                    "width_px": 1080,
                    "height_px": 1920,
                    "fps": 30,
                },
                "ready_for_pose": True,
            },
        },
        case_report={"case_id": "caso_export_001", "status": "analisis_completo"},
        comparison=_comparison(),
        performance=_performance(),
        landmark_visibility=[
            {
                "repetition_index": 1,
                "landmark": "left_hip",
                "anatomical_group": "hip",
                "side": "izquierda",
                "mean_visibility": 0.92,
                "usable_frames_percentage": 100,
                "availability": "visible_estable",
            },
            {
                "repetition_index": 1,
                "landmark": "right_hip",
                "anatomical_group": "hip",
                "side": "derecha",
                "mean_visibility": 0.88,
                "usable_frames_percentage": 95,
                "availability": "visible_estable",
            },
        ],
    )

    workbook = load_workbook(BytesIO(content))
    assert workbook.sheetnames == [
        "Instrumento 1",
        "Instrumento 2",
        "Instrumento 3",
        "Matriz de análisis",
        "Métricas",
    ]
    instrument_1 = workbook["Instrumento 1"]
    assert instrument_1["A2"].value == "Código del video"
    assert instrument_1["B2"].value == "caso_export_001"
    assert instrument_1["B4"].value == 28
    assert instrument_1["B5"].value == "Femenino"
    assert instrument_1["B14"].value == "1080 × 1920 px"
    assert instrument_1["B15"].value == "30 fps"
    assert not any(
        str(cell.value).startswith("registration.")
        for row in instrument_1.iter_rows()
        for cell in row
        if cell.value
    )
    assert any(
        cell.value == "Cadera"
        for row in instrument_1.iter_rows()
        for cell in row
    )
    assert workbook["Instrumento 3"]["A2"].value == "caso_export_001"


def test_pdf_export_has_a_valid_header() -> None:
    content = build_case_pdf(
        case_report={
            "case_id": "caso_export_001",
            "pipeline_version": "test",
        },
        comparison=_comparison(),
        performance=_performance(),
    )

    assert content.startswith(b"%PDF")
    assert len(content) > 1_000
    assert content.count(b"/Type /Page") >= 3
