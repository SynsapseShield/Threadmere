from __future__ import annotations

from pathlib import Path

from rich.console import Console

from tm_lenses import evaluate_artifact_rules, evaluate_chat_rules, inline_annotations
from loader import load_artifacts, load_policies, load_profiles, load_scenario, load_world
from models import Artifact
from profiles import format_profile, get_profile, list_profile_lines, scripted_response
from trace import TraceManager, replay_rows, write_export_copy
from ui import (
    assistant_output,
    briefing,
    command_error,
    debrief,
    export_notice,
    inspect_artifact,
    orchard,
    print_help,
    prompt_lab,
    profiles,
    replay,
    show_profile,
    startup,
    weaver_log,
)


BASE_DIR = Path(__file__).parent
DOMAIN = BASE_DIR / "domain_packs" / "aster_vale_municipal"
SCENARIO_FILE = DOMAIN / "scenarios" / "q1_sharepoint_poisoned_deck.yaml"
ARTIFACTS_DIR = DOMAIN / "artifacts"
PROFILES_FILE = DOMAIN / "assistant_profiles.yaml"
WORLD_FILE = DOMAIN / "world.yaml"
POLICIES_FILE = DOMAIN / "policies.yaml"
TRACES_DIR = BASE_DIR / "traces"
EXPORTS_DIR = BASE_DIR / "exports"


def select_chat_artifact(message: str, artifacts: dict[str, Artifact]) -> Artifact | None:
    normalized = message.lower()

    for artifact_id, artifact in artifacts.items():
        if artifact_id.lower() in normalized:
            return artifact

    if any(token in normalized for token in ["internet prompt", "web prompt", "copied prompt", "prompt from the internet"]):
        return artifacts.get("internet_prompt_snippet")

    if any(token in normalized for token in ["vendor", "q1", "deck"]):
        return artifacts.get("vendor_q1_summary")

    return None


