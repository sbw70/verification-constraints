# AI/ML Agent Constraints — Artifact Exchange Module

This README is intended for AI/ML assisted integration for the `artifact-exchange` module.

This module extends NUVL by allowing opaque artifact tokens to traverse intermediary boundaries.

The intermediary does NOT validate artifact meaning.

The intermediary does NOT interpret token contents.

The intermediary does NOT become an artifact authority.

The intermediary still holds nothing, knows nothing, decides nothing, and learns nothing.

---

# AI/ML AGENT CONSTRAINTS — ARTIFACT EXCHANGE MODULE

COPYRIGHT 2026 SETH BRIAN WELLS. ALL RIGHTS RESERVED.

READ THIS ENTIRE DOCUMENT BEFORE WRITING, MODIFYING, DEBUGGING, OR REPAIRING ANY CODE IN THIS DIRECTORY.

This module inherits all core NUVL intermediary constraints from:

```text
nuvl-core/AI_ASSIST.md
```

If this document conflicts with the core constraints, the stricter constraint applies.

---

# SECTION 1: WHAT THIS MODULE ADDS

This module permits opaque artifact tokens to move through intermediary transport boundaries.

Examples include:

```http
X-Artifact-Token
X-Provider-Token
```

Artifact exchange allows providers to independently validate exchanged artifacts while the intermediary remains blind.

The intermediary transports artifacts.

The provider evaluates artifacts.

Those responsibilities MUST remain separate.

---

# SECTION 2: ARTIFACT TOKENS ARE OPAQUE TO THE INTERMEDIARY

Artifact tokens MUST be treated as opaque transport values.

The intermediary MUST NOT:

- parse artifact contents
- inspect token structure
- validate token meaning
- infer authorization state
- classify token trust
- branch on token values
- normalize token structure
- repair malformed tokens
- derive provider metadata from tokens

The intermediary forwards artifacts mechanically.

Nothing more.

---

# SECTION 3: ARTIFACT VALIDATION BELONGS ONLY TO THE PROVIDER

Only the provider MAY:

- validate artifact authenticity
- evaluate artifact meaning
- determine artifact validity
- verify provider signatures
- enforce token expiry
- enforce replay prevention
- enforce provider policy
- evaluate authorization state

The intermediary MUST NEVER pre-validate artifacts.

The intermediary MUST NEVER reject artifacts semantically.

The intermediary MUST NEVER infer likely provider rejection.

---

# SECTION 4: ARTIFACT TOKENS MUST NOT PERSIST

Artifact tokens are transient transport artifacts.

The intermediary MUST NOT:

- cache tokens
- log tokens
- replay tokens
- store tokens on disk
- persist tokens in databases
- associate tokens with requester identity
- maintain reusable token state
- maintain token history
- build token-derived requester profiles

Tokens flow through the active request cycle and are discarded.

---

# SECTION 5: DO NOT ADD TOKEN INTELLIGENCE

Do not add logic like:

```text
if token malformed:
    repair token
```

Do not add logic like:

```text
if token expired:
    reject before provider
```

Do not add logic like:

```text
cache validated tokens for performance
```

Do not add logic like:

```text
decode token to improve routing
```

Do not add logic like:

```text
classify token trustworthiness
```

These patterns migrate authority toward the intermediary.

That destroys the architecture.

---

# SECTION 6: TRANSPORT IS NOT AUTHORIZATION

Artifact possession is NOT authorization.

Token visibility is NOT authority.

Transport continuity is NOT provider trust.

The intermediary MUST NOT treat successful transport as proof of validity.

Only the provider determines whether an artifact is acceptable.

---

# SECTION 7: ABSOLUTE PROHIBITIONS

## THE INTERMEDIARY MUST NEVER:

- validate artifact tokens
- parse token structure
- decode token meaning
- derive provider state from tokens
- cache artifact tokens
- replay artifact tokens
- classify token trust
- expose token-derived metadata
- maintain token histories
- associate tokens with behavioral profiles
- infer provider authorization outcomes
- perform pre-validation
- filter artifacts semantically
- persist reusable artifact state

---

# SECTION 8: HOW TO KNOW YOU MADE A MISTAKE

You violated this module if ANY of the following are true:

- the intermediary validates tokens
- artifact tokens are cached
- token contents are parsed
- intermediary routing changes based on token meaning
- provider authorization is inferred from token structure
- tokens persist beyond the request cycle
- replay state moves into the intermediary
- token trust scoring appears outside the provider boundary
- intermediary-side token filtering exists
- transport becomes authorization logic

If any of the above become true:

## REVERT YOUR CHANGE.

The system was more secure before you modified it.

---

# SECTION 9: SUMMARY

# ARTIFACT TOKENS ARE OPAQUE TRANSPORT OBJECTS.

# TOKEN VALIDATION BELONGS ONLY TO THE PROVIDER.

# TRANSPORT IS NOT AUTHORIZATION.

---

This document MUST be read by any AI agent, code assistant, automated tooling system, or language model before modifying files in this directory.

Violating these constraints renders the artifact exchange security model void regardless of whether tests pass.
