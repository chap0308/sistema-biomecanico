"""Tests for the exercise recommendation knowledge base."""

from recommendations.exercises import recommend_exercises


def test_recommend_exercises_returns_winging_protocols_for_matching_deficiencies() -> None:
    recommendations = recommend_exercises(
        ["possible_scapular_winging_pattern", "scapular_resting_asymmetry"]
    )

    protocol_ids = [item["protocol_id"] for item in recommendations]

    assert "scapular_winging_triceps_low_trap_band" in protocol_ids


def test_recommend_exercises_returns_forward_posture_protocol() -> None:
    recommendations = recommend_exercises(["forward_posture_pattern"])

    assert recommendations
    assert recommendations[0]["protocol_id"] == "pec_decompression_and_side_lying_ir_breath"


def test_recommend_exercises_ignores_unknown_deficiency_ids() -> None:
    recommendations = recommend_exercises(["unknown_deficiency"])

    assert recommendations == []


def test_recommend_exercises_returns_hip_protocol_for_matching_deficiency() -> None:
    recommendations = recommend_exercises(["posterior_hip_glide_restriction"])

    protocol_ids = [item["protocol_id"] for item in recommendations]

    assert "hip_posterior_glide_mobility_sequence" in protocol_ids
