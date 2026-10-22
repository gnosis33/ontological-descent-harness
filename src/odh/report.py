"""Local, immutable-per-run research artifacts."""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4
from typing import Any


def markdown_report(run: dict[str, Any]) -> str:
    lines = [
        "# Ontological Descent Experiment",
        "",
        f"**Problem:** {run['problem']}",
        "",
        f"**Provider:** {run['provider']}",
        "",
        f"**Created (UTC):** {run['created_utc']}",
        "",
        "**Status: UNVERIFIED.** All proposals, critiques, and scores are model-generated.",
        "No independent proof, novelty search, experiment, or outcome comparison is implied.",
        "",
        "## Baseline",
        "",
        "~~~json",
        json.dumps(run["baseline"], indent=2, ensure_ascii=False),
        "~~~",
        "",
        "## Ontology audit",
        "",
        "~~~json",
        json.dumps(run["audit"], indent=2, ensure_ascii=False),
        "~~~",
        "",
        "## Candidate hypotheses",
    ]
    for trial in run["trials"]:
        lines.extend([
            "",
            f"### Candidate {trial['index']}: {trial['candidate']['name']}",
            "",
            f"**Operator:** {trial['operator']}",
            "",
            "**Provisional proposal-quality score:** "
            f"{trial['provisional_total']}/25 (not empirical performance)",
            "",
            "#### Candidate",
            "",
            "~~~json",
            json.dumps(trial["candidate"], indent=2, ensure_ascii=False),
            "~~~",
            "",
            "#### Adversarial critique",
            "",
            "~~~json",
            json.dumps(trial["critique"], indent=2, ensure_ascii=False),
            "~~~",
            "",
            "#### Provisional evaluation",
            "",
            "~~~json",
            json.dumps(trial["evaluation"], indent=2, ensure_ascii=False),
            "~~~"
        ])
    lines.extend([
        "",
        "## Provisional ranking",
        "",
        ", ".join(f"Candidate {i}" for i in run["provisional_ranking"]),
        "",
        "The ranking is not scientific evidence. Test hypotheses against an",
        "independently evaluated baseline before claiming a benefit.",
        "",
    ])
    return "\n".join(lines)


def save_run(run: dict[str, Any], root: Path) -> Path:
    """Never overwrite an earlier research record."""
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    path = root / (timestamp + "-" + uuid4().hex[:8])
    path.mkdir(parents=True, exist_ok=False)
    (path / "report.json").write_text(
        json.dumps(run, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    (path / "report.md").write_text(markdown_report(run), encoding="utf-8")
    return path
