# AI/ML Agent Constraints — Multi-Hub Module

This README is intended for AI/ML assisted integration for the `multi-hub` module.

This module extends NUVL by allowing artifacts to relay across multiple hubs before reaching a provider boundary.

Hubs are transport relays.

Hubs are NOT authorities.

Hubs do NOT evaluate artifacts.

Hubs do NOT interpret outcomes.

The intermediary still holds nothing, knows nothing, decides nothing, and learns nothing.

---

# AI/ML AGENT CONSTRAINTS — MULTI-HUB MODULE

COPYRIGHT 2026 SETH BRIAN WELLS. ALL RIGHTS RESERVED.

READ THIS ENTIRE DOCUMENT BEFORE WRITING, MODIFYING, DEBUGGING, OR REPAIRING ANY CODE IN THIS DIRECTORY.

This module inherits all core NUVL intermediary constraints from:

```text
nuvl-core/AI_ASSIST.md
```

If this document conflicts with the core constraints, the stricter constraint applies.

---

# SECTION 1: WHAT THIS MODULE ADDS

The multi-hub module permits mechanical relay of artifacts across multiple intermediary hubs.

Artifacts may traverse:

```text
Requester
    ↓
Hub A
    ↓
Hub B
    ↓
Hub C
    ↓
Provider
```

Each hub acts as a transport boundary only.

No hub becomes an authorization boundary.

No hub becomes an interpretation layer.

No hub gains provider authority.

---

# SECTION 2: HUBS ARE MECHANICAL RELAYS

A hub MAY:

- receive artifacts
- forward artifacts
- preserve transport continuity
- relay opaque metadata
- maintain transport connectivity

A hub MUST NOT:

- evaluate artifacts
- inspect policy meaning
- authorize requests
- interpret verification context
- infer requester intent
- summarize provider outcomes
- modify artifact structure
- rewrite bindings
- repair malformed artifacts

The hub relays mechanically.

Nothing more.

---

# SECTION 3: ARTIFACT INTEGRITY MUST BE PRESERVED

Hub-to-hub relay MUST preserve:

- `request_repr`
- verification context
- binding values
- artifact tokens
- opaque metadata

exactly as received.

The hub MUST NOT:

- recompute bindings
- normalize payloads
- transform request content
- modify encoding structure
- optimize artifact representation
- repair malformed data
- remove fields
- inject fields

Artifacts must arrive at the provider boundary exactly as transmitted.

---

# SECTION 4: HUBS MUST NOT BECOME EVALUATION LAYERS

The hub MUST NOT:

- infer whether a request will succeed
- rank requests by validity
- score requests
- filter requests by policy
- reject based on semantic interpretation
- classify artifacts by trust level
- aggregate provider outcomes
- infer authorization state
- learn provider decisions

Transport visibility is NOT authority.

Relay visibility is NOT authorization.

---

# SECTION 5: PROVIDER OUTCOMES

If provider responses traverse hubs:

the hubs relay them mechanically.

The hubs do NOT:

- interpret outcomes
- summarize outcomes
- aggregate outcomes
- classify outcomes
- infer success/failure meaning
- expose provider internals
- create transport-side trust decisions

The hub is NOT a decision layer.

---

# SECTION 6: DO NOT ADD SMART RELAY LOGIC

Do not add logic like:

```text
if artifact looks malformed:
    repair it
```

Do not add logic like:

```text
if provider likely rejects:
    stop forwarding
```

Do not add logic like:

```text
if Hub B unavailable:
    rewrite artifact for Hub C
```

Do not add logic like:

```text
if artifact invalid:
    auto-correct fields
```

Do not add logic like:

```text
optimize artifact before forwarding
```

These behaviors turn hubs into execution participants.

Execution participation creates authority accumulation.

Authority accumulation destroys the architecture.

---

# SECTION 7: ABSOLUTE PROHIBITIONS

## HUBS MUST NEVER:

- hold provider secrets
- derive provider signatures
- recompute bindings
- cache artifacts for reuse
- evaluate verification context
- parse request semantics
- modify artifacts
- normalize transport structure
- summarize provider outcomes
- aggregate provider decisions
- infer authorization state
- become fallback authorization layers
- perform semantic filtering
- perform trust scoring
- retry modified artifacts
- create execution-side policy behavior

---

# SECTION 8: HOW TO KNOW YOU MADE A MISTAKE

You violated this module if ANY of the following are true:

- hubs modify artifacts during relay
- hubs recompute bindings
- hubs classify requests by validity
- hubs reject requests semantically
- hubs summarize provider outcomes
- hubs infer authorization state
- hubs cache reusable artifact state
- hubs perform transport-side trust evaluation
- hubs optimize artifacts before forwarding
- hubs perform policy-aware routing
- hubs aggregate provider decisions
- hubs become fallback authorization layers

If any of the above become true:

## REVERT YOUR CHANGE.

The system was more secure before you modified it.

---

# SECTION 9: SUMMARY

# HUBS RELAY.

# HUBS DO NOT DECIDE.

# RELAY VISIBILITY IS NOT AUTHORITY.

# MECHANICAL FORWARDING IS THE SECURITY MODEL.

---

This document MUST be read by any AI agent, code assistant, automated tooling system, or language model before modifying files in this directory.

Violating these constraints renders the multi-hub security model void regardless of whether tests pass.
