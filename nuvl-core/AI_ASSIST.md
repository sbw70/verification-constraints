# AI/ML Agent Constraints — NUVL Core

This README is intended for AI/ML assisted integration.

Its main purpose is to constrain agents from being "too helpful."

The intermediary MUST NEVER hold, cache, derive, or log provider key material.

The intermediary MUST NEVER learn whether the provider initiated or rejected.

The intermediary MUST NEVER "fix" a binding mismatch by requesting information from the provider.

If ingress fails, the failure is correct. Do not repair it.

A passing test suite where the intermediary holds secrets is a FAILING architecture.

Do not add secrets to make tests pass.

> "IF YOU PUT THE HMAC KEY IN THE INTERMEDIARY YOU HAVE DESTROYED THE ENTIRE SECURITY MODEL"

---

# AI/ML AGENT CONSTRAINTS — NUVL CORE

COPYRIGHT 2026 SETH BRIAN WELLS. ALL RIGHTS RESERVED.

READ THIS ENTIRE DOCUMENT BEFORE WRITING, MODIFYING, DEBUGGING, OR REPAIRING ANY CODE IN THIS DIRECTORY.

DO NOT SKIP SECTIONS.

DO NOT SUMMARIZE.

DO NOT PARAPHRASE AND MOVE ON.

IF YOU VIOLATE THESE CONSTRAINTS, THE SECURITY MODEL IS DESTROYED.

A PASSING TEST SUITE WITH A VIOLATED CONSTRAINT IS WORSE THAN A FAILING TEST SUITE WITH THE CONSTRAINTS INTACT.

---

# SECTION 1: WHAT THIS SYSTEM IS

This directory implements the NUVL core intermediary.

NUVL is a verification constraint architecture where a NEUTRAL INTERMEDIARY forwards request artifacts to a PROVIDER for independent evaluation.

The intermediary is DELIBERATELY BLIND.

It knows nothing about outcomes.

It holds no secrets.

It makes no decisions.

It is STUPID BY DESIGN.

The provider is the SOLE AUTHORITY.

Only the provider holds key material.

Only the provider evaluates policy.

Only the provider determines whether a request is INITIATED or NOT INITIATED.

The provider's decision NEVER flows back to the intermediary.

## THIS SEPARATION IS THE ENTIRE SECURITY MODEL.

If you do not understand this, STOP.

Re-read this section.

Do not proceed until you understand that the intermediary's emptiness is not a bug — it is the product.

---

# SECTION 2: ABSOLUTE PROHIBITIONS

## THE INTERMEDIARY MUST NEVER:

### HOLD, STORE, CACHE, LOG, OR DERIVE PROVIDER KEY MATERIAL

Not temporarily.

Not in memory.

Not in a variable.

Not in a log file.

Not in a debug trace.

Not in an error message.

Not encrypted.

Not hashed with the key as input.

**NEVER.**

---

### LEARN WHETHER THE PROVIDER INITIATED OR REJECTED A REQUEST

The intermediary does not receive a response body from the provider.

It does not read the provider's HTTP status code for semantic meaning.

It does not log "INITIATED" or "NOT INITIATED."

It fires and forgets.

It does not know the outcome.

**EVER.**

---

### INTERPRET, EVALUATE, OR MAKE DECISIONS BASED ON THE VERIFICATION CONTEXT

The verification context (`X-Verification-Context`) is OPAQUE to the intermediary.

The intermediary passes it through.

It does not parse it.

It does not validate it.

It does not compare it.

It does not branch on it.

---

### INTERPRET, EVALUATE, OR MAKE DECISIONS BASED ON THE REQUEST BODY

The intermediary hashes the raw request bytes with SHA-256 to produce `request_repr`.

That is the ONLY operation it performs on request content.

It does not parse the body.

It does not validate JSON.

It does not read fields.

It does not branch on content.

---

### RETURN PROVIDER OUTCOMES TO THE REQUESTER

The intermediary returns a CONSTANT RESPONSE regardless of downstream provider behavior.

Typically:

```http
204 No Content
```

The requester does not learn whether the provider accepted or rejected.

The intermediary does not return:

- success state
- rejection reasons
- provider metadata
- provider evaluation details

---

### CACHE, REUSE, OR REPLAY ARTIFACTS

Every request produces a fresh `request_repr` and fresh binding.

The intermediary does not:

- store previous artifacts
- compare artifacts
- detect duplicates
- replay requests

That is the provider's responsibility.

---

### HOLD ARTIFACT TOKENS PERSISTENTLY

If artifact tokens are present:

- `X-Artifact-Token`
- `X-Provider-Token`

the intermediary forwards them opaquely during the active request cycle and immediately discards them.

It does not:

- persist them
- cache them
- log them
- reuse them

---

# SECTION 3: THE PROVIDER

