# 0002. Pydantic v2 with strict mode and unknown-field rejection

## Status

Accepted

## Context

The record's value is that a valid instance is trustworthy. Lax parsing
undermines that in two ways: type coercion lets near-miss data through
(the string "true" becoming a boolean, an int becoming a string), and
ignored unknown fields let producers believe they recorded something
the schema silently dropped. A record that accepts anything verifies
nothing.

## Decision

Pydantic v2 with `strict=True` and `extra="forbid"` on every model.

- Strict mode: values must already be the declared type; no coercion.
  The one carve-out is `created_at`, validated leniently so ISO-8601
  strings from JSON round-trip correctly.
- `extra="forbid"`: an unknown field is a hard error, not a warning.
  Misspelled fields and schema drift surface at write time, at the
  producer, instead of at read time, at the reviewer.
- Enums are `Literal` types so invalid values name the field and the
  allowed set in the error.

## Consequences

Producers must emit exactly the schema — stricter integration work up
front, but every stored record is known-complete and known-typed.
Schema evolution is explicit: adding a field is a versioned change,
never a silent one.
