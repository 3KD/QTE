# Assumption Ledger (per claim)
_Last updated: $(date -u +%FT%TZ)_

Track exactly what each theoretical claim assumes.

## Core primitives you already have
- Diagonal phase gadgets from series coefficients
- (I)QFT blocks; controlled-phase ladders
- Basic state-prep for low-degree analytic series
- Artifact logging (depth, twoq, p*, job_id)

## Assumptions by claim
- Hidden period / QPE: standard black-box oracle; prep of a relevant eigenstate/superposition.
- IQP sampling: anticoncentration; average-case hardness; noise within XEB tolerance.
- HHL/sparse L: block-encodings or sparse access oracles; condition number κ bounded.
- PDE evolution: generator L is local/sparse; we report few observables.
- Koopman: a compiled U for one time-step; or data-driven U with certified approximation error.
- Amplitude estimation: reflections or QSVT variants available for the prepared state.

## QRAM / data access caveat (for completeness)
Any O(log m) or “streaming” claims rely on QRAM or equivalent; mark such claims **conditional**.

