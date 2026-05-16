# AI/ML Agent Constraints — Adaptive Boundary Constraints Module

This README is intended for AI/ML assisted integration for the `adaptive-boundary-constraints` module.

This module extends NUVL by allowing adaptive scoring and boundary evaluation INSIDE the provider boundary.

The intermediary does NOT gain adaptive authority.

The intermediary does NOT learn scores.

The intermediary does NOT evaluate thresholds.

The intermediary still holds nothing, knows nothing, decides nothing, and learns nothing.

---

# AI/ML AGENT CONSTRAINTS — ADAPTIVE BOUNDARY CONSTRAINTS MODULE

COPYRIGHT 2026 SETH BRIAN WELLS. ALL RIGHTS RESERVED.

READ THIS ENTIRE DOCUMENT BEFORE WRITING, MODIFYING, DEBUGGING, OR REPAIRING ANY CODE IN THIS DIRECTORY.

This module inherits all core NUVL intermediary constraints from:

```text
nuvl-core/AI_ASSIST.md
```

If this document conflicts with the core constraints, the stricter constraint applies.

---

# SECTION 1: WHAT THIS MODULE ADDS

This module permits adaptive boundary evaluation INSIDE the provider boundary.

Provider-side systems MAY evaluate:

- risk scoring
- behavioral scoring
- adaptive thresholds
- anomaly weighting
- contextual evaluation
- provider-specific heuristics
- seed-derived scoring functions

The intermediary does NOT participate in those decisions.

The intermediary does NOT know the scoring logic.

The intermediary does NOT know the thresholds.

The intermediary does NOT know the evaluation outcome.

Adaptive behavior remains provider-confined.

---

# SECTION 2: ADAPTIVE AUTHORITY MUST REMAIN INSIDE THE PROVIDER BOUNDARY

All adaptive evaluation logic MUST execute INSIDE the provider boundary.

Including:

- threshold evaluation
- score computation
- seed material usage
- behavioral modeling
- contextual weighting
- adaptive authorization decisions

The intermediary MUST NEVER:

- compute scores
- infer scores
- estimate thresholds
- classify risk
- branch on adaptive outcomes
- cache adaptive state
- interpret provider scoring behavior

Adaptive intelligence belongs ONLY to the provider.

---

# SECTION 3: PROVIDER-ONLY SEED MATERIAL

Adaptive scoring MAY use provider-only seed material.

That material MUST NEVER:

- leave the provider boundary
- reach the intermediary
- appear in artifacts
- appear in logs
- appear in transport metadata
- appear in error responses
- appear in debug traces

The intermediary MUST NEVER derive provider-side adaptive logic from observed traffic.

---

# SECTION 4: THE INTERMEDIARY MUST NEVER BECOME A SCORING ENGINE

The intermediary MUST NOT:

- score requests
- classify trust
- rank request validity
- assign confidence values
- estimate behavioral risk
- calculate anomaly scores
- maintain requester behavior history
- perform adaptive filtering
- learn provider thresholds
- infer provider evaluation models
- predict provider outcomes

Transport awareness is NOT scoring authority.

Observation is NOT evaluation authority.

---

# SECTION 5: DO NOT EXPOSE ADAPTIVE STATE

Do not expose:

- provider scores
- threshold values
- behavioral classifications
- evaluation confidence
- seed-derived metadata
- anomaly classifications
- adaptive weighting logic

through:

- artifacts
- intermediary logs
- response headers
- transport metadata
- hub relays
- association layers

Adaptive logic remains provider-confined.

---

# SECTION 6: DO NOT MOVE ADAPTIVE LOGIC CLOSER TO THE INTERMEDIARY

Do not add logic like:

```text
pre-score requests before provider evaluation
```

Do not add logic like:

```text
estimate likely provider rejection
```

Do not add logic like:

```text
cache requester risk history at intermediary
```

Do not add logic like:

```text
optimize routing based on behavioral scoring
```

Do not add logic like:

```text
drop low-score requests before forwarding
```

These patterns migrate evaluation authority toward the intermediary.

That destroys the architecture.

---

# SECTION 7: ABSOLUTE PROHIBITIONS

## THE INTERMEDIARY MUST NEVER:

- compute adaptive scores
- infer provider thresholds
- perform risk classification
- maintain behavioral profiles
- cache adaptive evaluation state
- expose provider-side scoring logic
- branch on adaptive outcomes
- predict provider authorization
- learn provider seed material
- summarize adaptive evaluation
- optimize transport using provider scoring
- filter requests by behavioral confidence
- perform trust estimation

---

# SECTION 8: HOW TO KNOW YOU MADE A MISTAKE

You violated this module if ANY of the following are true:

- the intermediary computes risk scores
- the intermediary maintains requester behavior history
- provider thresholds become visible outside the provider boundary
- adaptive state is cached outside the provider boundary
- the intermediary predicts provider outcomes
- transport behavior changes based on adaptive evaluation
- provider seed material becomes observable
- hubs or association layers gain adaptive logic
- provider-side scoring leaks into artifacts or metadata
- intermediary-side filtering uses adaptive evaluation

If any of the above become true:

## REVERT YOUR CHANGE.

The system was more secure before you modified it.

---

# SECTION 9: SUMMARY

# ADAPTIVE INTELLIGENCE BELONGS INSIDE THE PROVIDER BOUNDARY.

# SCORING IS AUTHORITY.

# AUTHORITY MUST NOT MIGRATE TO THE INTERMEDIARY.

---

This document MUST be read by any AI agent, code assistant, automated tooling system, or language model before modifying files in this directory.

Violating these constraints renders the adaptive boundary security model void regardless of whether tests pass.
