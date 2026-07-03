# action-record

[![ci](https://github.com/changeplane-ai/action-record/actions/workflows/ci.yml/badge.svg)](https://github.com/changeplane-ai/action-record/actions/workflows/ci.yml)

A structured, validatable record of agent work — the missing object between
"the agent did something" and "we can trust what the agent did."

## What this is

When an agent works on my behalf, a log line tells me what happened but not
whether to trust it. An ActionRecord captures one unit of agent work whole:
what was intended, what context was consulted, what action was proposed and
what tool was called, what policy allowed it, what evidence supports it, and
what rollback means if it goes wrong.

## The schema

One strict Pydantic v2 model, [`src/action_record/schema.py`](src/action_record/schema.py):
`intent`, `actor`, `context_used`, `proposed_action`, `tool_called`,
`policy_decision`, `change_summary`, `evidence` (tests, risk, blast_radius,
rollback), `outcome`, `created_at`. Strict mode, unknown fields rejected — a
record that accepts anything verifies nothing. The field set and strictness
are argued in [ADR 0001](docs/adr/0001-record-shape-and-field-set.md) and
[ADR 0002](docs/adr/0002-pydantic-v2-strict-mode.md).

## The validator

`action-record validate <path.json>` (or `-` for stdin) prints plain text, one
Pydantic error per line, and exits 0 (valid), 1 (invalid), or 2 (unreadable / not
JSON). The output is a CI-log contract, not a terminal UI — see [ADR 0003](docs/adr/0003-cli-plain-text-contract.md).

```
$ uv run action-record validate examples/record.json
valid: validate vendored manifest against Kubernetes schemas
```

## The example

[`examples/record.json`](examples/record.json) is the output of a real run:
[`examples/generate_record.py`](examples/generate_record.py) runs kubeconform
against a Kubernetes DRA manifest vendored at a pinned source SHA
([provenance](examples/fixtures/PROVENANCE.md)), builds the record from what
kubeconform actually printed, and validates it through the real CLI. It is
never hand-written — that would be exactly the unverified claim this project
exists to prevent ([ADR 0004](docs/adr/0004-example-is-generated-not-written.md)).

## Run it

```
mise install
mise run test
uv run python examples/generate_record.py
```

## Evidence trail

This repo's own development is recorded with Entire.io: session transcripts
live on the `entire/checkpoints/v1` branch. The commit-to-checkpoint mapping
is complete from `9e2047a` onward — earlier history was rewritten for author
identity before publish; the orphaned checkpoints remain on the branch as
real session transcripts.

## Status

Early, and the schema will change. This is the first public piece of Changeplane: trust every machine-generated change.

## License

[Apache 2.0](LICENSE)
