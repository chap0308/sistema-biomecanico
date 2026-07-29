"""Typed API contracts for blinded expert squat evaluation."""

from __future__ import annotations

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field, field_validator, model_validator

SquatPatternKey = Literal[
    "trunk_lateral_inclination",
    "pelvis_lateral_shift",
    "visible_dynamic_valgus",
    "bilateral_asymmetry",
]
ExpertClassification = Literal["presente", "ausente", "no_concluyente"]
ExpertConfidence = Literal["baja", "media", "alta"]
ObservedSide = Literal["izquierda", "derecha", "bilateral", "sin_direccion"]
EvaluationStatus = Literal["draft", "submitted"]

REQUIRED_PATTERNS = {
    "trunk_lateral_inclination",
    "pelvis_lateral_shift",
    "visible_dynamic_valgus",
    "bilateral_asymmetry",
}


class SquatExpertProfileResponse(BaseModel):
    """Expert account available to the investigator."""

    user_id: str
    email: str | None = None
    display_name: str | None = None


class SquatAssignmentCreateRequest(BaseModel):
    """Experts selected for one completed case."""

    evaluator_ids: list[str] = Field(min_length=1, max_length=3)

    @field_validator("evaluator_ids")
    @classmethod
    def unique_evaluators(cls, values: list[str]) -> list[str]:
        """Reject repeated evaluator identifiers."""
        if len(values) != len(set(values)):
            raise ValueError("evaluator_ids must be unique")
        return values


class SquatAssignmentCreatedResponse(BaseModel):
    """Result of assigning one case to selected experts."""

    case_id: str
    assigned: int = Field(ge=0)


class SquatCaseAssignmentResponse(BaseModel):
    """One evaluator currently assigned to an investigator-owned case."""

    assignment_id: str
    evaluator_id: str
    email: str | None = None
    display_name: str | None = None
    status: Literal["pending", "in_progress", "submitted"]
    has_response: bool = False


class SquatCaseAssignmentsResponse(BaseModel):
    """Assignment roster and its lifecycle lock."""

    case_id: str
    reference_status: Literal["open", "in_progress", "closed"]
    assignments: list[SquatCaseAssignmentResponse]


class SquatExpertEvaluationItem(BaseModel):
    """One independent observational classification."""

    repetition_index: int = Field(default=1, ge=1)
    pattern_key: SquatPatternKey
    classification: ExpertClassification
    observed_side: ObservedSide | None = None
    confidence: ExpertConfidence | None = None
    observation: str | None = Field(default=None, max_length=500)

    @model_validator(mode="after")
    def validate_observed_side(self) -> "SquatExpertEvaluationItem":
        """Keep direction meaningful only for a positive classification."""
        if self.classification == "presente" and self.observed_side is None:
            raise ValueError(
                "A present classification requires an observed side."
            )
        if self.classification != "presente" and self.observed_side is not None:
            raise ValueError(
                "Only a present classification can include an observed side."
            )
        return self


class SquatExpertEvaluationRequest(BaseModel):
    """Draft or final Instrument 3 response."""

    status: EvaluationStatus
    general_observation: str | None = Field(default=None, max_length=1000)
    items: list[SquatExpertEvaluationItem] = Field(default_factory=list)

    @model_validator(mode="after")
    def validate_items(self) -> "SquatExpertEvaluationRequest":
        """Require unique patterns and a complete final submission."""
        keys = [
            (item.repetition_index, item.pattern_key) for item in self.items
        ]
        if len(keys) != len(set(keys)):
            raise ValueError(
                "Each pattern can be evaluated only once per repetition."
            )
        if self.status == "submitted":
            repetition_indexes = {
                item.repetition_index for item in self.items
            }
            if not repetition_indexes:
                raise ValueError(
                    "A submitted evaluation requires at least one repetition."
                )
            for repetition_index in repetition_indexes:
                patterns = {
                    item.pattern_key
                    for item in self.items
                    if item.repetition_index == repetition_index
                }
                if patterns != REQUIRED_PATTERNS:
                    raise ValueError(
                        "Every submitted repetition must classify all four patterns."
                    )
        if self.status == "submitted" and any(
            item.confidence is None for item in self.items
        ):
            raise ValueError(
                "A submitted evaluation requires confidence for every pattern."
            )
        return self


class SquatExpertEvaluationResponse(BaseModel):
    """Expert-owned evaluation state, never system output."""

    evaluation_id: str
    status: EvaluationStatus
    general_observation: str | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None
    submitted_at: datetime | None = None
    items: list[SquatExpertEvaluationItem] = Field(default_factory=list)


class SquatExpertRepetitionResponse(BaseModel):
    """Temporal interval shown to the expert without system classifications."""

    repetition_index: int = Field(ge=1)
    start_seconds: float = Field(ge=0.0)
    peak_depth_seconds: float = Field(ge=0.0)
    end_seconds: float = Field(ge=0.0)


class SquatExpertAssignmentResponse(BaseModel):
    """Blinded assignment visible to its evaluator."""

    assignment_id: str
    case_id: str
    status: Literal["pending", "in_progress", "submitted"]
    created_at: datetime
    updated_at: datetime
    reference_status: Literal["open", "in_progress", "closed"] = "open"
    repetitions: list[SquatExpertRepetitionResponse] = Field(default_factory=list)
    evaluation: SquatExpertEvaluationResponse | None = None


class SquatEvaluationSavedResponse(BaseModel):
    """Confirmation returned after saving or submitting."""

    evaluation_id: str
    status: EvaluationStatus


__all__ = [
    "SquatAssignmentCreateRequest",
    "SquatAssignmentCreatedResponse",
    "SquatCaseAssignmentsResponse",
    "SquatEvaluationSavedResponse",
    "SquatExpertAssignmentResponse",
    "SquatExpertEvaluationRequest",
    "SquatExpertProfileResponse",
]
