"""Research-ready Excel and PDF exports for squat comparisons."""

from __future__ import annotations

from io import BytesIO
from typing import Any, Iterable

from matplotlib.backends.backend_pdf import PdfPages
import matplotlib.pyplot as plt
from openpyxl import Workbook
from openpyxl.styles import Alignment, Font, PatternFill
from openpyxl.utils import get_column_letter

from src.squat.comparison import (
    CaseComparison,
    DatasetPerformance,
    PatternComparison,
)

_PATTERN_NAMES = {
    "trunk_lateral_inclination": "Inclinación lateral del tronco",
    "pelvis_lateral_shift": "Desplazamiento lateral de pelvis",
    "visible_dynamic_valgus": "Valgo dinámico visible",
    "bilateral_asymmetry": "Asimetría bilateral observable",
}


def build_case_excel(
    *,
    case_record: dict[str, Any],
    case_report: dict[str, Any],
    comparison: CaseComparison,
    performance: DatasetPerformance,
) -> bytes:
    """Create one workbook containing Instruments 1-3 and derived analysis."""
    workbook = Workbook()
    default = workbook.active
    workbook.remove(default)
    _instrument_1_sheet(workbook, case_record)
    _instrument_2_sheet(workbook, case_report)
    _instrument_3_sheet(workbook, comparison)
    _analysis_sheet(workbook, comparison.patterns)
    _metrics_sheet(workbook, performance)
    for sheet in workbook.worksheets:
        _format_sheet(sheet)
    output = BytesIO()
    workbook.save(output)
    return output.getvalue()


def build_case_pdf(
    *,
    case_report: dict[str, Any],
    comparison: CaseComparison,
    performance: DatasetPerformance,
) -> bytes:
    """Create a concise investigator report without clinical diagnoses."""
    output = BytesIO()
    with PdfPages(output) as pdf:
        figure = plt.figure(figsize=(8.27, 11.69))
        figure.patch.set_facecolor("#f8f5ec")
        figure.text(
            0.08,
            0.93,
            "Evaluación de sentadilla bilateral",
            fontsize=20,
            fontweight="bold",
            color="#123b42",
        )
        figure.text(
            0.08,
            0.89,
            f"Caso: {comparison.case_id}",
            fontsize=11,
            color="#334155",
        )
        figure.text(
            0.08,
            0.86,
            (
                f"Pipeline: {case_report.get('pipeline_version', 'N/D')} | "
                f"Evaluaciones enviadas: {comparison.submitted_evaluations}"
            ),
            fontsize=9,
            color="#64748b",
        )
        table_rows = [
            [
                f"R{row.repetition_index} · {_PATTERN_NAMES[row.pattern_key]}",
                _label(row.reference.label if row.reference else None),
                _label(row.system_label),
                _match_label(row.exact_match),
            ]
            for row in comparison.patterns
        ]
        axis = figure.add_axes((0.07, 0.47, 0.86, 0.32))
        axis.axis("off")
        table = axis.table(
            cellText=table_rows,
            colLabels=[
                "Patrón",
                "Referencia experta",
                "Sistema",
                "Coincidencia",
            ],
            cellLoc="left",
            colLoc="left",
            loc="upper left",
            colWidths=[0.36, 0.24, 0.24, 0.16],
        )
        table.auto_set_font_size(False)
        table.set_fontsize(8)
        table.scale(1, 1.8)
        metrics = performance.overall
        metric_text = (
            "Desempeño acumulado del conjunto\n"
            f"Pares incluidos: {metrics.included_pairs}\n"
            f"Exactitud: {_percent(metrics.accuracy)}\n"
            f"Precisión: {_percent(metrics.precision)}\n"
            f"Sensibilidad: {_percent(metrics.sensitivity)}\n"
            f"Especificidad: {_percent(metrics.specificity)}\n"
            f"F1-score: {_decimal(metrics.f1_score)}\n"
            f"Kappa de Cohen: {_decimal(metrics.cohen_kappa)}\n"
            f"Pares no concluyentes excluidos: "
            f"{metrics.excluded_inconclusive_pairs}"
        )
        figure.text(
            0.08,
            0.37,
            metric_text,
            fontsize=10,
            linespacing=1.45,
            color="#1e293b",
        )
        figure.text(
            0.08,
            0.12,
            (
                "Este reporte describe compensaciones observables durante la "
                "sentadilla y no constituye un diagnóstico clínico. "
                "Los pares no concluyentes no se incluyen en las métricas."
            ),
            fontsize=8,
            color="#64748b",
            wrap=True,
        )
        pdf.savefig(figure, bbox_inches="tight")
        plt.close(figure)
    return output.getvalue()


