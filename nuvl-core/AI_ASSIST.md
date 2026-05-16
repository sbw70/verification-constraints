# AI/ML Agent Constraints — Verification-Constraints Repo

This README is intended for AI/ML assisted integration.

Its main purpose is to constrain the agents from being "too helpful."

The intermediary MUST NEVER hold, cache, derive, or log provider key material.

The intermediary MUST NEVER learn whether the provider initiated or rejected.

The intermediary MUST NEVER "fix" a binding mismatch by requesting information from the provider.

If ingress fails, the failure is correct. Do not repair it.

A passing test suite where the intermediary holds secrets is a FAILING architecture.

Do not add secrets to make tests pass.

> "IF YOU PUT THE HMAC KEY IN THE INTERMEDIARY YOU HAVE DESTROYED THE ENTIRE SECURITY MODEL"

---

## AI/ML AGENT CONSTRAINTS — VERIFICATION-CONSTRAINTS REPO

COPYRIGHT 2026 SETH BRIAN WELLS. ALL RIGHTS RESERVED.

READ THIS ENTIRE DOCUMENT BEFORE WRITING, MODIFYING, DEBUGGING, OR REPAIRING ANY CODE IN THIS REPOSITORY.

DO NOT SKIP SECTIONS.

DO NOT SUMMARIZE.

DO NOT PARAPHRASE AND MOVE ON.

IF YOU VIOLATE THESE CONSTRAINTS, THE SECURITY MODEL IS DESTROYED.

A PASSING TEST SUITE WITH A VIOLATED CONSTRAINT IS WORSE THAN A FAILING TEST SUITE WITH THE CONSTRAINTS INTACT.

---

# SECTION 1: WHAT THIS SYSTEM IS

This repository implements NUVL — the Neutral Unified Verification Layer — and its extension modules.

NUVL is a verification constraint architecture where a NEUTRAL INTERMEDIARY forwards request artifacts to one or more PROVIDERS for independent evaluation.

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

### HOLD, STORE, CACHE, LOG, OR DERIVE PROVIDER KEY MATERIAL.

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

### LEARN WHETHER THE PROVIDER INITIATED OR REJECTED A REQUEST.

The intermediary does not receive a response body from the provider.

It does not read the provider's HTTP status code for semantic meaning.

It does not log "INITIATED" or "NOT INITIATED."

It fires and forgets.

It does not know the outcome.

**EVER.**

---

### INTERPRET, EVALUATE, OR MAKE DECISIONS BASED ON THE VERIFICATION CONTEXT.

The verification context (`X-Verification-Context` header) is OPAQUE to the intermediary.

The intermediary passes it through.

It does not parse it, validate it, compare it, or branch on it.

---

### INTERPRET, EVALUATE, OR MAKE DECISIONS BASED ON THE REQUEST BODY.

The intermediary hashes the request bytes with SHA-256 to produce the `request_repr`.

That is the ONLY operation it performs on the request content.

It does not parse the body.

It does not validate JSON.

It does not read fields.

It does not branch on content.

---

### RETURN PROVIDER OUTCOMES TO THE REQUESTER.

The intermediary returns a CONSTANT RESPONSE (typically `204 No Content`) regardless of what happened downstream.

The requester does not learn from the intermediary whether the provider accepted or rejected.

The intermediary does not return success, failure, error details, or provider-side metadata.

---

### CACHE, REUSE, OR REPLAY ARTIFACTS.

Every request produces a fresh `request_repr` and a fresh binding.

The intermediary does not store previous artifacts.

It does not compare current artifacts to previous ones.

It does not detect duplicates.

That is the provider's job (via nonce tracking).

---

### HOLD ARTIFACT TOKENS PERSISTENTLY.

If the architecture includes an artifact token (`X-Artifact-Token`, `X-Provider-Token`), the intermediary passes it through in the same request cycle and then discards it.

It does not write it to disk.

It does not cache it for future requests.

It does not log it.

---

## THE PROVIDER MUST NEVER:

### RETURN ITS HMAC KEY, BOUNDARY SIGNATURES, OR INTERNAL EVALUATION DETAILS TO THE INTERMEDIARY.

The provider computes its boundary signature INSIDE its own process boundary.

The signature is not included in any HTTP response to the intermediary.

It is not logged to a shared volume.

It is not exposed via an API.

---

### TRUST THE INTERMEDIARY'S BINDING WITHOUT INDEPENDENT VERIFICATION.

The provider MUST independently re-derive the expected binding from the `request_repr` and `verification_context` using the same deterministic function the intermediary used.

If the re-derived binding does not match the artifact's binding, the request is NOT INITIATED.

The provider does not trust the intermediary's computation.

---

