"""Command-line validator for action records.

One command, one job: take a record as JSON, say whether it is valid,
and say exactly why not. Output is a plain-text contract for CI logs —
one error per line, meaningful exit codes (see ADR 0003):

    0  record is valid
    1  record violates the schema
    2  input is unreadable or not JSON
"""

import argparse
import json
import sys
from pathlib import Path

from pydantic import ValidationError

from action_record.schema import ActionRecord

EXIT_VALID = 0
EXIT_INVALID = 1
EXIT_UNREADABLE = 2


def _format_error_line(error: dict) -> str:
    """Render one Pydantic error as one line: field path, constraint, message.

    Pydantic's message already lists permitted values for literal errors,
    so the line carries everything a reader needs to fix the record.
    """
    loc = ".".join(str(part) for part in error["loc"]) or "(record)"
    return f"{loc}: {error['type']}: {error['msg']}"


def _read_input(path: str) -> str:
    """Return the raw text of the record, from a file or stdin ('-')."""
    if path == "-":
        return sys.stdin.read()
    return Path(path).read_text(encoding="utf-8")


def validate(path: str) -> int:
    """Validate one record and print the result; return the exit code."""
    try:
        raw = _read_input(path)
    except OSError as exc:
        reason = exc.strerror or str(exc)
        print(f"error: cannot read {path}: {reason}", file=sys.stderr)
        return EXIT_UNREADABLE

    try:
        json.loads(raw)
    except json.JSONDecodeError as exc:
        print(f"error: not valid JSON: {exc}", file=sys.stderr)
        return EXIT_UNREADABLE

    try:
        record = ActionRecord.model_validate_json(raw)
    except ValidationError as exc:
        for error in exc.errors():
            print(_format_error_line(error))
        return EXIT_INVALID

    print(f"valid: {record.intent}")
    return EXIT_VALID


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="action-record",
        description="Validate action records against the schema.",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)
    validate_parser = subparsers.add_parser(
        "validate", help="validate a record JSON file ('-' reads stdin)"
    )
    validate_parser.add_argument(
        "path", help="path to a record JSON file, or '-' to read stdin"
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    return validate(args.path)


if __name__ == "__main__":
    sys.exit(main())
