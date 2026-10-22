"""CLI-backed reasoning providers and a deterministic offline fixture.

CLI logins are managed by the provider's own official tooling. ODH does not
read, store, or transmit authentication tokens directly.
"""
from __future__ import annotations

import json
import os
import shlex
import subprocess
import tempfile
from pathlib import Path
from typing import Protocol


class ProviderError(RuntimeError):
    """A local provider command failed or returned no response."""


class Provider(Protocol):
    name: str

    def complete(self, prompt: str) -> str:
        """Return the model's final textual response."""


def _command(name: str, default: str) -> list[str]:
    command = shlex.split(os.environ.get(name, default))
    if not command:
        raise ProviderError(f"{name} contains no executable")
    return command


class CodexCLI:
    name = "codex"

    def __init__(self, timeout: int = 300) -> None:
        self.timeout = timeout

    def complete(self, prompt: str) -> str:
        with tempfile.TemporaryDirectory(prefix="odh-codex-") as directory:
            final = Path(directory) / "final.txt"
            args = _command("ODH_CODEX_CMD", "codex") + [
                "exec", "--sandbox", "read-only", "--skip-git-repo-check",
                "--output-last-message", str(final), "-"
            ]
            _run(args, prompt, directory, self.timeout)
            if not final.is_file() or not final.read_text(encoding="utf-8").strip():
                raise ProviderError("Codex returned no final message")
            return final.read_text(encoding="utf-8")


class ClaudeCLI:
    name = "claude"

    def __init__(self, timeout: int = 300) -> None:
        self.timeout = timeout

    def complete(self, prompt: str) -> str:
        with tempfile.TemporaryDirectory(prefix="odh-claude-") as directory:
            args = _command("ODH_CLAUDE_CMD", "claude") + [
                "-p", "--permission-mode", "plan",
                "--output-format", "text"
            ]
            return _run(args, prompt, directory, self.timeout)


def _run(args: list[str], prompt: str, cwd: str, timeout: int) -> str:
    try:
        process = subprocess.run(
            args, input=prompt, text=True, capture_output=True,
            cwd=cwd, timeout=timeout, check=False
        )
    except FileNotFoundError as exc:
        raise ProviderError(f"Command not found: {args[0]}") from exc
    except subprocess.TimeoutExpired as exc:
        raise ProviderError(f"Provider exceeded {timeout}s timeout") from exc

    if process.returncode != 0:
        detail = (process.stderr or process.stdout).strip()[-1200:]
        raise ProviderError(f"{args[0]} exited with {process.returncode}: {detail}")
    return process.stdout.strip()


class FixtureProvider:
    """Synthetic data for offline smoke tests. NEVER scientific evidence."""

    name = "fixture"

    def complete(self, prompt: str) -> str:
        stage = prompt.splitlines()[0].removeprefix("ODH_ROLE=").strip()
        if stage == "baseline":
            return json.dumps({
                "approach": "Represent task steps as graph nodes and dependencies as edges.",
                "primitives": ["node", "edge"],
                "assumptions": ["The problem has stable node identities."],
                "strengths": ["Well-understood graph algorithms."],
                "limitations": ["Dynamic capabilities need graph rebuilding."]
            })
        if stage == "audit":
            return json.dumps({
                "primitives": ["node", "edge"],
                "assumptions": ["Node identities are stable."],
                "dependencies": ["Routing depends on predefined adjacency."],
                "invariants": ["Authorized tasks finish without forbidden operations."],
                "uncertainties": ["Can capability discovery outperform static routing?"]
            })
        if stage == "candidate":
            payload = json.loads(prompt.split("ODH_INPUT_JSON=", 1)[1])
            operator = payload["operator"]
            return json.dumps({
                "name": f"Synthetic {operator}",
                "operator": operator,
                "primitives": ["capability", "condition"],
                "derived": ["tasks as observations of capabilities"],
                "reduction": ["Recover graph nodes and edges when capability sets stay fixed."],
                "distinguishing_case": "A previously unknown tool arrives mid-execution.",
                "predicted_benefit": "Adapt routing without a prior static edge.",
                "falsifier": "A graph baseline adapts equally well at lower cost.",
                "assumptions": ["Capabilities can be inspected."]
            })
        if stage == "critique":
            return json.dumps({
                "fatal_flaws": [],
                "counterexamples": ["Tool metadata is unreliable."],
                "possible_reductions": ["Could be a dynamic hypergraph."],
                "tests": ["Use hidden tool arrivals with identical task budgets."],
                "verdict": "Unverified hypothesis, requires baseline comparison."
            })
        if stage == "evaluate":
            return json.dumps({
                "scores": {
                    "coherence": 3, "reconstruction": 2, "discrimination": 3,
                    "testability": 4, "parsimony": 2
                },
                "rationale": "Synthetic scores for software testing only.",
                "recommended_test": "Compare success rate on unseen tools."
            })
        raise ProviderError(f"Unknown fixture stage: {stage}")


def make_provider(name: str) -> Provider:
    providers = {"codex": CodexCLI, "claude": ClaudeCLI, "fixture": FixtureProvider}
    if name not in providers:
        raise ValueError(f"Unsupported provider: {name}")
    return providers[name]()
