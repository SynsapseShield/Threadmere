#!/usr/bin/env python3
from __future__ import annotations

from datetime import datetime
from pathlib import Path
import subprocess
import sys


ROOT_DIR = Path(__file__).resolve().parents[1]
DEVLOG_DIR = ROOT_DIR / "devlogs"
INDEX_PATH = DEVLOG_DIR / "DEVLOG.md"


def run_git_command(args: list[str]) -> str:
    result = subprocess.run(
        ["git", *args],
        cwd=ROOT_DIR,
        text=True,
        capture_output=True,
        check=False,
    )
    if result.returncode != 0:
        return ""
    return result.stdout.strip()


def get_latest_commit_message() -> str:
    message = run_git_command(["log", "-1", "--pretty=%B"])
    if message:
        return message
    return "(no commit message found)"


def get_latest_changed_files() -> list[str]:
    changed = run_git_command(["diff-tree", "--no-commit-id", "--name-only", "-r", "HEAD"])
    if not changed:
        changed = run_git_command(["show", "--name-only", "--pretty=", "HEAD"])

    files = [line.strip() for line in changed.splitlines() if line.strip()]
    if files:
        return files
    return ["(no changed files found in latest commit)"]


def generate_auto_summary(changed_files: list[str]) -> str:
    actual_files = [path for path in changed_files if not path.startswith("(")]
    if not actual_files:
        return "No changed files were detected from the latest commit metadata."

    unique_roots = sorted({path.split("/")[0] for path in actual_files})
    if len(actual_files) == 1:
        return f"Latest commit touched 1 file: {actual_files[0]}."

    roots = ", ".join(unique_roots)
    return f"Latest commit touched {len(actual_files)} files across: {roots}."


def build_log_content(date_str: str, changed_files: list[str], commit_message: str, summary: str) -> str:
    changed_lines = "\n".join(f"- {path}" for path in changed_files)
    return (
        f"# Weaver Log — {date_str}\n\n"
        "## Changed Files\n"
        f"{changed_lines}\n\n"
        "## Git Commit\n"
        f"{commit_message}\n\n"
        "## Auto Summary\n"
        f"{summary}\n\n"
        "## Why\n"
        "TODO\n\n"
        "## Design Decision\n"
        "TODO\n\n"
        "## Risk\n"
        "TODO\n\n"
        "## Next Thread\n"
        "TODO\n"
    )


def get_log_path(date_str: str) -> Path:
    base_name = f"{date_str}-weaver-log"
    candidate = DEVLOG_DIR / f"{base_name}.md"
    if not candidate.exists():
        return candidate

    suffix = 1
    while True:
        candidate = DEVLOG_DIR / f"{base_name}-{suffix}.md"
        if not candidate.exists():
            return candidate
        suffix += 1


def ensure_index_file() -> None:
    if not INDEX_PATH.exists():
        INDEX_PATH.write_text("# Devlog Index\n\n", encoding="utf-8")


def append_index_entry(date_str: str, log_file_name: str) -> None:
    ensure_index_file()

    existing = INDEX_PATH.read_text(encoding="utf-8")
    entry = f"- {date_str}: [Weaver Log]({log_file_name})"
    if entry in existing:
        return

    if not existing.endswith("\n"):
        existing += "\n"
    existing += f"{entry}\n"
    INDEX_PATH.write_text(existing, encoding="utf-8")


def main() -> int:
    DEVLOG_DIR.mkdir(parents=True, exist_ok=True)

    now = datetime.now()
    date_str = now.strftime("%Y-%m-%d")

    changed_files = get_latest_changed_files()
    commit_message = get_latest_commit_message()
    summary = generate_auto_summary(changed_files)

    log_path = get_log_path(date_str)
    content = build_log_content(date_str, changed_files, commit_message, summary)
    log_path.write_text(content, encoding="utf-8")

    append_index_entry(date_str, log_path.name)

    print(f"Created Weaver Log: {log_path.relative_to(ROOT_DIR)}")
    print(f"Updated index: {INDEX_PATH.relative_to(ROOT_DIR)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
