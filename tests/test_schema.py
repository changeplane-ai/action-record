"""Schema validation tests: round-trip fidelity and strict rejection."""

import pytest
from pydantic import ValidationError

from action_record import ActionRecord, Evidence


def valid_record_kwargs() -> dict:
    """A complete, valid set of ActionRecord fields."""
    return {
        "intent": "Scaffold the action-record repo with schema and tests",
        "actor": "claude-code/fable-5",
        "context_used": ["prompt-1", "docs/adr/0001-record-shape-and-field-set.md"],
        "proposed_action": "Write src/action_record/schema.py with strict Pydantic v2 models",
        "tool_called": "Write",
        "policy_decision": "allowed",
        "change_summary": "Adds the ActionRecord schema with strict validation and structured evidence.",
        "evidence": Evidence(
            tests="pytest tests/test_schema.py",
            risk="low",
            blast_radius="New repo only; no existing consumers.",
            rollback="git revert the schema commit.",
        ),
        "outcome": "pending_review",
    }


def test_round_trip_preserves_record():
    """construct -> JSON -> parse yields an equal record."""
    record = ActionRecord(**valid_record_kwargs())
    parsed = ActionRecord.model_validate_json(record.model_dump_json())
    assert parsed == record, "record must survive a JSON round-trip unchanged"


def test_unknown_field_rejected():
    with pytest.raises(ValidationError) as exc_info:
        ActionRecord(**valid_record_kwargs(), log_dump="raw transcript text")
    error = exc_info.value.errors()[0]
    assert error["loc"] == ("log_dump",), (
        f"expected the error to name field 'log_dump', got loc={error['loc']}"
    )
    assert error["type"] == "extra_forbidden", (
        f"expected constraint 'extra_forbidden' (unknown fields rejected), "
        f"got {error['type']!r}"
    )


def test_missing_required_field_rejected():
    kwargs = valid_record_kwargs()
    del kwargs["change_summary"]
    with pytest.raises(ValidationError) as exc_info:
        ActionRecord(**kwargs)
    error = exc_info.value.errors()[0]
    assert error["loc"] == ("change_summary",), (
        f"expected the error to name field 'change_summary', got loc={error['loc']}"
    )
    assert error["type"] == "missing", (
        f"expected constraint 'missing' (field is required), got {error['type']!r}"
    )


def test_invalid_policy_decision_rejected():
    kwargs = valid_record_kwargs()
    kwargs["policy_decision"] = "maybe"
    with pytest.raises(ValidationError) as exc_info:
        ActionRecord(**kwargs)
    error = exc_info.value.errors()[0]
    assert error["loc"] == ("policy_decision",), (
        f"expected the error to name field 'policy_decision', got loc={error['loc']}"
    )
    assert error["type"] == "literal_error", (
        f"expected constraint 'literal_error' (value not in allowed set), "
        f"got {error['type']!r}"
    )
    assert "allowed" in error["msg"] and "requires_human_review" in error["msg"], (
        "error message must list the permitted policy_decision values"
    )