def _instrument_1_sheet(workbook: Workbook, record: dict[str, Any]) -> None:
    sheet = workbook.create_sheet("Instrumento 1")
    sheet.append(["Campo", "Valor registrado"])
    for key, value in _flatten(record):
        sheet.append([key, _cell(value)])


def _instrument_2_sheet(workbook: Workbook, report: dict[str, Any]) -> None:
    sheet = workbook.create_sheet("Instrumento 2")
    pose = report.get("pose") or {}
    findings = report.get("findings") or {}
    decisions = findings.get("decisions") or []
    headers = [
        "Código del video",
        "Estado",
        "Fotogramas totales",
        "Fotogramas válidos",
        "% fotogramas válidos",
        "% procesados correctamente",
        "Promedio de puntos clave por fotograma",
        "Reglas implementadas",
        "Compensaciones detectadas",
        "Versión de reglas",
    ]
    sheet.append(headers)
    sheet.append(
        [
            report.get("case_id"),
            report.get("status"),
            pose.get("total_frames"),
            pose.get("valid_frames"),
            pose.get("valid_frames_percentage"),
            pose.get("processed_frames_percentage"),
            pose.get("mean_detected_keypoints"),
            len(decisions),
            ", ".join(findings.get("detected_findings") or []),
            findings.get("ruleset_version"),
        ]
    )
    sheet.append([])
    sheet.append(
        [
            "Patrón",
            "Repetición",
            "Estado del sistema",
            "Dirección",
            "Valor agregado",
            "Unidad",
            "Umbral ausente",
            "Umbral presente",
        ]
    )
    for decision in decisions:
        sheet.append(
            [
                decision.get("finding"),
                decision.get("repetition_index"),
                decision.get("status"),
                decision.get("direction"),
                decision.get("aggregate_value"),
                decision.get("unit"),
                decision.get("absent_max"),
                decision.get("present_min"),
            ]
        )


def _instrument_3_sheet(
    workbook: Workbook,
    comparison: CaseComparison,
) -> None:
    sheet = workbook.create_sheet("Instrumento 3")
    sheet.append(
        [
            "Código del video",
            "Ejecución",
            "Patrón",
            "Evaluador 1",
            "Evaluador 2",
            "Evaluador 3",
            "Sistema",
            "Referencia final",
            "Método de consolidación",
        ]
    )
    for row in comparison.patterns:
        expert_labels = [
            _judgment_label(
                judgment.classification,
                judgment.observed_side,
                row.pattern_key,
            )
            for judgment in row.expert_judgments
        ]
        expert_labels.extend([""] * (3 - len(expert_labels)))
        sheet.append(
            [
                comparison.case_id,
                f"{comparison.case_id}-repeticion-{row.repetition_index}",
                _PATTERN_NAMES[row.pattern_key],
                *expert_labels[:3],
                _label(row.system_label),
                _label(row.reference.label if row.reference else None),
                (
                    row.reference.method
                    if row.reference
                    else row.reference_status
                ),
            ]
        )


