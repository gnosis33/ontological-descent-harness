# Contributing

Critical, empirical feedback is welcome, including evidence that a claimed
ontology is a mere restatement of an existing formalism.

## Development

1. Use Python 3.11+.
2. Run `python -m pip install -e ".[dev]"`.
3. Run `python -m pytest -q` before proposing changes.
4. Keep fixtures independent of network access and provider accounts.
5. Include regression tests for every new stage or search operator.
6. Distinguish model judgments, proven results, and measured outcomes.
7. Do not add automatic execution of model-authored code without explicit user
   approval, sandbox isolation, and a separate security review.

## Research contributions

A useful candidate ontology identifies precise primitives, formal rules,
baseline reduction, distinguishing tests, and falsifiers. Cite established
mathematical neighbors; changing vocabulary alone does not establish novelty.

No secrets, personal data, private workspace excerpts, or provider credentials
should be committed. The project is public.
