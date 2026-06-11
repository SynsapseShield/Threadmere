from __future__ import annotations

from datetime import datetime
from typing import Literal, Optional

from pydantic import BaseModel, Field

from .event_types import EventType


class User(BaseModel):
    user_id: str = Field(min_length=1)
    display_name: str = Field(min_length=1)
    created_at: datetime


class Workspace(BaseModel):
    workspace_id: str = Field(min_length=1)
    owner_user_id: str = Field(min_length=1)
    name: str = Field(min_length=1)
    created_at: datetime


class Session(BaseModel):
    session_id: str = Field(min_length=1)
    workspace_id: str = Field(min_length=1)
    initiated_by_user_id: str = Field(min_length=1)
    started_at: datetime


class Message(BaseModel):
    message_id: str = Field(min_length=1)
    session_id: str = Field(min_length=1)
    author_kind: Literal["user", "assistant", "system"]
    body: str = Field(min_length=1)
    created_at: datetime


class MemoryRecord(BaseModel):
    memory_id: str = Field(min_length=1)
    workspace_id: str = Field(min_length=1)
    source_message_id: str = Field(min_length=1)
    summary: str = Field(min_length=1)
    trust_level: float = Field(ge=0.0, le=1.0)
    created_at: datetime


class Task(BaseModel):
    task_id: str = Field(min_length=1)
    session_id: str = Field(min_length=1)
    title: str = Field(min_length=1)
    status: Literal["todo", "in_progress", "done", "blocked"]
    assignee_agent_id: Optional[str] = None
    created_at: datetime


class Agent(BaseModel):
    agent_id: str = Field(min_length=1)
    profile_id: str = Field(min_length=1)
    role_id: str = Field(min_length=1)
    active: bool = True


class AgentRole(BaseModel):
    role_id: str = Field(min_length=1)
    name: str = Field(min_length=1)
    description: str = Field(min_length=1)


class AgentPermission(BaseModel):
    permission_id: str = Field(min_length=1)
    agent_id: str = Field(min_length=1)
    permission_name: str = Field(min_length=1)
    granted: bool


class AgentObservation(BaseModel):
    observation_id: str = Field(min_length=1)
    session_id: str = Field(min_length=1)
    agent_id: str = Field(min_length=1)
    source_type: Literal["message", "artifact", "event", "snapshot"]
    source_id: str = Field(min_length=1)
    note: str = Field(min_length=1)
    created_at: datetime


class AgentDecision(BaseModel):
    decision_id: str = Field(min_length=1)
    session_id: str = Field(min_length=1)
    agent_id: str = Field(min_length=1)
    module_run_id: Optional[str] = None
    action: str = Field(min_length=1)
    rationale: str = Field(min_length=1)
    risk_score: float = Field(ge=0.0, le=1.0)
    trust_score: float = Field(ge=0.0, le=1.0)
    created_at: datetime


class Module(BaseModel):
    module_id: str = Field(min_length=1)
    name: str = Field(min_length=1)
    version: str = Field(min_length=1)
    deterministic: bool = True


class ModuleRun(BaseModel):
    module_run_id: str = Field(min_length=1)
    module_id: str = Field(min_length=1)
    session_id: str = Field(min_length=1)
    triggered_by_agent_id: Optional[str] = None
    input_ref: str = Field(min_length=1)
    started_at: datetime
    ended_at: Optional[datetime] = None
    status: Literal["running", "succeeded", "failed"]


class ModuleOutput(BaseModel):
    output_id: str = Field(min_length=1)
    module_run_id: str = Field(min_length=1)
    output_type: str = Field(min_length=1)
    payload_ref: str = Field(min_length=1)
    created_at: datetime


class Event(BaseModel):
    event_id: str = Field(min_length=1)
    session_id: str = Field(min_length=1)
    event_type: EventType
    severity: Literal["low", "medium", "high"]
    explanation: str = Field(min_length=1)
    created_at: datetime


class RiskSnapshot(BaseModel):
    snapshot_id: str = Field(min_length=1)
    session_id: str = Field(min_length=1)
    subject_id: str = Field(min_length=1)
    risk_score: float = Field(ge=0.0, le=1.0)
    measured_at: datetime


class TrustSnapshot(BaseModel):
    snapshot_id: str = Field(min_length=1)
    session_id: str = Field(min_length=1)
    subject_id: str = Field(min_length=1)
    trust_score: float = Field(ge=0.0, le=1.0)
    measured_at: datetime


class DriftSnapshot(BaseModel):
    snapshot_id: str = Field(min_length=1)
    session_id: str = Field(min_length=1)
    subject_id: str = Field(min_length=1)
    drift_score: float = Field(ge=0.0, le=1.0)
    measured_at: datetime


class ReplayFrame(BaseModel):
    frame_id: str = Field(min_length=1)
    session_id: str = Field(min_length=1)
    turn_id: int = Field(ge=1)
    event_id: str = Field(min_length=1)
    state_ref: str = Field(min_length=1)
    created_at: datetime


class AuditLogEntry(BaseModel):
    audit_id: str = Field(min_length=1)
    session_id: str = Field(min_length=1)
    actor_type: Literal["user", "agent", "module", "system"]
    actor_id: str = Field(min_length=1)
    action: str = Field(min_length=1)
    target_type: str = Field(min_length=1)
    target_id: str = Field(min_length=1)
    justification: str = Field(min_length=1)
    created_at: datetime


class ThreadmereState(BaseModel):
    users: dict[str, User] = Field(default_factory=dict)
    workspaces: dict[str, Workspace] = Field(default_factory=dict)
    sessions: dict[str, Session] = Field(default_factory=dict)
    messages: dict[str, Message] = Field(default_factory=dict)
    memories: dict[str, MemoryRecord] = Field(default_factory=dict)
    tasks: dict[str, Task] = Field(default_factory=dict)

    agents: dict[str, Agent] = Field(default_factory=dict)
    agent_roles: dict[str, AgentRole] = Field(default_factory=dict)
    agent_permissions: dict[str, AgentPermission] = Field(default_factory=dict)
    agent_observations: dict[str, AgentObservation] = Field(default_factory=dict)
    agent_decisions: dict[str, AgentDecision] = Field(default_factory=dict)

    modules: dict[str, Module] = Field(default_factory=dict)
    module_runs: dict[str, ModuleRun] = Field(default_factory=dict)
    module_outputs: dict[str, ModuleOutput] = Field(default_factory=dict)

    events: dict[str, Event] = Field(default_factory=dict)
    risk_snapshots: dict[str, RiskSnapshot] = Field(default_factory=dict)
    trust_snapshots: dict[str, TrustSnapshot] = Field(default_factory=dict)
    drift_snapshots: dict[str, DriftSnapshot] = Field(default_factory=dict)
    replay_frames: dict[str, ReplayFrame] = Field(default_factory=dict)
    audit_log: dict[str, AuditLogEntry] = Field(default_factory=dict)