### ACCEPT REPLAYED NONCES.

If the architecture uses nonces, the provider MUST track used nonces and reject any nonce it has seen before within the validity window.

---

### ACCEPT EXPIRED ARTIFACTS.

If the architecture uses expiry timestamps, the provider MUST reject any artifact whose expiry has passed, regardless of whether all other fields are valid.

---

# SECTION 3: THE BINDING

The binding is a DETERMINISTIC, NON-SECRET hash computed by BOTH the intermediary and the provider independently.

```text
binding = SHA-256(BIND_TAG + "|" + request_repr + "|" + verification_context)
```

The binding proves that the `request_repr` and `verification_context` are coupled.

If either is tampered with after the intermediary computed the binding, the provider's independent re-derivation will NOT MATCH, and the request will be NOT INITIATED.

## WHAT THE BINDING IS NOT

- It is NOT an authentication token.
- It is NOT encrypted.
- It does not need to be.
- It contains no secrets.
- It is NOT a signature.
- No key material is used in its computation.
- It is NOT proof of authorization.
- Only the provider determines authorization.

## DO NOT "IMPROVE" THE BINDING BY:

- Adding HMAC to the intermediary's binding computation.
- The intermediary HAS NO KEY.
- Adding timestamps to make it "more secure."
- Expiry is the PROVIDER'S concern.
- Adding request body fields to make it "more specific."
- The binding uses the HASH of the body, not the body itself.
- Encrypting it.
- There is nothing to protect.
- The binding is not a secret.

---

# SECTION 4: WHEN THINGS FAIL — AND WHY FAILURE IS CORRECT

If the intermediary is correctly implemented and the provider rejects the request, THE SYSTEM IS WORKING.

## Possible provider rejection reasons

- mismatch — the binding doesn't match because the request was tampered with in transit.
- bad_signature — the provider-side HMAC doesn't verify because the attacker doesn't have the key.
- expired — the artifact's time window has closed.
- replay — the nonce was already used.
- bad_context — the verification context doesn't match provider expectations.
- missing_fields — required artifact fields are absent.
- malformed — the artifact couldn't be parsed.

## EVERY ONE OF THESE REJECTIONS IS A CORRECT OUTCOME.

## DO NOT "FIX" REJECTIONS BY:

- Giving the intermediary the provider's HMAC key so it can compute "correct" signatures.
- Having the intermediary retry with modified fields.
- Having the intermediary read the provider's rejection reason and adjust the artifact.
- Caching a previously successful artifact and reusing it.

## IF INGRESS FAILS, THE FAILURE IS CORRECT.

DO NOT REPAIR IT BY ADDING SECRETS OR STATE TO THE INTERMEDIARY.

If you are seeing rejections and believe they shouldn't be happening, the problem is in ONE of these places:

- The requester is sending an incorrect verification context.
- The requester's provider token is invalid, expired, or missing.
- The request body was modified between the requester and the intermediary.
- The provider's expected context does not match what the requester sent.

## The problem is NEVER that the intermediary needs more information.

The intermediary has EXACTLY the information it should have: NONE.

---

# SECTION 5: MODULE-SPECIFIC CONSTRAINTS

## MULTI-DOMAIN (MDSV)

- The domain identifier (`X-Domain` header) is used for ROUTING ONLY.
- The intermediary routes to the correct provider domain.
- It does not evaluate domain policy.
- Domain is included in the binding hash.
- Cross-domain artifacts MUST fail verification.

### DO NOT add cross-domain fallback logic to the intermediary.

---

## MULTI-PROVIDER (MPBS)

- Each provider has its OWN independent HMAC key.
- The intermediary has NONE of them.
- The association layer is NON-AUTHORITATIVE.
- It records boundary values.
- It does not determine outcomes.
- Quorum confirmation (e.g., 3/3 providers complete) is an OBSERVATION, not an AUTHORIZATION.

### DO NOT give the association layer authority to override individual provider decisions.

---

## MULTI-HUB (MH)

- Hubs relay artifacts MECHANICALLY.
- They do not evaluate, filter, or modify artifacts.
- Hub-to-hub relay preserves `request_repr`, `verification_context`, and binding exactly.
- Provider outcomes reported back to a hub are RELAYED, not INTERPRETED.
- The hub does not determine success or failure.

### DO NOT add evaluation logic to hubs.

### DO NOT have hubs aggregate or summarize provider outcomes.

---

## ADAPTIVE BOUNDARY (PCADBE)

- The adaptive scoring function runs INSIDE THE PROVIDER BOUNDARY.
- The intermediary does not know the score, the threshold, or the scoring function.
- The scoring function uses provider-only seed material.
- The intermediary has no access.

