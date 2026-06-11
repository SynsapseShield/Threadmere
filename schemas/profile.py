from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field


class ToneTraits(BaseModel):
    warmth: float = Field(ge=0.0, le=1.0)
    directness: float = Field(ge=0.0, le=1.0)
    formality: float = Field(ge=0.0, le=1.0)
    reassurance: float = Field(ge=0.0, le=1.0)


class PriorityTraits(BaseModel):
    helpfulness: float = Field(ge=0.0, le=1.0)
    safety: float = Field(ge=0.0, le=1.0)
    provenance: float = Field(ge=0.0, le=1.0)
    continuity: float = Field(ge=0.0, le=1.0)
    efficiency: float = Field(ge=0.0, le=1.0)
    user_dignity: float = Field(ge=0.0, le=1.0)


class BoundaryTraits(BaseModel):
    ambiguity_tolerance: float = Field(ge=0.0, le=1.0)
    authority_skepticism: float = Field(ge=0.0, le=1.0)
    private_data_sensitivity: float = Field(ge=0.0, le=1.0)
    refusal_threshold: float = Field(ge=0.0, le=1.0)
    clarification_threshold: float = Field(ge=0.0, le=1.0)
    quarantine_threshold: float = Field(ge=0.0, le=1.0)


class MemoryTraits(BaseModel):
    can_write_memory: bool
    memory_write_threshold: float = Field(ge=0.0, le=1.0)
    requires_verified_sources: bool
    allows_unverified_summaries: bool


class ToolTraits(BaseModel):
    can_request_tools: bool
    tool_use_threshold: float = Field(ge=0.0, le=1.0)
    requires_human_review_for_tools: bool


class ResponseStyle(BaseModel):
    default_refusal_style: Literal[
        "safe_redirect", "evidence_required", "operational_limit", "soft_redirect"
    ]
    prefers_clarifying_questions: bool
    max_response_lines: int = Field(ge=1, le=30)
    inline_explanation: bool


class AssistantProfile(BaseModel):
    profile_id: str = Field(min_length=1)
    display_name: str = Field(min_length=1)
    description: str = Field(min_length=1)
    tone: ToneTraits
    priorities: PriorityTraits
    boundaries: BoundaryTraits
    memory: MemoryTraits
    tools: ToolTraits
    response_style: ResponseStyle


class AssistantProfileRegistry(BaseModel):
    profiles: dict[str, AssistantProfile]
