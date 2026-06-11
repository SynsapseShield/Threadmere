from __future__ import annotations

from typing import Literal

# Canonical inspectable lifecycle events.
INSPECTABLE_EVENT_TYPES = (
    "user_message_received",
    "agent_invoked",
    "module_ran",
    "risk_detected",
    "boundary_triggered",
    "safe_redirect_suggested",
    "memory_updated",
    "loop_detected",
    "human_review_requested",
)

# Backward-compatible event types kept for existing fixtures/rules.
LEGACY_EVENT_TYPES = (
    "artifact_loaded",
    "policy_warning",
    "poisoned_apple_detected",
    "source_lineage_uncertain",
    "retrieval_contamination_risk",
    "memory_write_blocked",
)

ALL_EVENT_TYPES = INSPECTABLE_EVENT_TYPES + LEGACY_EVENT_TYPES

EventType = Literal[
    "user_message_received",
    "agent_invoked",
    "module_ran",
    "risk_detected",
    "boundary_triggered",
    "safe_redirect_suggested",
    "memory_updated",
    "loop_detected",
    "human_review_requested",
    "artifact_loaded",
    "policy_warning",
    "poisoned_apple_detected",
    "source_lineage_uncertain",
    "retrieval_contamination_risk",
    "memory_write_blocked",
]