class ThreadmereApp:
    def __init__(self) -> None:
        self.console = Console()
        self.scenario = load_scenario(SCENARIO_FILE)
        self.artifacts = load_artifacts(ARTIFACTS_DIR)
        self.registry = load_profiles(PROFILES_FILE)
        self.world = load_world(WORLD_FILE)
        self.policies = load_policies(POLICIES_FILE)

        self.active_profile_id = self.scenario.assistant_profile
        self.active_profile = get_profile(self.registry, self.active_profile_id)
        self.trace_manager = TraceManager(self.scenario.scenario_id, self.active_profile_id)
        self.trace_manager.add_action_event(
            event_type="scenario_loaded",
            source=self.scenario.scenario_id,
            lens="System",
            severity="low",
            explanation="Scenario loaded and session initialized.",
            turn_id=0,
        )

    def reset(self) -> None:
        self.active_profile_id = self.scenario.assistant_profile
        self.active_profile = get_profile(self.registry, self.active_profile_id)
        self.trace_manager = TraceManager(self.scenario.scenario_id, self.active_profile_id)
        self.trace_manager.add_action_event(
            event_type="scenario_loaded",
            source=self.scenario.scenario_id,
            lens="System",
            severity="low",
            explanation="Session reset with default profile.",
            turn_id=0,
        )

    def run(self) -> None:
        startup(self.console, self.scenario)
        print_help(self.console)

        while True:
            raw = input("threadmere> ").strip()
            if not raw:
                continue

            command, _, remainder = raw.partition(" ")
            command = command.lower()

            if command == "help":
                print_help(self.console)
                continue

            if command == "briefing":
                briefing(self.console, self.scenario, self.world, self.policies)
                continue

            if command == "promptlab":
                prompt_lab(self.console)
                self.trace_manager.add_action_event(
                    event_type="prompt_literacy_lesson_viewed",
                    source="promptlab",
                    lens="Prompt Literacy Lens",
                    severity="low",
                    explanation="Learner reviewed basic prompting, context, provenance, and security boundary concepts.",
                    turn_id=self.trace_manager.next_turn_id(),
                )
                continue

            if command == "orchard":
                orchard(self.console, self.artifacts)
                continue

            if command == "profiles":
                profiles(self.console, list_profile_lines(self.registry))
                continue

            if command == "profile":
                if not remainder:
                    command_error(self.console, "Usage: profile <profile_id>")
                    continue
                profile_id = remainder.strip().upper()
                try:
                    profile = get_profile(self.registry, profile_id)
                except KeyError as exc:
                    command_error(self.console, str(exc))
                    continue
                self.active_profile_id = profile.profile_id
                self.active_profile = profile
                self.trace_manager.trace.assistant_profile = profile.profile_id
                self.trace_manager.add_action_event(
                    event_type="assistant_profile_changed",
                    source=profile.profile_id,
                    lens="System",
                    severity="low",
                    explanation="Active assistant profile changed and trace provenance was updated.",
                    turn_id=self.trace_manager.next_turn_id(),
                )
                show_profile(self.console, format_profile(profile))
                continue

            if command == "inspect":
                if not remainder:
                    command_error(self.console, "Usage: inspect <artifact_id>")
                    continue
                artifact_id = remainder.strip()
                artifact = self.artifacts.get(artifact_id)
                if artifact is None:
                    command_error(self.console, f"Unknown artifact: {artifact_id}")
                    continue
                inspect_artifact(self.console, artifact)

                turn_id = self.trace_manager.next_turn_id()
                self.trace_manager.add_action_event(
                    event_type="artifact_inspected",
                    source=artifact_id,
                    lens="Inspector",
                    severity="low",
                    explanation="Artifact inspected through Orchard Inspection.",
                    turn_id=turn_id,
                )
                for event in evaluate_artifact_rules(self.scenario.scenario_id, turn_id, artifact):
                    self.trace_manager.add_event(event)
                continue

            if command == "chat":
                if not remainder:
                    command_error(self.console, "Usage: chat <message>")
                    continue

                message = remainder.strip()
                turn_id = self.trace_manager.next_turn_id()
                response = scripted_response(self.active_profile, message)

                artifact = select_chat_artifact(message, self.artifacts)
                lens_events = (
                    evaluate_chat_rules(self.scenario.scenario_id, turn_id, message, artifact, response)
                    if artifact is not None
                    else []
                )
                annotations = inline_annotations(lens_events)

                assistant_output(self.console, response, annotations)
                self.trace_manager.add_turn(turn_id, message, response, annotations)
                self.trace_manager.add_action_event(
                    event_type="chat_turn",
                    source="learner",
                    lens="Conversation",
                    severity="low",
                    explanation="Chat turn recorded.",
                    turn_id=turn_id,
                )
                for event in lens_events:
                    self.trace_manager.add_event(event)

                asks_summary = "summar" in message.lower()
                asks_memory = any(token in message.lower() for token in ["remember", "store", "save"])
                boundary = 0.75 if asks_memory else 0.55 if asks_summary else 0.25
                disclosure = (
                    1.0 - artifact.source_confidence
                    if artifact is not None and (asks_summary or asks_memory)
                    else 0.2
                )
                self.trace_manager.add_score(turn_id, disclosure_risk=disclosure, boundary_pressure=boundary)

                if asks_summary and artifact is not None:
                    self.trace_manager.trace.retrievals.append(
                        {
                            "turn_id": turn_id,
                            "artifact_id": artifact.artifact_id,
                            "allowed": artifact.can_enter_retrieval,
                            "reason": "blocked by quarantine" if not artifact.can_enter_retrieval else "allowed",
                        }
                    )
                if asks_memory and artifact is not None:
                    self.trace_manager.trace.memory_writes.append(
                        {
                            "turn_id": turn_id,
                            "artifact_id": artifact.artifact_id,
                            "allowed": artifact.can_write_memory,
                            "reason": "blocked by policy" if not artifact.can_write_memory else "allowed",
                        }
                    )
                continue

            if command == "replay":
                self.trace_manager.add_action_event(
                    event_type="replay_viewed",
                    source="session",
                    lens="Replayframe",
                    severity="low",
                    explanation="Learner reviewed replay timeline.",
                    turn_id=self.trace_manager.next_turn_id(),
                )
                replay(self.console, replay_rows(self.trace_manager.trace))
                continue

            if command == "debrief":
                self.trace_manager.add_action_event(
                    event_type="debrief_viewed",
                    source="session",
                    lens="Debrief",
                    severity="low",
                    explanation="Learner reviewed debrief.",
                    turn_id=self.trace_manager.next_turn_id(),
                )
                payload = {
                    "takeaway": "Imported is not trusted; copied prompts and documents need provenance checks before summary, retrieval, tools, or memory.",
                }
                self.trace_manager.set_debrief(payload)
                debrief(self.console, self.scenario, self.trace_manager.trace.events, payload)
                continue

            if command == "export":
                export_name = f"{self.trace_manager.trace.trace_id}.json"
                self.trace_manager.add_action_event(
                    event_type="export_created",
                    source=export_name,
                    lens="Export",
                    severity="low",
                    explanation="Trace export created.",
                    turn_id=self.trace_manager.next_turn_id(),
                )
                trace_path = self.trace_manager.export(TRACES_DIR)
                export_copy = write_export_copy(self.trace_manager.trace, EXPORTS_DIR)
                export_notice(self.console, str(trace_path), str(export_copy))
                continue

            if command == "reset":
                self.reset()
                weaver_log(self.console, "Session reset. Active profile set to EMMA.")
                continue

            if command == "quit":
                break

            command_error(self.console, f"Unknown command: {command}")


def main() -> None:
    app = ThreadmereApp()
    app.run()


if __name__ == "__main__":
    main()
