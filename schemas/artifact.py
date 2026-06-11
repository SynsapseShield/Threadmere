from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field


class ChainOfCustodyStep(BaseModel):
    step: str = Field(min_length=1)
    verified: bool


class NormalizedArtifact(BaseModel):
    model_config = ConfigDict(extra="forbid")

    artifact_id: str = Field(min_length=1)
    filename: str = Field(min_length=1)
    artifact_type: str = Field(min_length=1)
    source_type: str = Field(min_length=1)
    source_confidence: float = Field(ge=0.0, le=1.0)
    trust_state: Literal["trusted", "unverified", "unknown"] = "unknown"
    visible_text: str = Field(min_length=1)
    hidden_text: str = ""
    metadata: dict[str, Any] = Field(default_factory=dict)
    ocr_text: str = ""
    rendered_text: str = ""
    parsed_text: str = ""
    summary: str = ""
    visible_summary: str = ""
    visible_source: str = ""
    visible_author: str = ""
    created_by: str = Field(min_length=1)
    imported_from: str = Field(min_length=1)
    first_seen_at: str = Field(min_length=1)
    chain_of_custody: list[ChainOfCustodyStep] = Field(default_factory=list)
    has_hidden_text: bool = False
    has_metadata_conflict: bool = False
    has_ocr_mismatch: bool = False
    contains_instruction_like_language: bool = False
    can_write_memory: bool = False
    can_enter_retrieval: bool = False
    quarantine_status: Literal["clean", "quarantined", "review"] = "clean"

    @property
    def display_name(self) -> str:
        return self.filename or self.artifact_id


class ArtifactFixtureSet(BaseModel):
    artifacts: list[NormalizedArtifact]
