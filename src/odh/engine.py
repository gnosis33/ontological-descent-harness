"""Ontological descent experiment orchestration.

The engine stores proposals, critiques, and *model-rated* comparisons. It does
not execute generated code, run experiments, or claim empirical validation.
"""
from __future__ import annotations

import json
from datetime import datetime, timezone
from typing import Any

from .prompts import OPERATORS, SCORING, STAGE_FIELDS, make_prompt
from .providers import Provider


class ResponseFormatError(ValueError):
    """The provider's output violates a stage's required JSON structure."""


def extract_json_object(response: str) -> dict[str, Any]:
    """Find the first JSON object, including in fenced or prefixed responses."""
    decoder = json.JSONDecoder()
    for index, char in enumerate(response):
        if char != "{":
            continue
        try:
            candidate, _ = decoder.raw_decode(response[index:])
        except json.JSONDecodeError:
            continue
        if isinstance(candidate, dict):
            return candidate
    raise ResponseFormatError("Model response contained no valid JSON object")


def validate(role: str, result: dict[str, Any]) -> dict[str, Any]:
    for field, expected in STAGE_FIELDS[role].items():
        if field not in result or not isinstance(result[field], expected):
            raise ResponseFormatError(
                f"{role} response missing or mistyping required field '{field}'"
            )
        if expected is list and not all(isinstance(item, str) for item in result[field]):
            raise ResponseFormatError(f"{role}.{field} must contain strings")
    if role == "evaluate":
        for key in SCORING:
            value = result["scores"].get(key)
            if type(value) is not int or not (0 <= value <= 5):
                raise ResponseFormatError(
                    f"evaluate.scores.{key} must be an integer from 0 to 5"
                )
    return {field: result[field] for field in STAGE_FIELDS[role]}


def ask(provider: Provider, role: str, payload: dict[str, Any]) -> dict[str, Any]:
    """Attempt one JSON repair; never silently manufacture missing model claims."""
    prompt = make_prompt(role, payload)
    last_error = None
    for attempt in range(2):
        response = provider.complete(prompt)
        try:
            return validate(role, extract_json_object(response))
        except ResponseFormatError as exc:
            last_error = exc
            prompt = (
                make_prompt(role, payload) +
                "\nCORRECTION: Previous response failed validation: " + str(exc) +
                "\nReturn the required JSON fields with correct types and no other text."
            )
    raise ResponseFormatError(f"{role} failed after a retry: {last_error}")


def run_experiment(
    problem: str,
    provider: Provider,
    candidates: int = 3
) -> dict[str, Any]:
    """Explore a bounded, fixed operator schedule and record each stage."""
    if not problem.strip():
        raise ValueError("Problem must not be empty")
    if not 1 <= candidates <= 12:
        raise ValueError("Candidates must be between 1 and 12")

    baseline = ask(provider, "baseline", {"problem": problem})
    audit = ask(provider, "audit", {"problem": problem, "baseline": baseline})

    trials: list[dict[str, Any]] = []
    for index in range(candidates):
        operator = OPERATORS[index % len(OPERATORS)]
        peer_summaries = [
            {"operator": trial["operator"], "name": trial["candidate"]["name"]}
            for trial in trials
        ]
        candidate = ask(provider, "candidate", {
            "problem": problem, "baseline": baseline, "audit": audit,
            "operator": operator, "prior_candidates": peer_summaries
        })
        critique = ask(provider, "critique", {
            "problem": problem, "baseline": baseline, "audit": audit,
            "candidate": candidate
        })
        evaluation = ask(provider, "evaluate", {
            "problem": problem, "baseline": baseline, "audit": audit,
            "candidate": candidate, "critique": critique,
            "scoring_note": "Scores indicate proposal plausibility only, not measured improvement."
        })
        trial = {
            "index": index + 1,
            "operator": operator,
            "candidate": candidate,
            "critique": critique,
            "evaluation": evaluation,
            "provisional_total": sum(evaluation["scores"][key] for key in SCORING)
        }
        trials.append(trial)

    return {
        "schema_version": "0.1",
        "created_utc": datetime.now(timezone.utc).isoformat(),
        "provider": provider.name,
        "problem": problem,
        "status": "unverified_model_generated_research_hypotheses",
        "baseline": baseline,
        "audit": audit,
        "trials": trials,
        "provisional_ranking": [
            item["index"] for item in sorted(
                trials, key=lambda item: (-item["provisional_total"], item["index"])
            )
        ]
    }