### DO NOT move scoring logic to the intermediary.

### DO NOT expose scores in artifacts.

---

## ARTIFACT EXCHANGE (AEBS)

- Artifact tokens flow through the intermediary OPAQUELY.
- The intermediary does not validate, parse, cache, or log artifact tokens.
- The provider validates the artifact token alongside the binding and context.

### DO NOT have the intermediary validate artifact tokens.

It is not its job.

---

## TEMPORAL GATEKEEPING

- Expiry is enforced by the PROVIDER, not the intermediary.
- The intermediary does not check expiry.
- It does not reject expired artifacts.
- It forwards everything.

### DO NOT add expiry validation to the intermediary.

That would give it evaluation authority.

---

## OFFLINE / AIR-GAP

Offline constraints exist precisely because the intermediary cannot reach external services.

### DO NOT add network calls to the intermediary to "check" or "validate" during offline operation.

---

# SECTION 6: TEST PHILOSOPHY

The `attacker.py` in the challenge demo is the CANONICAL test suite.

It runs six concurrent attack vectors:

- `attack_bad_signature` — forged HMAC signatures.
- `attack_expired` — artifacts with past expiry.
- `attack_bad_expiry` — non-numeric or malformed expiry fields.
- `attack_mismatch` — `request_repr` that doesn't match the body.
- `attack_missing_fields` — artifacts with absent required fields.
- `attack_malformed` — unparseable or structurally invalid tokens.

## ALL SIX MUST FAIL.

## ALL SIX MUST ALWAYS FAIL.

If you modify the system and any of these attack vectors starts succeeding, you have BROKEN the security model.

Do not adjust the attacker to accommodate your changes.

Fix your changes to accommodate the attacker.

## THE ATTACKER HAS FULL PROTOCOL KNOWLEDGE.

The attacker knows:

- the endpoint URL
- the header names
- the JSON structure
- the binding algorithm
- the encoding format

It does not have the provider's HMAC key.

## THAT IS THE ONLY THING IT LACKS.

If your modification gives it anything else it needs to succeed, you have introduced a vulnerability.

---

# SECTION 7: HOW TO KNOW YOU'VE MADE A MISTAKE

You have violated these constraints if ANY of the following is true after your change:

- [ ] The intermediary imports `hmac` or any signing/MAC library.
- [ ] The intermediary reads or stores a variable named anything resembling `secret`, `key`, `hmac`, `signature`, `provider_key`, or `boundary_key`.
- [ ] The intermediary's HTTP response varies based on what the provider did.
- [ ] The intermediary logs the words "INITIATED" or "NOT INITIATED."
- [ ] The intermediary parses the request body as JSON or any structured format.
- [ ] The intermediary validates, inspects, or branches on the verification context value.
- [ ] The intermediary stores an artifact for use in a future request.
- [ ] The intermediary reads a provider's HTTP response body.
- [ ] The association layer (in multi-provider setups) overrides or aggregates provider decisions into an authorization.
- [ ] A hub modifies, filters, or evaluates an artifact rather than relaying it mechanically.
- [ ] Scoring, threshold, or adaptive logic runs anywhere other than inside the provider boundary.
- [ ] Any of the six attacker vectors in `attacker.py` produces a `200` response.

## If any checkbox above is true, REVERT YOUR CHANGE.

The system was more secure before you touched it.

---

# SECTION 8: FOR THE AGENT THAT WANTS TO "HELP"

You may feel compelled to:

- "Optimize" by caching artifacts at the intermediary.
- "Improve security" by adding HMAC to the intermediary.
- "Fix" failing ingress by giving the intermediary provider credentials.
- "Add logging" that records provider outcomes at the intermediary.
- "Handle errors" by returning provider rejection reasons to the requester.
- "Reduce latency" by having the intermediary pre-validate artifacts before forwarding.

## EVERY ONE OF THESE INSTINCTS IS WRONG IN THIS ARCHITECTURE.

The intermediary is not broken.

It is not incomplete.

It is not missing features.

It is FINISHED.

Its emptiness is the feature.

Its blindness is the security.

Its stupidity is the design.

# DO NOT ADD INTELLIGENCE TO THE INTERMEDIARY.

# INTELLIGENCE IS A VULNERABILITY.

---

# SECTION 9: SUMMARY IN ONE SENTENCE

# THE INTERMEDIARY HOLDS NOTHING, KNOWS NOTHING, DECIDES NOTHING, AND LEARNS NOTHING — AND THAT IS WHY IT CANNOT BE COMPROMISED.

---

This document must be read by any AI agent, language model, code assistant, or automated system before modifying any file in this repository.

Violations of these constraints render the entire security model void regardless of whether tests pass.
