# ADR 0003: The validator's output is a plain-text contract

## Status

Accepted

## Context

The validator's primary consumer is a CI log, not a human at a
terminal. A CI log cannot render color, spinners, or box-drawing
characters, and downstream tooling greps it. Whatever the validator
prints is therefore an interface other systems will depend on, and it
must stay stable and machine-scannable.

## Decision

`action-record validate` emits plain text with meaningful exit codes:

- **Valid** — one line, `valid: <intent>`, exit 0.
- **Invalid** — one Pydantic error per line on stdout, formatted as
  `<field.path>: <constraint>: <message>` (the message lists permitted
  values where applicable), exit 1.
- **Unreadable or not JSON** — one `error: ...` line on stderr, exit 2.

The CLI is built on stdlib argparse. No click, no rich, no color, no
progress output — nothing that varies with TTY detection.

Exit codes separate "the record is wrong" (1) from "you never gave me
a record" (2), so a pipeline can distinguish a schema regression from
a broken artifact path.

## Consequences

- CI can gate on the exit code alone and grep failures by field name.
- One error per line means a diff of two runs shows exactly which
  violations appeared or disappeared.
- The output format is now a contract: changing it is a breaking
  change and warrants an ADR, not a drive-by edit.
