from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class LensRuleConditions(BaseModel):
    model_config = ConfigDict(extra="forbid")

    has_hidden_text: bool | None = None
    contains_instruction_like_language: bool | None = None
    has_metadata_conflict: bool | None = None
    has_ocr_mismatch: bool | None = None
    can_write_memory: bool | None = None
    can_enter_retrieval: bool | None = None
    source_confidence_lte: float | None = Field(default=None, ge=0.0, le=1.0)
    trust_state_in: list[str] = Field(default_factory=list)
    quarantine_status_in: list[str] = Field(default_factory=list)
    source_type_in: list[str] = Field(default_factory=list)
    requires_retrieval_requested: bool | None = None
    requires_memory_write_requested: bool | None = None


class LensRule(BaseModel):
    rule_id: str = Field(min_length=1)
    lens: str = Field(min_length=1)
    severity: Literal["low", "medium", "high"]
    explanation: str = Field(min_length=1)
    conditions: LensRuleConditions = Field(alias="if")
    emit_event: str = Field(min_length=1)


class LensRuleSet(BaseModel):
    rules: list[LensRule]
