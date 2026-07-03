# 0001. Record shape and field set

## Status

Accepted

## Context

Agent work today is reconstructed after the fact from transcripts and
log dumps. Reviewers need one record answering: what was the goal, who
acted, what was consulted, what was proposed, what was decided, and
what evidence supports it. A free-form log holds all of that but
verifies none of it.

## Decision

An action record is a flat, small set of required fields with one nested
structure:

- `intent`, `actor`, `context_used` — provenance: goal, agent, and the
  references actually consulted.
- `proposed_action`, `tool_called`, `policy_decision` — the action and
  its gate. `policy_decision` is a closed enum: allowed,
  requires_human_review, denied.
- `change_summary` — exactly one reviewer-evaluable sentence.
- `evidence` — structured, not prose: tests run, a risk enum,
  blast radius, and a rollback path. All four required.
- `outcome` — lifecycle enum; `created_at` — UTC, auto-populated.

Deliberately left out: free-form log dumps, raw tool output, diffs,
and timing/telemetry — those belong in transcript storage. Evidence is
a structured model rather than a text blob so that "no rollback plan"
is a validation error, not a discovery during an incident.

## Consequences

Records are small enough to review at a glance and strict enough to
reject incomplete evidence. Anything outside the field set has no home
here by design; new needs require a schema change and an ADR.
