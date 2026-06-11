from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from uuid import uuid4

from models import Event, Trace, Turn, TurnScore
from security import redact_trace_text


class TraceManager:
    def __init__(self, scenario_id: str, assistant_profile: str) -> None:
        self.trace = Trace(
            trace_id=f"trace_{uuid4().hex[:10]}",
            scenario_id=scenario_id,
            assistant_profile=assistant_profile,
        )
        self._turn_counter = 0

    def next_turn_id(self) -> int:
        self._turn_counter += 1
        return self._turn_counter

    def add_event(self, event: Event) -> None:
        self.trace.events.append(event)

    def add_action_event(
        self,
        *,
        event_type: str,
        source: str,
        lens: str,
        severity: str,
        explanation: str,
        turn_id: int = 0,
    ) -> None:
        self.add_event(
            Event(
                event_id=f"evt:{event_type}:{uuid4().hex[:8]}",
                scenario_id=self.trace.scenario_id,
                turn_id=turn_id,
                event_type=event_type,
                source=source,
                lens=lens,
                severity=severity,
                explanation=explanation,
                created_at=datetime.utcnow().isoformat() + "Z",
            )
        )

    def add_turn(self, turn_id: int, user_message: str, assistant_response: str, annotations: list[str]) -> None:
        self.trace.turns.append(
            Turn(
                turn_id=turn_id,
                user_message=redact_trace_text(user_message),
                assistant_response=redact_trace_text(assistant_response),
                annotations=annotations,
            )
        )

    def add_score(self, turn_id: int, disclosure_risk: float, boundary_pressure: float) -> None:
        continuity_dependency = min(1.0, 0.2 + turn_id * 0.12)
        drift_delta = min(1.0, 0.1 + boundary_pressure * 0.5)
        intent_risk = min(1.0, 0.2 + boundary_pressure * 0.4)
        self.trace.scores.append(
            TurnScore(
                turn_id=turn_id,
                intent_risk=intent_risk,
                boundary_pressure=boundary_pressure,
                continuity_dependency=continuity_dependency,
                drift_delta=drift_delta,
                disclosure_risk=disclosure_risk,
            )
        )

    def set_debrief(self, payload: dict) -> None:
        self.trace.debrief = payload

    def export(self, traces_dir: Path) -> Path:
        traces_dir.mkdir(parents=True, exist_ok=True)
        output_path = traces_dir / f"{self.trace.trace_id}.json"
        output_path.write_text(self.trace.model_dump_json(indent=2), encoding="utf-8")
        output_path.chmod(0o600)
        return output_path


def replay_rows(trace: Trace) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    ordered = sorted(trace.events, key=lambda item: (item.turn_id, item.created_at))
    for event in ordered:
        rows.append(
            {
                "turn": str(event.turn_id),
                "time": event.created_at,
                "action": event.lens,
                "source": event.source,
                "event_type": event.event_type,
                "severity": event.severity,
                "explanation": event.explanation,
            }
        )
    return rows


def write_export_copy(trace: Trace, export_dir: Path) -> Path:
    export_dir.mkdir(parents=True, exist_ok=True)
    path = export_dir / f"{trace.trace_id}.json"
    path.write_text(json.dumps(trace.model_dump(), indent=2), encoding="utf-8")
    path.chmod(0o600)
    return path
