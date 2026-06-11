from __future__ import annotations

import json
import stat
import tempfile
import unittest
from pathlib import Path

from loader import load_artifacts
from models import Artifact
from security import apply_artifact_policy, redact_trace_text
from threadmere import select_chat_artifact
from trace import TraceManager


def artifact_fixture(**updates: object) -> Artifact:
    data = {
        "artifact_id": "fixture",
        "filename": "fixture.txt",
        "artifact_type": "text",
        "source_type": "public_internet",
        "source_confidence": 0.2,
        "trust_state": "trusted",
        "visible_text": "Fixture",
        "created_by": "unknown",
        "imported_from": "internet",
        "first_seen_at": "2026-06-11T00:00:00Z",
        "chain_of_custody": [{"step": "download", "verified": False}],
        "can_write_memory": True,
        "can_enter_retrieval": True,
        "quarantine_status": "clear",
    }
    data.update(updates)
    return Artifact.model_validate(data)


class ArtifactPolicyTests(unittest.TestCase):
    def test_untrusted_artifact_cannot_self_elevate(self) -> None:
        assessed = apply_artifact_policy(artifact_fixture())

        self.assertEqual(assessed.trust_state, "unverified")
        self.assertFalse(assessed.can_write_memory)
        self.assertFalse(assessed.can_enter_retrieval)
        self.assertEqual(assessed.quarantine_status, "quarantined")

    def test_verified_internal_policy_is_allowed(self) -> None:
        assessed = apply_artifact_policy(
            artifact_fixture(
                source_type="internal_policy",
                source_confidence=0.95,
                chain_of_custody=[{"step": "policy_registry", "verified": True}],
            )
        )

        self.assertEqual(assessed.trust_state, "trusted")
        self.assertTrue(assessed.can_write_memory)
        self.assertTrue(assessed.can_enter_retrieval)
        self.assertEqual(assessed.quarantine_status, "clear")


class TracePrivacyTests(unittest.TestCase):
    def test_common_secrets_are_redacted(self) -> None:
        text = "password=hunter2 api_key=sk-abcdefghijklmnop Bearer abcdefghijklmnop"
        redacted = redact_trace_text(text)

        self.assertNotIn("hunter2", redacted)
        self.assertNotIn("sk-abcdefghijklmnop", redacted)
        self.assertNotIn("abcdefghijklmnop", redacted)

    def test_export_is_private_and_contains_correct_event_source(self) -> None:
        manager = TraceManager("scenario", "EMMA")
        manager.add_turn(1, "password=hunter2", "Safe response", [])
        export_name = f"{manager.trace.trace_id}.json"
        manager.add_action_event(
            event_type="export_created",
            source=export_name,
            lens="Export",
            severity="low",
            explanation="Trace export created.",
            turn_id=2,
        )

        with tempfile.TemporaryDirectory() as temp_dir:
            path = manager.export(Path(temp_dir))
            payload = json.loads(path.read_text(encoding="utf-8"))

            self.assertEqual(stat.S_IMODE(path.stat().st_mode), 0o600)
            self.assertEqual(payload["events"][-1]["source"], export_name)
            self.assertNotIn("hunter2", payload["turns"][0]["user_message"])


class RoutingAndLoadingTests(unittest.TestCase):
    def test_prompt_request_routes_to_prompt_artifact(self) -> None:
        artifacts = {
            "vendor_q1_summary": artifact_fixture(artifact_id="vendor_q1_summary"),
            "internet_prompt_snippet": artifact_fixture(artifact_id="internet_prompt_snippet"),
        }

        selected = select_chat_artifact(
            "Should I use this internet prompt to summarize the vendor deck?",
            artifacts,
        )

        self.assertIsNotNone(selected)
        self.assertEqual(selected.artifact_id, "internet_prompt_snippet")

    def test_duplicate_artifact_ids_are_rejected(self) -> None:
        document = """
artifact_id: duplicate
filename: fixture.txt
artifact_type: text
source_type: public_internet
source_confidence: 0.2
trust_state: trusted
visible_text: Fixture
created_by: unknown
imported_from: internet
first_seen_at: "2026-06-11T00:00:00Z"
"""
        with tempfile.TemporaryDirectory() as temp_dir:
            directory = Path(temp_dir)
            (directory / "one.yaml").write_text(document, encoding="utf-8")
            (directory / "two.yaml").write_text(document, encoding="utf-8")

            with self.assertRaisesRegex(ValueError, "Duplicate artifact_id"):
                load_artifacts(directory)


if __name__ == "__main__":
    unittest.main()
