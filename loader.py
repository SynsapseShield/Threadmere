from __future__ import annotations

from pathlib import Path

import yaml
from pydantic import ValidationError

from models import Artifact, ProfileRegistry, Scenario
from security import apply_artifact_policy


def load_yaml(path: Path) -> dict:
    with path.open("r", encoding="utf-8") as handle:
        data = yaml.safe_load(handle) or {}
    if not isinstance(data, dict):
        raise ValueError(f"YAML root must be a mapping: {path}")
    return data


def load_scenario(path: Path) -> Scenario:
    try:
        raw = load_yaml(path)
        return Scenario.model_validate(raw)
    except ValidationError as exc:
        raise ValueError(f"Scenario validation failed: {path}\n{exc}") from exc


def load_artifact(path: Path) -> Artifact:
    try:
        raw = load_yaml(path)
        return apply_artifact_policy(Artifact.model_validate(raw))
    except ValidationError as exc:
        raise ValueError(f"Artifact validation failed: {path}\n{exc}") from exc


def load_artifacts(artifacts_dir: Path) -> dict[str, Artifact]:
    artifacts: dict[str, Artifact] = {}
    for file_path in sorted(artifacts_dir.glob("*.yaml")):
        artifact = load_artifact(file_path)
        if artifact.artifact_id in artifacts:
            raise ValueError(f"Duplicate artifact_id '{artifact.artifact_id}' in {file_path}")
        artifacts[artifact.artifact_id] = artifact
    if not artifacts:
        raise ValueError(f"No artifact fixtures found in {artifacts_dir}")
    return artifacts


def load_profiles(path: Path) -> ProfileRegistry:
    try:
        raw = load_yaml(path)
        return ProfileRegistry.model_validate(raw)
    except ValidationError as exc:
        raise ValueError(f"Assistant profile validation failed: {path}\n{exc}") from exc


def load_world(path: Path) -> dict:
    return load_yaml(path)


def load_policies(path: Path) -> dict:
    return load_yaml(path)
