"""API requests for investigator consensus and comparison."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field, model_validator


class SquatManualReferenceRequest(BaseModel):
    """Guided consensus recorded for one unresolved pattern."""

    classification: Literal["presente", "ausente", "no_concluyente"]
    observed_side: Literal[
        "izquierda",
        "derecha",
        "bilateral",
        "sin_direccion",
    ] | None = None
    observation: str | None = Field(default=None, max_length=1000)

    @model_validator(mode="after")
    def validate_side(self) -> "SquatManualReferenceRequest":
        """Require direction only when the consensus is positive."""
        if self.classification == "presente" and self.observed_side is None:
            raise ValueError(
                "A present reference requires an observed side."
            )
        if self.classification != "presente" and self.observed_side is not None:
            raise ValueError(
                "Only a present reference can include an observed side."
            )
        return self


__all__ = ["SquatManualReferenceRequest"]
