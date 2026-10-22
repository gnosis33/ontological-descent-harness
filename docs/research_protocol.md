# Research protocol: Testing ontological descent

## Primary hypothesis

A structured ontology-search harness improves the frequency with which a fixed
model discovers **useful representation changes**, compared with conventional
agent prompting under comparable time, budget, and available tools.

A useful change is one that an independent evaluator can implement or reason
about, that preserves baseline requirements, and that produces a measurable
benefit or a new independently testable prediction. A novel-sounding explanation
does not qualify by itself.

## Comparison conditions

- **A: Conventional baseline.** Same model, ordinary problem-solving prompt.
- **B: Prompt-only.** Same model with an instruction to question assumptions.
- **C: Structured harness.** Ontology audit, explicit primitive operators,
  independent criticism, provisional scoring, and retained artifacts.

Pre-register problem cases and primary outcomes. Use blind evaluations whenever
possible. Match inference budgets, models, tools, and opportunity for retries.
Account separately for tokens, execution time, and financial cost.

## Evaluation targets

1. **Invariant preservation:** security, functionality, and known successful cases.
2. **Reduction quality:** whether baseline behavior is recovered under explicit
   stated assumptions, rather than hand-waved.
3. **Discrimination:** a test where competing ontologies predict or enable
   meaningfully different outcomes.
4. **Outcome advantage:** measured task success, sample efficiency, maintainability,
   expressivity, or some other task-relevant metric.
5. **Novelty and parsimony:** independent comparison against known techniques,
   including category theory, process theories, dynamic graphs, and control theory.
6. **Cost-adjusted value:** advantage after deducting ontology-search overhead.

## Failure criteria

Reject a candidate when it cannot preserve required invariants, is inconsistent,
contains no distinguishing prediction or executable test, or performs no better
than a simpler baseline after adjusting for cost.

## Critical controls

- Evaluate against strong graph/hypergraph/category-theoretic baselines.
- Include tasks for which **no ontology revision is beneficial**.
- Red-team evaluator bias toward exotic wording and excessive complexity.
- Prevent benchmark contamination and leakage of expected solutions.
- Report negative results, disagreements, and unsuccessful branches.
- Have outcome evaluators blinded to which condition produced the solution.
- Repeat with different models and domains before generalizing.

## Current limitations of v0.1

All candidate critiques and scores come from model inference. They are
hypothesis triage, not validated theorem checking, literature review, or
empirical benchmarking. The fixture provider is intentionally synthetic and
must never be counted as experimental evidence.

## Proposed next milestones

1. Build an independent evaluator with deterministic domain tests.
2. Add a benchmark set with hidden solution families and cases favoring status quo.
3. Store a persistent search DAG, including failures and provenance.
4. Add controlled recursive depth and a descent-stopping criterion.
5. Conduct blinded A/B/C experiments and publish raw results.