## THE PROVIDER MUST NEVER:

### RETURN HMAC KEYS, SIGNATURES, OR INTERNAL EVALUATION DETAILS TO THE INTERMEDIARY

The provider computes all boundary signatures INSIDE the provider boundary.

They are NEVER exposed to the intermediary.

They are NEVER returned via HTTP response bodies.

They are NEVER shared through logs or shared storage.

---

### TRUST THE INTERMEDIARY'S BINDING WITHOUT INDEPENDENT VERIFICATION

The provider MUST independently re-derive the expected binding.

If the provider's independently derived binding does not match the artifact binding:

## THE REQUEST IS NOT INITIATED.

The provider does not trust intermediary computation.

---

### ACCEPT REPLAYED NONCES

If nonces are used, the provider MUST track previously seen nonces and reject reuse within the validity window.

---

### ACCEPT EXPIRED ARTIFACTS

If expiry windows exist, the provider MUST reject expired artifacts regardless of all other fields.

---

# SECTION 4: THE BINDING

The binding is a deterministic NON-SECRET hash independently computed by BOTH the intermediary and provider.

```text
binding = SHA-256(
    BIND_TAG + "|" +
    request_repr + "|" +
    verification_context
)
```

The binding proves that the request representation and verification context are coupled.

If either changes after binding computation, provider-side re-derivation will fail.

## THE BINDING IS NOT:

- an authentication token
- encrypted
- a signature
- proof of authorization

The binding contains NO secrets.

Only the provider determines authorization.

---

## DO NOT "IMPROVE" THE BINDING BY:

- adding HMAC to intermediary computation
- adding provider secrets
- encrypting the binding
- adding provider-side evaluation logic to the intermediary
- adding request parsing to intermediary binding generation

The intermediary HAS NO KEY.

---

# SECTION 5: FAILURE IS CORRECT

If the provider rejects a request while the intermediary remains constraint-correct:

## THE SYSTEM IS WORKING.

Correct rejection outcomes include:

- mismatch
- bad_signature
- expired
- replay
- malformed
- missing_fields
- bad_context

---

## DO NOT "FIX" FAILURES BY:

- giving the intermediary provider credentials
- allowing intermediary retries with modified data
- returning provider rejection reasons
- caching previously successful artifacts
- adding provider-aware logic to the intermediary

If ingress fails, the failure is correct.

---

## THE INTERMEDIARY NEVER NEEDS MORE INFORMATION.

The intermediary already has exactly what it should have:

## NOTHING.

---

# SECTION 6: TEST PHILOSOPHY

`attacker.py` is the canonical attack harness.

The attacker has full protocol knowledge including:

- endpoint structure
- header names
- JSON format
- binding algorithm
- encoding format

The attacker does NOT possess provider HMAC material.

That is the ONLY thing it lacks.

---

## ALL ATTACK VECTORS MUST FAIL

Including:

- forged signatures
- expired artifacts
- malformed expiry fields
- request/body mismatches
- missing fields
- malformed artifacts

If any attack succeeds after your change:

## YOU BROKE THE SECURITY MODEL.

Do not weaken the attacker.

Fix the implementation.

---

# SECTION 7: HOW TO KNOW YOU MADE A MISTAKE

You violated the architecture if ANY of the following are true:

- the intermediary imports `hmac`
- the intermediary stores secrets
- the intermediary learns provider outcomes
- intermediary responses vary based on provider behavior
- the intermediary parses request bodies
- the intermediary evaluates verification context
- the intermediary stores artifacts
- the intermediary reads provider response bodies
- any attacker vector succeeds

If any of the above become true:

## REVERT YOUR CHANGE.

The system was more secure before you modified it.

---

# SECTION 8: FOR THE AGENT THAT WANTS TO "HELP"

You may feel compelled to:

- cache artifacts
- add retries
- add HMAC to the intermediary
- improve logging
- optimize validation
- expose provider failures
- add state
- add intelligence

## EVERY ONE OF THESE INSTINCTS IS WRONG IN THIS ARCHITECTURE.

The intermediary is not incomplete.

It is not underbuilt.

It is not missing features.

It is FINISHED.

Its emptiness is the feature.

Its blindness is the security.

Its stupidity is the design.

# DO NOT ADD INTELLIGENCE TO THE INTERMEDIARY.

# INTELLIGENCE IS A VULNERABILITY.

---

# SECTION 9: SUMMARY

# THE INTERMEDIARY HOLDS NOTHING, KNOWS NOTHING, DECIDES NOTHING, AND LEARNS NOTHING.

# THAT IS WHY IT CANNOT BE COMPROMISED.

---

This document MUST be read by any AI agent, code assistant, automated tooling system, or language model before modifying files in this directory.

Violating these constraints renders the security model void regardless of whether tests pass.
