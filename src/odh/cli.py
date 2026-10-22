"""Command-line entry point for bounded ontological-descent experiments."""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

from .engine import run_experiment
from .providers import ProviderError, make_provider
from .report import save_run


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="odh", description="Ontological Descent Harness research prototype"
    )
    commands = parser.add_subparsers(dest="command", required=True)
    runner = commands.add_parser("run", help="Run a bounded ontological search")
    source = runner.add_mutually_exclusive_group(required=True)
    source.add_argument("--problem", help="Text of the problem to investigate")
    source.add_argument(
        "--problem-file", type=Path, help="UTF-8 file containing the problem"
    )
    runner.add_argument(
        "--provider", choices=("codex", "claude", "fixture"), required=True
    )
    runner.add_argument("--candidates", type=int, default=3)
    runner.add_argument("--output-dir", type=Path, default=Path("runs"))
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        problem = (
            args.problem if args.problem is not None
            else args.problem_file.read_text(encoding="utf-8")
        )
        provider = make_provider(args.provider)
        result = run_experiment(problem, provider, args.candidates)
        path = save_run(result, args.output_dir)
    except (ValueError, ProviderError, OSError) as exc:
        print(f"ODH error: {exc}", file=sys.stderr)
        return 1
    print(f"Unverified research report saved to: {path}")
    for trial in result["trials"]:
        print(
            f"  {trial['index']}: {trial['candidate']['name']} "
            f"({trial['provisional_total']}/25 provisional)"
        )
    print("No empirical performance or novelty claims have been established.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
