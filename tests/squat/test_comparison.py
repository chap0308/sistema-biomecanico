"""Tests for expert consolidation and performance metrics."""

from src.squat.comparison import (
    ExpertJudgment,
    FinalReference,
    build_case_comparisons,
    calculate_fleiss_kappa,
    calculate_metrics,
)


def _judgment(
    evaluator_id: str,
    pattern_key: str,
    classification: str,
    side: str | None = None,
    repetition_index: int = 1,
) -> ExpertJudgment:
    return ExpertJudgment(
        evaluator_id=evaluator_id,
        repetition_index=repetition_index,
        pattern_key=pattern_key,
        classification=classification,
        observed_side=side,
        confidence="alta",
    )


def test_two_matching_experts_create_direct_reference() -> None:
    rows = build_case_comparisons(
        judgments=[
            _judgment(
                "e1",
                "visible_dynamic_valgus",
                "presente",
                "izquierda",
            ),
            _judgment(
                "e2",
                "visible_dynamic_valgus",
                "presente",
                "izquierda",
            ),
        ],
        system_decisions=[
            {
                "finding": "valgo_dinamico_visible",
                "status": "presente",
                "direction": "izquierda",
            }
        ],
    )

    valgus = next(
        row for row in rows if row.pattern_key == "visible_dynamic_valgus"
    )
    assert valgus.reference is not None
    assert valgus.reference.method == "coincidencia_directa"
    assert valgus.exact_match is True
    assert valgus.binary_outcome == "TP"


def test_disagreement_requires_manual_consensus() -> None:
    rows = build_case_comparisons(
        judgments=[
            _judgment(
                "e1",
                "pelvis_lateral_shift",
                "presente",
                "izquierda",
            ),
            _judgment("e2", "pelvis_lateral_shift", "ausente"),
        ],
        system_decisions=[],
    )

    pelvis = next(
        row for row in rows if row.pattern_key == "pelvis_lateral_shift"
    )
    assert pelvis.reference is None
    assert pelvis.reference_status == "consenso_requerido"


def test_three_experts_use_absolute_majority() -> None:
    rows = build_case_comparisons(
        judgments=[
            _judgment("e1", "bilateral_asymmetry", "presente", "izquierda"),
            _judgment("e2", "bilateral_asymmetry", "presente", "derecha"),
            _judgment("e3", "bilateral_asymmetry", "ausente"),
        ],
        system_decisions=[],
    )

    asymmetry = next(
        row for row in rows if row.pattern_key == "bilateral_asymmetry"
    )
    assert asymmetry.reference is not None
    assert asymmetry.reference.method == "mayoria_absoluta"
    assert asymmetry.reference.label == "presente"


def test_manual_consensus_resolves_disagreement() -> None:
    rows = build_case_comparisons(
        judgments=[
            _judgment("e1", "trunk_lateral_inclination", "ausente"),
            _judgment(
                "e2",
                "trunk_lateral_inclination",
                "presente",
                "derecha",
            ),
        ],
        system_decisions=[],
        manual_references={
            "trunk_lateral_inclination": FinalReference(
                classification="ausente",
                method="consenso_guiado",
                observation="Revisión conjunta del video.",
            )
        },
    )

    trunk = rows[0]
    assert trunk.reference_status == "consolidada"
    assert trunk.reference is not None
    assert trunk.reference.method == "consenso_guiado"


def test_metrics_separate_binary_detection_and_directional_agreement() -> None:
    rows = build_case_comparisons(
        judgments=[
            _judgment(
                "e1",
                "trunk_lateral_inclination",
                "presente",
                "izquierda",
            ),
            _judgment(
                "e2",
                "trunk_lateral_inclination",
                "presente",
                "izquierda",
            ),
        ],
        system_decisions=[
            {
                "finding": "inclinacion_lateral_tronco",
                "status": "presente",
                "direction": "derecha",
            }
        ],
    )

    metrics = calculate_metrics([rows[0]], scope="tronco")
    assert metrics.true_positive == 1
    assert metrics.f1_score == 1.0
    assert metrics.exact_agreement == 0.0


def test_metrics_exclude_inconclusive_pairs() -> None:
    rows = build_case_comparisons(
        judgments=[
            _judgment("e1", "visible_dynamic_valgus", "no_concluyente"),
            _judgment("e2", "visible_dynamic_valgus", "no_concluyente"),
        ],
        system_decisions=[
            {
                "finding": "valgo_dinamico_visible",
                "status": "ausente",
            }
        ],
    )
    valgus = next(
        row for row in rows if row.pattern_key == "visible_dynamic_valgus"
    )

    metrics = calculate_metrics([valgus], scope="valgo")
    assert metrics.included_pairs == 0
    assert metrics.excluded_inconclusive_pairs == 1
    assert metrics.f1_score is None


def test_metrics_count_each_repetition_pattern_pair() -> None:
    rows = build_case_comparisons(
        judgments=[
            _judgment(
                evaluator,
                "visible_dynamic_valgus",
                classification,
                "izquierda" if classification == "presente" else None,
                repetition_index,
            )
            for repetition_index, classification in ((1, "presente"), (2, "ausente"))
            for evaluator in ("e1", "e2")
        ],
        system_decisions=[
            {
                "repetition_index": 1,
                "finding": "valgo_dinamico_visible",
                "status": "presente",
                "direction": "izquierda",
            },
            {
                "repetition_index": 2,
                "finding": "valgo_dinamico_visible",
                "status": "ausente",
            },
        ],
    )
    valgus_rows = [
        row for row in rows if row.pattern_key == "visible_dynamic_valgus"
    ]

    metrics = calculate_metrics(valgus_rows, scope="valgo")

    assert metrics.included_pairs == 2
    assert metrics.true_positive == 1
    assert metrics.true_negative == 1
    assert metrics.f1_score == 1.0
    assert metrics.cohen_kappa == 1.0


def test_fleiss_kappa_uses_only_items_with_three_experts() -> None:
    rows = build_case_comparisons(
        judgments=[
            _judgment(
                evaluator,
                "visible_dynamic_valgus",
                classification,
                "izquierda" if classification == "presente" else None,
                repetition_index,
            )
            for repetition_index, classification in (
                (1, "presente"),
                (2, "ausente"),
            )
            for evaluator in ("e1", "e2", "e3")
        ],
        system_decisions=[],
    )

    kappa, items = calculate_fleiss_kappa(rows)

    assert items == 2
    assert kappa == 1.0