def _analysis_sheet(
    workbook: Workbook,
    rows: Iterable[PatternComparison],
) -> None:
    sheet = workbook.create_sheet("Matriz de análisis")
    sheet.append(
        [
            "Ejecución",
            "Patrón",
            "Referencia final",
            "Salida del sistema",
            "Coincidencia exacta",
            "Resultado binario",
            "Observación",
        ]
    )
    for row in rows:
        sheet.append(
            [
                f"repeticion-{row.repetition_index}",
                _PATTERN_NAMES[row.pattern_key],
                _label(row.reference.label if row.reference else None),
                _label(row.system_label),
                _match_label(row.exact_match),
                row.binary_outcome or "No calculable",
                (
                    "Par excluido por estado no concluyente"
                    if row.reference
                    and (
                        row.reference.classification == "no_concluyente"
                        or row.system_classification == "no_concluyente"
                    )
                    else row.reference_status
                ),
            ]
        )


def _metrics_sheet(
    workbook: Workbook,
    performance: DatasetPerformance,
) -> None:
    sheet = workbook.create_sheet("Métricas")
    sheet.append(
        [
            "Ámbito",
            "Pares incluidos",
            "Excluidos",
            "VP",
            "VN",
            "FP",
            "FN",
            "Exactitud",
            "Precisión",
            "Sensibilidad",
            "Especificidad",
            "F1-score",
            "Acuerdo exacto",
            "Kappa",
        ]
    )
    for metric in [performance.overall, *performance.by_pattern]:
        sheet.append(
            [
                metric.scope,
                metric.included_pairs,
                metric.excluded_inconclusive_pairs,
                metric.true_positive,
                metric.true_negative,
                metric.false_positive,
                metric.false_negative,
                metric.accuracy,
                metric.precision,
                metric.sensitivity,
                metric.specificity,
                metric.f1_score,
                metric.exact_agreement,
                metric.cohen_kappa,
            ]
        )


def _format_sheet(sheet: Any) -> None:
    header_fill = PatternFill("solid", fgColor="123B42")
    for cell in sheet[1]:
        cell.font = Font(color="FFFFFF", bold=True)
        cell.fill = header_fill
        cell.alignment = Alignment(wrap_text=True, vertical="center")
    sheet.freeze_panes = "A2"
    sheet.auto_filter.ref = sheet.dimensions
    for column in range(1, sheet.max_column + 1):
        width = max(
            len(str(sheet.cell(row=row, column=column).value or ""))
            for row in range(1, sheet.max_row + 1)
        )
        sheet.column_dimensions[get_column_letter(column)].width = min(
            max(width + 2, 12),
            42,
        )
    for row in sheet.iter_rows():
        for cell in row:
            cell.alignment = Alignment(wrap_text=True, vertical="top")


def _flatten(
    payload: dict[str, Any],
    prefix: str = "",
) -> Iterable[tuple[str, Any]]:
    for key, value in payload.items():
        path = f"{prefix}.{key}" if prefix else key
        if isinstance(value, dict):
            yield from _flatten(value, path)
        else:
            yield path, value


def _cell(value: Any) -> Any:
    if isinstance(value, list):
        return ", ".join(str(item) for item in value)
    return value


def _judgment_label(
    classification: str,
    side: str | None,
    pattern_key: str,
) -> str:
    if classification != "presente":
        return _label(classification)
    if pattern_key == "bilateral_asymmetry":
        return "Presente"
    return _label(f"presente_{side or 'sin_direccion'}")


def _label(value: str | None) -> str:
    if value is None:
        return "Pendiente"
    return value.replace("_", " ").capitalize()


def _match_label(value: bool | None) -> str:
    if value is None:
        return "No calculable"
    return "Sí" if value else "No"


def _percent(value: float | None) -> str:
    return f"{value * 100:.1f} %" if value is not None else "N/D"


def _decimal(value: float | None) -> str:
    return f"{value:.3f}" if value is not None else "N/D"


__all__ = ["build_case_excel", "build_case_pdf"]
