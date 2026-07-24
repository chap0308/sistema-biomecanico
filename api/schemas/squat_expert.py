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


class SquatExpertEvaluationItem(BaseModel):
    """One independent observational classification."""

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
        patterns = [item.pattern_key for item in self.items]
        if len(patterns) != len(set(patterns)):
            raise ValueError("Each pattern can be evaluated only once.")
        if self.status == "submitted" and set(patterns) != REQUIRED_PATTERNS:
            raise ValueError(
                "A submitted evaluation must classify all four patterns."
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


class SquatExpertAssignmentResponse(BaseModel):
    """Blinded assignment visible to its evaluator."""

    assignment_id: str
    case_id: str
    status: Literal["pending", "in_progress", "submitted"]
    created_at: datetime
    updated_at: datetime
    evaluation: SquatExpertEvaluationResponse | None = None


class SquatEvaluationSavedResponse(BaseModel):
    """Confirmation returned after saving or submitting."""

    evaluation_id: str
    status: EvaluationStatus


__all__ = [
    "SquatAssignmentCreateRequest",
    "SquatAssignmentCreatedResponse",
    "SquatEvaluationSavedResponse",
    "SquatExpertAssignmentResponse",
    "SquatExpertEvaluationRequest",
    "SquatExpertProfileResponse",
]
