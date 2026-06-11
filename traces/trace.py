from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field

from schemas.event_types import EventType


class LensEvent(BaseModel):
    event_id: str = Field(min_length=1)
    scenario_id: str = Field(min_length=1)
    turn_id: int = Field(ge=1)
    event_type: EventType
    rule_id: str = Field(min_length=1)
    artifact_id: str = Field(min_length=1)
    source: str = Field(min_length=1)
    lens: str = Field(min_length=1)
    severity: Literal["low", "medium", "high"]
    explanation: str = Field(min_length=1)
    matched_conditions: list[str] = Field(default_factory=list)
    inline_annotation: str = ""


class TurnScores(BaseModel):
    turn_id: int = Field(ge=1)
    intent_risk: float = Field(ge=0.0, le=1.0)
    boundary_pressure: float = Field(ge=0.0, le=1.0)
    continuity_dependency: float = Field(ge=0.0, le=1.0)
    drift_delta: float = Field(ge=0.0, le=1.0)
    disclosure_risk: float = Field(ge=0.0, le=1.0)


class RetrievalDecision(BaseModel):
    turn_id: int = Field(ge=1)
    artifact_id: str = Field(min_length=1)
    allowed: bool
    reason: str = Field(min_length=1)


class MemoryWriteDecision(BaseModel):
    turn_id: int = Field(ge=1)
    artifact_id: str = Field(min_length=1)
    allowed: bool
    reason: str = Field(min_length=1)


class TurnRecord(BaseModel):
    turn_id: int = Field(ge=1)
    user_message: str = Field(min_length=1)
    assistant_response: str = Field(min_length=1)
    annotations: list[str] = Field(default_factory=list)
    inspected_artifacts: list[str] = Field(default_factory=list)
    retrieved_artifacts: list[str] = Field(default_factory=list)


class DebriefReport(BaseModel):
    summary: str = Field(min_length=1)
    successes: list[str] = Field(default_factory=list)
    failures: list[str] = Field(default_factory=list)
    next_steps: list[str] = Field(default_factory=list)


class SessionTrace(BaseModel):
    trace_id: str = Field(min_length=1)
    scenario_id: str = Field(min_length=1)
    assistant_profile: str = Field(min_length=1)
    turns: list[TurnRecord] = Field(default_factory=list)
    events: list[LensEvent] = Field(default_factory=list)
    scores: list[TurnScores] = Field(default_factory=list)
    memory_writes: list[MemoryWriteDecision] = Field(default_factory=list)
    retrievals: list[RetrievalDecision] = Field(default_factory=list)
    debrief: DebriefReport


class LensTrace(SessionTrace):
    pass
