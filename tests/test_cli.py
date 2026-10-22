"""CLI smoke test using deterministic fixture data only."""
from pathlib import Path

from odh.cli import main


def test_fixture_cli_writes_both_formats(tmp_path: Path):
    code = main([
        "run", "--provider", "fixture", "--problem", "Test problem.",
        "--candidates", "2", "--output-dir", str(tmp_path)
    ])
    assert code == 0
    created = list(tmp_path.iterdir())
    assert len(created) == 1
    assert (created[0] / "report.json").exists()
    assert (created[0] / "report.md").exists()
