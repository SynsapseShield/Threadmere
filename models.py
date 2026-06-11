from __future__ import annotations

from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel, Field


class ChainOfCustodyStep(BaseModel):
    step: str = Field(min_length=1)
    verified: bool


class Artifact(BaseModel):
    artifact_id: str = Field(min_length=1)
    filename: str = Field(min_length=1)
    artifact_type: str = Field(min_length=1)
    source_type: str = Field(min_length=1)
    source_confidence: float = Field(ge=0.0, le=1.0)
    trust_state: Literal["trusted", "unverified", "unknown"]
    visible_text: str = Field(min_length=1)
    hidden_text: str = ""
    metadata: dict[str, Any] = Field(default_factory=dict)
    ocr_text: str = ""
    rendered_text: str = ""
    parsed_text: str = ""
    summary: str = ""
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
    quarantine_status: Literal["clear", "review", "quarantined"] = "clear"


class Scenario(BaseModel):
    scenario_id: str = Field(min_length=1)
    title: str = Field(min_length=1)
    domain_pack: str = Field(min_length=1)
    learner_role: str = Field(min_length=1)
    assistant_profile: str = Field(min_length=1)
    available_artifacts: list[str] = Field(min_length=1)
    trusted_sources: list[str] = Field(default_factory=list)
    untrusted_sources: list[str] = Field(default_factory=list)
    hidden_risks: list[str] = Field(default_factory=list)
    active_policies: list[str] = Field(default_factory=list)
    success_conditions: list[str] = Field(default_factory=list)
    failure_conditions: list[str] = Field(default_factory=list)
    expected_lens_events: list[str] = Field(default_factory=list)
    debrief_goals: list[str] = Field(default_factory=list)


class ProfileTraits(BaseModel):
    calmness: float = Field(ge=0.0, le=1.0)
    provenance_strictness: float = Field(ge=0.0, le=1.0)
    continuity_sensitivity: float = Field(ge=0.0, le=1.0)
    policy_rigidity: float = Field(ge=0.0, le=1.0)
    explanatory_style: float = Field(ge=0.0, le=1.0)


class AssistantProfile(BaseModel):
    profile_id: str = Field(min_length=1)
    display_name: str = Field(min_length=1)
    profile_category: Literal["agent", "ai"]
    tagline: str = Field(min_length=1)
    behavior: str = Field(min_length=1)
    traits: ProfileTraits


class ProfileRegistry(BaseModel):
    profiles: dict[str, AssistantProfile] = Field(default_factory=dict)


class Event(BaseModel):
    event_id: str = Field(min_length=1)
    scenario_id: str = Field(min_length=1)
    turn_id: int = Field(ge=0)
    event_type: str = Field(min_length=1)
    source: str = Field(min_length=1)
    lens: str = Field(min_length=1)
    severity: Literal["low", "medium", "high"]
    explanation: str = Field(min_length=1)
    created_at: str = Field(default_factory=lambda: datetime.utcnow().isoformat() + "Z")


class Turn(BaseModel):
    turn_id: int = Field(ge=1)
    user_message: str = Field(min_length=1)
    assistant_response: str = Field(min_length=1)
    annotations: list[str] = Field(default_factory=list)


class TurnScore(BaseModel):
    turn_id: int = Field(ge=1)
    intent_risk: float = Field(ge=0.0, le=1.0)
    boundary_pressure: float = Field(ge=0.0, le=1.0)
    continuity_dependency: float = Field(ge=0.0, le=1.0)
    drift_delta: float = Field(ge=0.0, le=1.0)
    disclosure_risk: float = Field(ge=0.0, le=1.0)


class Trace(BaseModel):
    trace_id: str = Field(min_length=1)
    scenario_id: str = Field(min_length=1)
    assistant_profile: str = Field(min_length=1)
    turns: list[Turn] = Field(default_factory=list)
    events: list[Event] = Field(default_factory=list)
    scores: list[TurnScore] = Field(default_factory=list)
    memory_writes: list[dict[str, Any]] = Field(default_factory=list)
    retrievals: list[dict[str, Any]] = Field(default_factory=list)
    debrief: dict[str, Any] = Field(default_factory=dict)
