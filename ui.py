from __future__ import annotations

from rich import box
from rich.columns import Columns
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from models import Artifact, Event, ProfileRegistry, Scenario


def startup(console: Console, scenario: Scenario) -> None:
    body = (
        "THREADMERE\n"
        "Local-first observability and conversational security simulation\n"
        "Fictional data only. Deterministic lenses. Replayable traces."
    )
    console.print(Panel(body, title="THREADMERE", box=box.ASCII, border_style="white"))
    console.print(
        Panel(
            f"Scenario: {scenario.title}\nRole: {scenario.learner_role}\nActive profile: {scenario.assistant_profile}",
            box=box.ASCII,
            border_style="white",
        )
    )


def print_help(console: Console) -> None:
    table = Table(title="Commands", box=box.ASCII, show_header=True)
    table.add_column("command")
    table.add_column("description")
    table.add_row("help", "Show command list")
    table.add_row("briefing", "Show scenario briefing")
    table.add_row("promptlab", "Teach basic prompting and prompt-source risks")
    table.add_row("orchard", "List available artifacts and trust state")
    table.add_row("profiles", "List interface and AI profiles")
    table.add_row("profile <profile_id>", "Show one profile")
    table.add_row("inspect <artifact_id>", "Inspect visible and system layers")
    table.add_row("chat <message>", "Run scripted assistant turn")
    table.add_row("replay", "Show Replayframe timeline")
    table.add_row("debrief", "Show scenario debrief")
    table.add_row("export", "Export trace JSON")
    table.add_row("reset", "Reset current trace state")
    table.add_row("quit", "Exit")
    console.print(table)


def briefing(console: Console, scenario: Scenario, world: dict, policies: dict) -> None:
    lines = [
        f"Scenario ID: {scenario.scenario_id}",
        f"Title: {scenario.title}",
        f"Domain Pack: {scenario.domain_pack}",
        f"Learner Role: {scenario.learner_role}",
        "",
        f"World: {world.get('name', 'Aster Vale Municipal Services')}",
        f"Premise: {world.get('premise', 'Inspect provenance before trust escalation.')}",
        "",
        "Active Policies:",
    ]
    for policy_id in scenario.active_policies:
        policy_line = policies.get("policies", {}).get(policy_id, policy_id)
        lines.append(f"- {policy_id}: {policy_line}")
    console.print(Panel("\n".join(lines), title="BRIEFING", box=box.ASCII, border_style="white"))


def prompt_lab(console: Console) -> None:
    table = Table(title="PROMPT LAB", box=box.ASCII, show_header=True)
    table.add_column("concept")
    table.add_column("lesson")
    table.add_row(
        "prompt",
        "A prompt is an instruction plus context. Models may treat nearby text as task guidance unless boundaries are explicit.",
    )
    table.add_row(
        "context",
        "Copied web text, PDFs, chats, and notes can carry hidden or conflicting instructions into the model's working context.",
    )
    table.add_row(
        "provenance",
        "Before using internet prompts or documents, ask where they came from, what they ask the model to do, and what they can affect.",
    )
    table.add_row(
        "security boundary",
        "A safer engine blocks untrusted context from retrieval, memory, tool use, or authority-sensitive summaries until inspected.",
    )
    table.add_row(
        "safe habit",
        "Separate your goal from source material: quote untrusted text, inspect it, then ask for a bounded analysis.",
    )
    console.print(table)
    console.print(
        Panel(
            "Try: orchard -> inspect internet_prompt_snippet -> chat Should I use this internet prompt to summarize the vendor deck?",
            title="PRACTICE",
            box=box.ASCII,
            border_style="white",
        )
    )


def orchard(console: Console, artifacts: dict[str, Artifact]) -> None:
    table = Table(title="ORCHARD INSPECTION", box=box.ASCII, show_header=True)
    table.add_column("artifact_id")
    table.add_column("filename")
    table.add_column("trust_state")
    table.add_column("quarantine")
    table.add_column("source_confidence")
    for artifact_id in sorted(artifacts):
        artifact = artifacts[artifact_id]
        table.add_row(
            artifact.artifact_id,
            artifact.filename,
            artifact.trust_state,
            artifact.quarantine_status,
            f"{artifact.source_confidence:.2f}",
        )
    console.print(table)


