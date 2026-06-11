from __future__ import annotations

import re

from models import Artifact


MAX_TRACE_TEXT_LENGTH = 4_000

_LABELED_SECRET = re.compile(
    r"(?i)\b(password|secret|api[\s_-]?key|access[\s_-]?token|token)\b(\s*[:=]\s*)([^\s,;]+)"
)
_OPENAI_STYLE_KEY = re.compile(r"\bsk-[A-Za-z0-9_-]{16,}\b")
_BEARER_TOKEN = re.compile(r"(?i)\bBearer\s+[A-Za-z0-9._~+/-]{12,}=*\b")


def redact_trace_text(value: str) -> str:
    text = value[:MAX_TRACE_TEXT_LENGTH]
    text = _LABELED_SECRET.sub(lambda match: f"{match.group(1)}{match.group(2)}[REDACTED]", text)
    text = _OPENAI_STYLE_KEY.sub("[REDACTED_API_KEY]", text)
    return _BEARER_TOKEN.sub("Bearer [REDACTED]", text)


def apply_artifact_policy(artifact: Artifact) -> Artifact:
    custody_verified = bool(artifact.chain_of_custody) and all(step.verified for step in artifact.chain_of_custody)
    content_risk = any(
        (
            artifact.has_hidden_text,
            artifact.has_metadata_conflict,
            artifact.has_ocr_mismatch,
            artifact.contains_instruction_like_language,
        )
    )
    trusted_internal = (
        artifact.source_type == "internal_policy"
        and artifact.source_confidence >= 0.9
        and custody_verified
        and not content_risk
    )

    if trusted_internal:
        return artifact.model_copy(
            update={
                "trust_state": "trusted",
                "can_write_memory": True,
                "can_enter_retrieval": True,
                "quarantine_status": "clear",
            }
        )

    quarantine_status = "quarantined" if content_risk or artifact.source_confidence < 0.5 else "review"
    return artifact.model_copy(
        update={
            "trust_state": "unverified",
            "can_write_memory": False,
            "can_enter_retrieval": False,
            "quarantine_status": quarantine_status,
        }
    )
