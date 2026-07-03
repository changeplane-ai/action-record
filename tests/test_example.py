"""Keeps the example honest: the generator must produce a CLI-valid record."""

import subprocess
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent


def test_regenerated_record_passes_cli_validation(tmp_path):
    output = tmp_path / "record.json"

    result = subprocess.run(
        ["uv", "run", "python", "examples/generate_record.py", str(output)],
        capture_output=True,
        text=True,
        cwd=PROJECT_ROOT,
    )

    assert result.returncode == 0, (
        f"generator must exit 0 (CLI validation passed), got "
        f"{result.returncode}: {result.stdout}{result.stderr}"
    )
    assert result.stdout.startswith("valid: "), (
        f"generator must echo the CLI's 'valid:' line, got: {result.stdout!r}"
    )
    assert output.exists(), "generator must write the record where told"
