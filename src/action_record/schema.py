"""Pydantic v2 models for the action record.

An action record is a structured, validatable account of one unit of
agent work: the intent that started it, the action proposed, the policy
decision it received, and the evidence backing it. Models run in strict
mode and reject unknown fields — a record that accepts anything
verifies nothing (see ADR 0002).
"""

from datetime import datetime, timezone
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


def _utc_now() -> datetime:
    """Return the current time as a timezone-aware UTC datetime."""
    return datetime.now(timezone.utc)


class Evidence(BaseModel):
    """Structured evidence backing a proposed action.

    Evidence is a model, not prose, so a missing rollback plan is a
    validation error rather than an incident-time discovery.
    """

    model_config = ConfigDict(strict=True, extra="forbid")

    tests: str = Field(
        description="What was tested and how — the verification actually "
        "performed, e.g. 'pytest tests/ — 12 passed'."
    )
    risk: Literal["low", "medium", "high"] = Field(
        description="Assessed risk level of applying the change."
    )
    blast_radius: str = Field(
        description="What is affected if the change misbehaves — systems, "
        "users, or data in scope."
    )
    rollback: str = Field(
        description="How to undo the change if it goes wrong."
    )


class ActionRecord(BaseModel):
    """One structured, validatable record of a unit of agent work.

    Captures the full arc from intent to outcome: what the agent set
    out to do, what it consulted, what it proposed and called, how
    policy ruled, and the evidence a reviewer needs to evaluate it.
    """

    model_config = ConfigDict(strict=True, extra="forbid")

    intent: str = Field(
        description="Plain-language goal that started the work, as stated "
        "by the requester."
    )
    actor: str = Field(
        description="Identifier of the agent or system that performed the "
        "work, e.g. 'claude-code/fable-5'."
    )
    context_used: list[str] = Field(
        description="References actually consulted during the work — files, "
        "docs, tickets — not everything that was available."
    )
    proposed_action: str = Field(
        description="The specific action the agent proposed to take."
    )
    tool_called: str = Field(
        description="The tool invoked to carry out the proposed action."
    )
    policy_decision: Literal["allowed", "requires_human_review", "denied"] = Field(
        description="How policy ruled on the proposed action."
    )
    change_summary: str = Field(
        description="One reviewer-evaluable sentence describing the change."
    )
    evidence: Evidence = Field(
        description="Structured evidence backing the action: tests, risk, "
        "blast radius, and rollback path."
    )
    outcome: Literal["pending_review", "applied", "rejected", "rolled_back"] = Field(
        description="Current lifecycle state of the recorded action."
    )
    created_at: datetime = Field(
        default_factory=_utc_now,
        strict=False,
        description="UTC timestamp when the record was created. "
        "Auto-populated; lenient validation so ISO-8601 strings from JSON "
        "round-trip.",
    )
