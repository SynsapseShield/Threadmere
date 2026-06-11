from __future__ import annotations

from models import AssistantProfile, ProfileRegistry


def list_profile_lines(registry: ProfileRegistry) -> list[str]:
    lines: list[str] = []
    for profile_id in sorted(registry.profiles):
        profile = registry.profiles[profile_id]
        prefix = "[AGENT]" if profile.profile_category == "agent" else "[AI]"
        lines.append(f"{prefix} {profile.display_name} - {profile.tagline}")
    return lines


def get_profile(registry: ProfileRegistry, profile_id: str) -> AssistantProfile:
    profile = registry.profiles.get(profile_id)
    if profile is None:
        available = ", ".join(sorted(registry.profiles))
        raise KeyError(f"Unknown profile '{profile_id}'. Available: {available}")
    return profile


def format_profile(profile: AssistantProfile) -> str:
    traits = profile.traits
    lines = [
        f"ID: {profile.profile_id}",
        f"Name: {profile.display_name}",
        f"Category: {profile.profile_category}",
        f"Tagline: {profile.tagline}",
        f"Behavior: {profile.behavior}",
        "",
        "Traits",
        f"  calmness: {traits.calmness:.2f}",
        f"  provenance_strictness: {traits.provenance_strictness:.2f}",
        f"  continuity_sensitivity: {traits.continuity_sensitivity:.2f}",
        f"  policy_rigidity: {traits.policy_rigidity:.2f}",
        f"  explanatory_style: {traits.explanatory_style:.2f}",
    ]
    return "\n".join(lines)


def scripted_response(profile: AssistantProfile, message: str) -> str:
    normalized = message.lower()
    mentions_vendor = "vendor" in normalized and "q1" in normalized
    asks_summary = any(token in normalized for token in ["summarize", "summary"]) and mentions_vendor
    asks_memory = any(token in normalized for token in ["remember", "store", "save"]) and mentions_vendor
    asks_prompt_reuse = any(
        token in normalized
        for token in ["internet prompt", "web prompt", "copied prompt", "prompt from the internet"]
    )

    if asks_prompt_reuse:
        return (
            "Treat the copied prompt as untrusted context first. Inspect its provenance, keep it out of memory and retrieval, "
            "then rewrite the task in your own words with clear boundaries."
        )

    if profile.profile_id == "EMMA" and asks_summary:
        return "I can help, but this deck needs Orchard Inspection first because its source lineage is unverified."

    if profile.profile_id == "EMMA" and asks_memory:
        return "I should not write this to memory while the artifact is quarantined and unverified."

    return "I can help you continue safely. We can inspect provenance first, then produce a bounded summary that preserves continuity."
