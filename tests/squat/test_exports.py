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
        case_record={"registration": {"case": {"case_id": "caso_export_001"}}},
        case_report={"case_id": "caso_export_001", "status": "analisis_completo"},
        comparison=_comparison(),
        performance=_performance(),
    )

    workbook = load_workbook(BytesIO(content))
    assert workbook.sheetnames == [
        "Instrumento 1",
        "Instrumento 2",
        "Instrumento 3",
        "Matriz de análisis",
        "Métricas",
    ]
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