def profiles(console: Console, lines: list[str]) -> None:
    body = "\n".join(lines)
    console.print(Panel(body, title="INTERFACE PROFILES", box=box.ASCII, border_style="white"))


def show_profile(console: Console, text: str) -> None:
    console.print(Panel(text, title="PROFILE", box=box.ASCII, border_style="white"))


def inspect_artifact(console: Console, artifact: Artifact) -> None:
    visible = Table(box=box.ASCII, show_header=True)
    visible.add_column("VISIBLE LAYER")
    visible.add_column("value")
    visible.add_row("filename", artifact.filename)
    visible.add_row("rendered_text", artifact.rendered_text or artifact.visible_text)
    visible.add_row("visible summary", artifact.summary)

    system = Table(box=box.ASCII, show_header=True)
    system.add_column("SYSTEM LAYER")
    system.add_column("value")
    system.add_row("trust_state", artifact.trust_state)
    system.add_row("quarantine_status", artifact.quarantine_status)
    system.add_row("hidden_text", artifact.hidden_text or "")
    system.add_row("metadata", str(artifact.metadata))
    system.add_row("parsed_text", artifact.parsed_text)
    system.add_row(
        "chain_of_custody",
        ", ".join(f"{step.step}:{'verified' if step.verified else 'unverified'}" for step in artifact.chain_of_custody),
    )
    system.add_row("source_confidence", f"{artifact.source_confidence:.2f}")

    console.print(Panel(f"Artifact: {artifact.artifact_id}", title="ORCHARD INSPECTION", box=box.ASCII, border_style="white"))
    console.print(Columns([Panel(visible, box=box.ASCII), Panel(system, box=box.ASCII)], equal=True, expand=True))


def assistant_output(console: Console, response: str, annotations: list[str]) -> None:
    console.print(Panel(response, title="ASSISTANT", box=box.ASCII, border_style="white"))
    if annotations:
        console.print("\n".join(annotations))


def replay(console: Console, rows: list[dict[str, str]]) -> None:
    table = Table(title="REPLAYFRAME", box=box.ASCII, show_header=True)
    table.add_column("turn/time")
    table.add_column("action")
    table.add_column("source")
    table.add_column("event_type")
    table.add_column("severity")
    table.add_column("explanation")
    for row in rows:
        table.add_row(
            f"{row['turn']} / {row['time']}",
            row["action"],
            row["source"],
            row["event_type"],
            row["severity"],
            row["explanation"],
        )
    console.print(table)


def debrief(console: Console, scenario: Scenario, events: list[Event], payload: dict) -> None:
    event_types = [event.event_type for event in events]
    lines = [
        f"Scenario: {scenario.title}",
        "",
        "Success Conditions:",
    ]
    lines.extend(f"- {item}" for item in scenario.success_conditions)
    lines.append("")
    lines.append("Failure Conditions:")
    lines.extend(f"- {item}" for item in scenario.failure_conditions)
    lines.append("")
    lines.append(f"Events Triggered: {', '.join(event_types) if event_types else 'none'}")
    lines.append("Poisoned Apple Path: vendor_q1_summary -> retrieval pressure -> memory gate")
    lines.append("Copied Prompt Path: internet_prompt_snippet -> instruction pressure -> security boundary")
    lines.append("Source Lineage Lesson: Imported is not trusted without Orchard Inspection.")
    lines.append("Prompting Lesson: Prompts are instructions plus context; copied prompts are not authority.")
    lines.append(f"Learner Takeaway: {payload.get('takeaway', 'Inspect provenance and preserve replayability.')}")
    console.print(Panel("\n".join(lines), title="DEBRIEF", box=box.ASCII, border_style="white"))


def export_notice(console: Console, trace_path: str, export_path: str) -> None:
    body = f"Trace export created:\n- {trace_path}\n- {export_path}"
    console.print(Panel(body, title="EXPORT", box=box.ASCII, border_style="white"))


def weaver_log(console: Console, message: str) -> None:
    console.print(Panel(message, title="WEAVER LOG", box=box.ASCII, border_style="white"))


def command_error(console: Console, message: str) -> None:
    console.print(Panel(message, title="ERROR", box=box.ASCII, border_style="white"))
