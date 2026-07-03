"""Generate examples/record.json from a real kubeconform run.

Runs kubeconform against the vendored DRA manifest, wraps the run in
an ActionRecord, writes it as JSON, and validates the result through
the real CLI (`action-record validate`) — the public contract, not an
imported function. The committed record.json is the output of this
script, never hand-written (see ADR 0004).

Usage: python examples/generate_record.py [output-path]
"""

import re
import subprocess
import sys
from pathlib import Path

from action_record import ActionRecord, Evidence

EXAMPLES_DIR = Path(__file__).parent
FIXTURE = EXAMPLES_DIR / "fixtures" / "dra-deviceclass-resourceclaim.yaml"
PROVENANCE = EXAMPLES_DIR / "fixtures" / "PROVENANCE.md"


def provenance_commit() -> str:
    """Return the pinned source SHA recorded in PROVENANCE.md."""
    match = re.search(
        r"^Commit: ([0-9a-f]{40})$", PROVENANCE.read_text(), flags=re.MULTILINE
    )
    if match is None:
        raise SystemExit(f"error: no commit SHA found in {PROVENANCE}")
    return match.group(1)


def run_kubeconform() -> str:
    """Validate the fixture with kubeconform; return its summary line."""
    result = subprocess.run(
        ["kubeconform", "-summary", str(FIXTURE)],
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        raise SystemExit(
            f"error: kubeconform failed (exit {result.returncode}):\n"
            f"{result.stdout}{result.stderr}"
        )
    return result.stdout.strip()


def build_record(kubeconform_summary: str) -> ActionRecord:
    fixture_rel = FIXTURE.relative_to(EXAMPLES_DIR.parent)
    return ActionRecord(
        intent="validate vendored manifest against Kubernetes schemas",
        actor="examples/generate_record.py",
        context_used=[
            str(fixture_rel),
            f"examples/fixtures/PROVENANCE.md@{provenance_commit()}",
        ],
        proposed_action=f"Run kubeconform -summary against {fixture_rel}",
        tool_called="kubeconform",
        policy_decision="allowed",
        change_summary="Validated the vendored DRA manifest against Kubernetes "
        "schemas; every resource passed.",
        evidence=Evidence(
            tests=f"kubeconform -summary {fixture_rel} — {kubeconform_summary}",
            risk="low",
            blast_radius="none — read-only validation",
            rollback="n/a — no change made",
        ),
        outcome="applied",
    )


def main(argv: list[str]) -> int:
    output = Path(argv[1]) if len(argv) > 1 else EXAMPLES_DIR / "record.json"
    record = build_record(run_kubeconform())
    output.write_text(record.model_dump_json(indent=2) + "\n", encoding="utf-8")

    result = subprocess.run(
        ["action-record", "validate", str(output)],
        capture_output=True,
        text=True,
    )
    print(result.stdout, end="")
    print(result.stderr, end="", file=sys.stderr)
    return result.returncode


if __name__ == "__main__":
    sys.exit(main(sys.argv))
