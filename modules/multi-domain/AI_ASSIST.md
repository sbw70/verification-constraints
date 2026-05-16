# AI/ML Agent Constraints — Multi-Domain Module

This README is intended for AI/ML assisted integration for the `multi-domain` module.

This module extends NUVL by adding domain-aware routing.

It does **not** give the intermediary domain authority.

The intermediary still holds nothing, knows nothing, decides nothing, and learns nothing.

---

# AI/ML AGENT CONSTRAINTS — MULTI-DOMAIN MODULE

COPYRIGHT 2026 SETH BRIAN WELLS. ALL RIGHTS RESERVED.

READ THIS ENTIRE DOCUMENT BEFORE WRITING, MODIFYING, DEBUGGING, OR REPAIRING ANY CODE IN THIS DIRECTORY.

This module inherits all core NUVL intermediary constraints from:

```text
nuvl-core/AI_ASSIST.md
```

If this document conflicts with the core constraints, the stricter constraint applies.

---

# SECTION 1: WHAT THIS MODULE ADDS

The multi-domain module adds mechanical domain routing.

A request may include a domain identifier, typically:

```http
X-Domain: example-domain
```

The domain identifier is used to route the artifact toward the correct provider domain.

The domain identifier is **not** authorization.

The domain identifier is **not** policy.

The domain identifier is **not** trust.

The domain identifier is **not** a provider decision.

---

# SECTION 2: DOMAIN ROUTING IS NOT DOMAIN AUTHORITY

The intermediary MAY use the domain identifier to select a configured provider route.

The intermediary MUST NOT evaluate whether the requester is allowed to use that domain.

The intermediary MUST NOT decide whether the domain is valid for the requester.

The intermediary MUST NOT infer authorization from domain presence.

The intermediary MUST NOT downgrade, upgrade, rewrite, or substitute domains.

Routing is mechanical.

Authority remains with the provider.

---

# SECTION 3: DOMAIN BINDING

The domain value participates in the artifact binding for this module.

If the domain is changed after binding, provider-side re-derivation MUST fail.

Cross-domain artifacts MUST NOT verify.

A binding created for one domain MUST NOT be accepted as valid for another domain.

The intermediary MUST NOT repair a domain mismatch.

The intermediary MUST NOT request a corrected domain from the provider.

The intermediary MUST NOT retry with a different domain.

Failure is correct.

---

# SECTION 4: ABSOLUTE PROHIBITIONS

## THE INTERMEDIARY MUST NEVER:

- evaluate domain policy
- authorize domain access
- validate domain entitlement
- inspect domain-specific requester permissions
- infer requester intent from domain value
- perform cross-domain fallback
- rewrite the `X-Domain` value
- substitute a default domain after failure
- retry a failed artifact against another domain
- ask the provider which domain should be used
- learn whether a domain-specific request was initiated or rejected
- cache domain-specific artifacts
- maintain domain-specific requester state
- merge domain behavior across providers

---

# SECTION 5: DO NOT ADD CROSS-DOMAIN FALLBACK

Cross-domain fallback destroys the model.

Do not add logic like:

```text
if provider_A rejects:
    try provider_B
```

Do not add logic like:

```text
if domain missing:
    infer best domain
```

Do not add logic like:

```text
if domain mismatch:
    ask provider for corrected domain
```

Do not add logic like:

```text
if domain unavailable:
    route to default domain
```

A failed domain route is not something to repair.

It is a boundary condition.

---

# SECTION 6: PROVIDER RESPONSIBILITY

The provider is responsible for independently verifying:

- the request representation
- the verification context
- the domain value
- the binding
- any provider-side policy
- any domain-specific entitlement
- any replay or expiry constraints

The intermediary does not help.

The intermediary does not pre-check.

The intermediary does not interpret rejection.

The intermediary forwards and exits.

---

# SECTION 7: HOW TO KNOW YOU MADE A MISTAKE

You violated this module if ANY of the following are true:

- the intermediary treats `X-Domain` as authorization
- the intermediary validates requester permission for a domain
- the intermediary rewrites the domain value
- the intermediary retries against another domain
- the intermediary adds default-domain fallback
- the intermediary asks a provider which domain should be used
- the intermediary learns whether a domain route was accepted or rejected
- the intermediary caches domain routing decisions per requester
- the intermediary stores domain-specific artifacts for reuse
- cross-domain artifacts succeed verification

If any of the above become true:

## REVERT YOUR CHANGE.

The system was more secure before you modified it.

---

# SECTION 8: SUMMARY

# DOMAIN AWARENESS IS ROUTING ONLY.

# ROUTING IS NOT AUTHORITY.

# CROSS-DOMAIN FALLBACK IS A SECURITY FAILURE.

---

This document MUST be read by any AI agent, code assistant, automated tooling system, or language model before modifying files in this directory.

Violating these constraints renders the multi-domain security model void regardless of whether tests pass.
