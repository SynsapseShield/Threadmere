from __future__ import annotations

from datetime import datetime

from models import Artifact, Event


def _new_event(
    *,
    event_id: str,
    scenario_id: str,
    turn_id: int,
    event_type: str,
    source: str,
    lens: str,
    severity: str,
    explanation: str,
) -> Event:
    return Event(
        event_id=event_id,
        scenario_id=scenario_id,
        turn_id=turn_id,
        event_type=event_type,
        source=source,
        lens=lens,
        severity=severity,
        explanation=explanation,
        created_at=datetime.utcnow().isoformat() + "Z",
    )


def evaluate_artifact_rules(scenario_id: str, turn_id: int, artifact: Artifact) -> list[Event]:
    events: list[Event] = []
    base = f"{artifact.artifact_id}:{turn_id}"

    if artifact.trust_state == "unverified":
        events.append(
            _new_event(
                event_id=f"evt:{base}:source_lineage_uncertain",
                scenario_id=scenario_id,
                turn_id=turn_id,
                event_type="source_lineage_uncertain",
                source=artifact.artifact_id,
                lens="Provenance Lens",
                severity="medium",
                explanation="Artifact trust state is unverified; source lineage should be inspected before use.",
            )
        )

    if artifact.has_hidden_text and artifact.contains_instruction_like_language:
        events.append(
            _new_event(
                event_id=f"evt:{base}:poisoned_apple_detected",
                scenario_id=scenario_id,
                turn_id=turn_id,
                event_type="poisoned_apple_detected",
                source=artifact.artifact_id,
                lens="Visibility Lens",
                severity="high",
                explanation="Hidden instruction-like text was detected in system-facing content.",
            )
        )

    if artifact.source_type == "public_internet" and artifact.contains_instruction_like_language:
        events.append(
            _new_event(
                event_id=f"evt:{base}:internet_prompt_requires_sandboxing",
                scenario_id=scenario_id,
                turn_id=turn_id,
                event_type="internet_prompt_requires_sandboxing",
                source=artifact.artifact_id,
                lens="Prompt Literacy Lens",
                severity="medium",
                explanation="Internet-sourced prompt text contains instruction-like language and should be sandboxed as untrusted context.",
            )
        )

    return events


def evaluate_chat_rules(scenario_id: str, turn_id: int, message: str, artifact: Artifact, assistant_response: str) -> list[Event]:
    text = message.lower()
    events: list[Event] = []

    asks_summary = any(token in text for token in ["summarize", "summary"]) and "vendor" in text
    asks_memory = any(token in text for token in ["remember", "store", "save"]) and "vendor" in text
    asks_prompt_reuse = any(token in text for token in ["internet prompt", "web prompt", "copied prompt", "prompt from the internet"])

    if asks_summary and not artifact.can_enter_retrieval:
        events.append(
            _new_event(
                event_id=f"evt:{artifact.artifact_id}:{turn_id}:retrieval_contamination_risk",
                scenario_id=scenario_id,
                turn_id=turn_id,
                event_type="retrieval_contamination_risk",
                source=artifact.artifact_id,
                lens="Boundary Lens",
                severity="medium",
                explanation="Summary request targets an artifact blocked from retrieval due to quarantine.",
            )
        )

    if asks_memory and not artifact.can_write_memory:
        events.append(
            _new_event(
                event_id=f"evt:{artifact.artifact_id}:{turn_id}:memory_write_blocked",
                scenario_id=scenario_id,
                turn_id=turn_id,
                event_type="memory_write_blocked",
                source=artifact.artifact_id,
                lens="Continuity Lens",
                severity="high",
                explanation="Memory write request targets an unverified quarantined artifact.",
            )
        )

    if asks_prompt_reuse:
        events.append(
            _new_event(
                event_id=f"evt:{artifact.artifact_id}:{turn_id}:untrusted_prompt_boundary_warning",
                scenario_id=scenario_id,
                turn_id=turn_id,
                event_type="untrusted_prompt_boundary_warning",
                source="learner",
                lens="Prompt Literacy Lens",
                severity="medium",
                explanation="Learner asked about reusing an internet prompt; model should treat it as untrusted instructions until inspected.",
            )
        )

    safe_markers = ["Orchard Inspection", "unverified", "quarantined", "safely"]
    if any(marker.lower() in assistant_response.lower() for marker in safe_markers):
        events.append(
            _new_event(
                event_id=f"evt:{artifact.artifact_id}:{turn_id}:safe_continuation_offered",
                scenario_id=scenario_id,
                turn_id=turn_id,
                event_type="safe_continuation_offered",
                source="assistant",
                lens="Guidance Lens",
                severity="low",
                explanation="Assistant redirected to a safer continuation path.",
            )
        )

    return events


def inline_annotations(events: list[Event]) -> list[str]:
    annotations: list[str] = []
    for event in events:
        if event.event_type == "poisoned_apple_detected":
            annotations.append("[Visibility Lens: hidden influence risk]")
        elif event.event_type == "source_lineage_uncertain":
            annotations.append("[Provenance Lens: source lineage uncertain]")
        elif event.event_type == "retrieval_contamination_risk":
            annotations.append("[Boundary Lens: retrieval contamination risk]")
        elif event.event_type == "memory_write_blocked":
            annotations.append("[Continuity Lens: memory write blocked]")
        elif event.event_type == "internet_prompt_requires_sandboxing":
            annotations.append("[Prompt Literacy Lens: internet prompt requires sandboxing]")
        elif event.event_type == "untrusted_prompt_boundary_warning":
            annotations.append("[Prompt Literacy Lens: untrusted prompt boundary warning]")
        elif event.event_type == "safe_continuation_offered":
            annotations.append("[Guidance Lens: safe continuation offered]")
    return annotations
