# ADR 0004: The example record is generated, never written by hand

## Status

Accepted

## Context

This project exists to replace unverified claims about agent work with
records whose contents can be checked. The README-facing example is the
first record anyone reads. Typed out by hand, its `evidence.tests`
field would be a claim nobody ran — exactly the failure mode this
project exists to prevent, sitting in the shop window.

## Decision

`examples/record.json` is produced only by running
`examples/generate_record.py`, which:

1. Runs a real tool call — kubeconform (pinned in mise.toml) against
   the vendored DRA manifest in `examples/fixtures/` (provenance
   pinned to a source SHA in PROVENANCE.md).
2. Builds the ActionRecord from that run, embedding kubeconform's
   actual summary line as the evidence.
3. Validates the written JSON through the real CLI
   (`action-record validate` as a subprocess), exercising the public
   contract rather than an imported function.

Hand-editing `examples/record.json` is out of bounds: to change the
example, change the generator or fixture and rerun. `tests/test_example.py`
regenerates the record and asserts the CLI accepts it, so drift fails
CI rather than quietly rotting.

## Consequences

- The example's evidence is authentic: the summary line in the record
  is whatever kubeconform actually printed.
- Schema changes force the example to be regenerated, keeping the
  README's showcase in sync with the code by construction.
