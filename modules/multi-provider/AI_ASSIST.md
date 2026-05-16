
# AI/ML Agent Constraints — Multi-Provider Module

This README is intended for AI/ML assisted integration for the `multi-provider` module.

This module extends NUVL by allowing independent provider-bound verification across multiple providers.

It does NOT centralize authority.

It does NOT create shared provider trust.

It does NOT permit intermediary-side authorization aggregation.

The intermediary still holds nothing, knows nothing, decides nothing, and learns nothing.

---

# AI/ML AGENT CONSTRAINTS — MULTI-PROVIDER MODULE

COPYRIGHT 2026 SETH BRIAN WELLS. ALL RIGHTS RESERVED.

READ THIS ENTIRE DOCUMENT BEFORE WRITING, MODIFYING, DEBUGGING, OR REPAIRING ANY CODE IN THIS DIRECTORY.

This module inherits all core NUVL intermediary constraints from:

```text
nuvl-core/AI_ASSIST.md
```

If this document conflicts with the core constraints, the stricter constraint applies.

---

# SECTION 1: WHAT THIS MODULE ADDS

The multi-provider module allows request artifacts to be independently evaluated by multiple providers.

Each provider operates as an independent authority boundary.

Providers do not share authority.

Providers do not share secrets.

Providers do not inherit trust from each other.

The intermediary coordinates routing only.

The intermediary is NOT an authority broker.

---

# SECTION 2: PROVIDERS REMAIN INDEPENDENT

Each provider has its OWN:

- HMAC key material
- verification state
- replay protection
- policy evaluation
- authorization logic
- scoring logic
- expiry enforcement
- decision authority

No provider trusts another provider's verification result automatically.

No provider inherits authorization from another provider.

A valid result from Provider A does NOT imply validity for Provider B.

---

# SECTION 3: THE INTERMEDIARY MUST NEVER BECOME AN AUTHORITY LAYER

The intermediary MAY relay artifacts to multiple providers.

The intermediary MAY observe transport completion.

The intermediary MUST NOT:

- aggregate authorization
- merge provider decisions
- override provider rejection
- infer consensus authorization
- create provider trust hierarchies
- rank providers by trust
- determine quorum authorization
- substitute provider approval
- synthesize a final authorization result

The intermediary routes.

The providers decide.

---

# SECTION 4: QUORUM IS OBSERVATION, NOT AUTHORIZATION

If the architecture tracks provider completion counts such as:

```text
2/2 completed
3/3 completed
```

that information is OBSERVATIONAL ONLY.

Completion count is NOT authorization.

Consensus count is NOT authority.

Transport completion is NOT provider trust.

The association layer MUST remain NON-AUTHORITATIVE.

---

# SECTION 5: ABSOLUTE PROHIBITIONS

## THE INTERMEDIARY MUST NEVER:

- hold provider HMAC keys
- centralize provider secrets
- cache provider authorization results
- combine provider decisions into authorization
- retry artifacts against alternate providers automatically
- substitute one provider's decision for another
- infer provider trust relationships
- rank providers by reliability or trustworthiness
- expose provider-specific rejection reasons
- create a global authorization state
- maintain provider consensus state as authority
- override provider rejection based on quorum logic
- decide that "enough providers approved"
- learn whether a specific provider initiated or rejected

---

# SECTION 6: PROVIDER ISOLATION IS THE SECURITY MODEL

Each provider boundary must remain cryptographically and operationally independent.

Compromise of one provider MUST NOT grant authority over another provider.

The intermediary MUST NOT become a shared trust anchor.

The association layer MUST NOT become centralized authorization infrastructure.

The architecture depends on distributed authority confinement.

Not distributed authority accumulation.

---

# SECTION 7: DO NOT BUILD A CENTRAL AUTHORITY SYSTEM

Do not add logic like:

```text
if 2 of 3 providers approve:
    authorize request
```

Do not add logic like:

```text
provider_A trusted provider_B
```

Do not add logic like:

```text
if primary provider fails:
    inherit authorization from backup provider
```

Do not add logic like:

```text
combine provider outcomes into final trust score
```

These patterns collapse provider-bound authority into intermediary-side authority accumulation.

That destroys the architecture.

---

# SECTION 8: HOW TO KNOW YOU MADE A MISTAKE

You violated this module if ANY of the following are true:

- providers share HMAC material
- the intermediary stores provider secrets
- provider outcomes are merged into centralized authorization
- quorum becomes authorization
- provider trust becomes transitive
- the association layer overrides provider decisions
- provider scoring becomes centralized
- the intermediary determines whether enough providers approved
- provider rejection is hidden by fallback authorization
- one provider's authorization automatically grants another provider's authorization
- the intermediary learns provider-side authorization outcomes

If any of the above become true:

## REVERT YOUR CHANGE.

The system was more secure before you modified it.

---

# SECTION 9: SUMMARY

# MULTIPLE PROVIDERS DO NOT CREATE SHARED AUTHORITY.

# QUORUM IS OBSERVATION, NOT AUTHORIZATION.

# THE ASSOCIATION LAYER IS NOT A TRUST ANCHOR.

---

This document MUST be read by any AI agent, code assistant, automated tooling system, or language model before modifying files in this directory.

Violating these constraints renders the multi-provider security model void regardless of whether tests pass.
