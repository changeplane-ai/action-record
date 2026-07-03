"""CLI contract tests: exit codes and plain-text output, via subprocess."""

import json
import subprocess
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent


def valid_record() -> dict:
    """A complete, valid ActionRecord as plain JSON-ready data."""
    return {
        "intent": "Add the validator CLI to action-record",
        "actor": "claude-code/fable-5",
        "context_used": ["prompt-2", "src/action_record/schema.py"],
        "proposed_action": "Write src/action_record/cli.py with a validate command",
        "tool_called": "Write",
        "policy_decision": "allowed",
        "change_summary": "Adds a plain-text validate command with meaningful exit codes.",
        "evidence": {
            "tests": "pytest tests/test_cli.py",
            "risk": "low",
            "blast_radius": "New CLI only; no existing consumers.",
            "rollback": "git revert the CLI commit.",
        },
        "outcome": "pending_review",
    }


def run_validate(path: str, stdin: str | None = None) -> subprocess.CompletedProcess:
    return subprocess.run(
        ["uv", "run", "action-record", "validate", path],
        input=stdin,
        capture_output=True,
        text=True,
        cwd=PROJECT_ROOT,
    )


def test_valid_file_exits_0_and_echoes_intent(tmp_path):
    record_path = tmp_path / "record.json"
    record_path.write_text(json.dumps(valid_record()))

    result = run_validate(str(record_path))

    assert result.returncode == 0, f"expected exit 0, got {result.returncode}: {result.stderr}"
    assert result.stdout == "valid: Add the validator CLI to action-record\n"


def test_valid_record_on_stdin_exits_0(tmp_path):
    result = run_validate("-", stdin=json.dumps(valid_record()))

    assert result.returncode == 0, f"expected exit 0, got {result.returncode}: {result.stderr}"
    assert result.stdout.startswith("valid: ")


def test_invalid_record_exits_1_and_names_field(tmp_path):
    record = valid_record()
    record["policy_decision"] = "maybe"
    del record["change_summary"]
    record_path = tmp_path / "record.json"
    record_path.write_text(json.dumps(record))

    result = run_validate(str(record_path))

    assert result.returncode == 1, f"expected exit 1, got {result.returncode}: {result.stderr}"
    lines = result.stdout.splitlines()
    assert len(lines) == 2, f"expected one line per error, got: {result.stdout!r}"
    assert any(line.startswith("policy_decision: ") for line in lines), (
        f"errors must name the failing field, got: {result.stdout!r}"
    )
    assert any(line.startswith("change_summary: missing") for line in lines), (
        f"errors must name the missing field and constraint, got: {result.stdout!r}"
    )
    policy_line = next(line for line in lines if line.startswith("policy_decision"))
    assert "requires_human_review" in policy_line, (
        f"literal errors must list permitted values, got: {policy_line!r}"
    )


def test_malformed_json_exits_2(tmp_path):
    record_path = tmp_path / "record.json"
    record_path.write_text("{not json")

    result = run_validate(str(record_path))

    assert result.returncode == 2, f"expected exit 2, got {result.returncode}"
    assert "not valid JSON" in result.stderr


def test_missing_file_exits_2(tmp_path):
    result = run_validate(str(tmp_path / "does-not-exist.json"))

    assert result.returncode == 2, f"expected exit 2, got {result.returncode}"
    assert "cannot read" in result.stderr
