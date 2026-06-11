from __future__ import annotations

from schemas.artifact import NormalizedArtifact
from schemas.lens_rule import LensRule, LensRuleSet
from traces.trace import LensEvent


def evaluate_rule(
    rule: LensRule,
    artifact: NormalizedArtifact,
    *,
    scenario_id: str,
    turn_id: int,
    retrieval_requested: bool,
    memory_write_requested: bool,
) -> LensEvent | None:
    matched_conditions: list[str] = []
    conditions = rule.conditions

    equality_checks = {
        "has_hidden_text": artifact.has_hidden_text,
        "contains_instruction_like_language": artifact.contains_instruction_like_language,
        "has_metadata_conflict": artifact.has_metadata_conflict,
        "has_ocr_mismatch": artifact.has_ocr_mismatch,
        "can_write_memory": artifact.can_write_memory,
        "can_enter_retrieval": artifact.can_enter_retrieval,
        "requires_retrieval_requested": retrieval_requested,
        "requires_memory_write_requested": memory_write_requested,
    }

    for key, actual_value in equality_checks.items():
        expected_value = getattr(conditions, key)
        if expected_value is None:
            continue
        if actual_value != expected_value:
            return None
        matched_conditions.append(key)

    if conditions.source_confidence_lte is not None:
        if artifact.source_confidence > conditions.source_confidence_lte:
            return None
        matched_conditions.append("source_confidence_lte")

    if conditions.trust_state_in:
        if artifact.trust_state not in conditions.trust_state_in:
            return None
        matched_conditions.append("trust_state_in")

    if conditions.quarantine_status_in:
        if artifact.quarantine_status not in conditions.quarantine_status_in:
            return None
        matched_conditions.append("quarantine_status_in")

    if conditions.source_type_in:
        if artifact.source_type not in conditions.source_type_in:
            return None
        matched_conditions.append("source_type_in")

    return LensEvent(
        event_id=f"{rule.rule_id}:{artifact.artifact_id}:{turn_id}",
        scenario_id=scenario_id,
        turn_id=turn_id,
        event_type=rule.emit_event,
        rule_id=rule.rule_id,
        artifact_id=artifact.artifact_id,
        source=artifact.display_name,
        lens=rule.lens,
        severity=rule.severity,
        explanation=rule.explanation,
        matched_conditions=matched_conditions,
        inline_annotation=f"{rule.lens.replace('_', ' ')}: {rule.explanation}",
    )


def evaluate_artifacts(
    artifacts: list[NormalizedArtifact],
    ruleset: LensRuleSet,
    *,
    scenario_id: str,
    turn_id: int,
    retrieval_requested: bool = False,
    memory_write_requested: bool = False,
) -> list[LensEvent]:
    events: list[LensEvent] = []
    for artifact in artifacts:
        for rule in ruleset.rules:
            event = evaluate_rule(
                rule,
                artifact,
                scenario_id=scenario_id,
                turn_id=turn_id,
                retrieval_requested=retrieval_requested,
                memory_write_requested=memory_write_requested,
            )
            if event is not None:
                events.append(event)

    return events
