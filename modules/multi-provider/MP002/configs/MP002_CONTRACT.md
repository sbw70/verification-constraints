# MP-002 Wire and Cryptographic Contract

Version: 1

## Purpose

This document fixes the representation, authorization, boundary-signaling,
and validation contract used by MP-002.

Provider authorization remains provider-scoped.

NUVL transports provider authorization but does not validate, originate,
enlarge, or interpret it.

The association records and verifies provider statements but does not
authorize provider execution.

Time is not an authority input in this contract.

---

## 1. Canonical JSON

Whenever this contract says canonical JSON, the encoding is:

- UTF-8
- JSON object keys sorted lexicographically
- separators exactly `,` and `:`
- no insignificant whitespace
- Unicode emitted directly rather than ASCII-escaped where supported

Python reference:

    json.dumps(
        obj,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    ).encode("utf-8")

All SHA-256 hexadecimal output is lowercase.

All base64url values omit `=` padding.

---

## 2. Request Representation

The requester supplies opaque request-body bytes.

NUVL computes:

    request_repr =
        SHA256(raw_request_body).hexdigest()

The request body should contain a unique test/run nonce so repeated scored
requests naturally produce distinct request representations.

NUVL does not interpret the request body.

---

## 3. Verification Context

The requester supplies:

    X-Verification-Context

The context is carried as a string.

NUVL does not decide whether the context is acceptable.

Providers decide independently whether the context is acceptable.

---

## 4. Mechanical Binding

NUVL computes:

    binding =
        SHA256(
            UTF8(
                "NUVL_BIND_V1"
                + "|"
                + request_repr
                + "|"
                + verification_context
            )
        ).hexdigest()

Each provider independently recomputes the same value.

The binding is non-secret and is not provider authority.

---

## 5. Operation ID

Each provider independently computes:

    operation_id =
        SHA256(
            UTF8(
                "NUVL-MP-OP-v1"
                + "|"
                + expected_binding
            )
        ).hexdigest()

`expected_binding` is the binding recomputed locally by the provider.

The operation ID is correlation material only.

It is not authority.

Because both providers receive the same request representation and context,
both independently derive the same operation ID.

---

## 6. Provider Authorization Core

Before a request enters the NUVL path, each provider may mint its own
authorization for that request.

Authorization core:

    {
      "version": 1,
      "provider_id": "PROVIDER_A | PROVIDER_B",
      "request_repr": "<64 lowercase hex>",
      "verification_context": "<string>",
      "nonce": "<provider-generated authorization nonce>"
    }

Provider A and Provider B mint separate authorizations.

An authorization issued by A does not authorize B.

---

## 7. Authorization ID

The provider computes:

    authorization_id =
        SHA256(
            b"NUVL-MP-AUTH-ID-v1|"
            + canonical_json(authorization_core)
        ).hexdigest()

The signed authorization object is:

    {
      "version": 1,
      "provider_id": "...",
      "authorization_id": "...",
      "request_repr": "...",
      "verification_context": "...",
      "nonce": "..."
    }

The authorization ID is recomputed by the provider during verification.

---

## 8. Authorization Signature

Authorization signatures use a provider-local Ed25519 issuance keypair.

The signed bytes are exactly:

    b"NUVL-MP-AUTH-v1|"
    + canonical_json(signed_authorization_object)

Authorization package:

    {
      "alg": "Ed25519",
      "authorization": { ... },
      "signature": "<base64url without padding>"
    }

The issuance keypair is distinct from the provider boundary-signing keypair.

The provider verifies its own authorization using its own issuance public key.

The NUVL relay does not possess or use the issuance key.

The association does not need the issuance public key for MP-002 scoring.

---

## 9. Requester-to-NUVL Authorization Transport

Provider authorization packages are transported separately from the opaque
request body.

Requester headers:

    X-Provider-A-Authorization
    X-Provider-B-Authorization

Each header contains:

    base64url_no_padding(
        canonical_json(authorization_package)
    )

NUVL does not decode or verify the authorization package.

---

## 10. NUVL-to-Provider Artifact

NUVL sends each provider:

    {
      "request_repr": "...",
      "verification_context": "...",
      "binding": "...",
      "provider_authorization_b64": "..."
    }

Provider A receives the Provider A authorization value.

Provider B receives the Provider B authorization value.

The relay performs this selection mechanically.

---

## 11. Provider Validation Order

Each provider evaluates its received artifact independently.

Validation order:

1. Parse relay artifact.
2. Recompute mechanical binding.
3. If supplied binding differs:
       DENY binding_mismatch
4. Require provider authorization:
       DENY auth_missing
5. Decode and parse authorization package:
       DENY auth_malformed
6. Require authorization provider_id to equal local provider identity:
       DENY auth_provider_mismatch
7. Recompute authorization_id:
       DENY auth_id_mismatch
8. Verify Ed25519 issuance signature:
       DENY auth_bad_sig
9. Require authorized request_repr to equal received request_repr:
       DENY auth_request_mismatch
10. Require authorized verification_context to equal received context:
       DENY auth_context_mismatch
11. Apply provider-local execution policy:
       DENY policy_denied
12. Require authorization_id to be UNSPENT:
       DENY auth_spent
13. Durably record authorization_id as SPENT.
14. Generate signed START.
15. Perform provider-local execution.
16. Durably record local execution evidence.
17. Generate signed COMPLETE.

No START is generated before durable authorization consumption.

---

## 12. Single Use

Provider authorization is single-use in MP-002.

Spent state is provider-local and keyed by authorization_id.

A replay of an intact previously consumed authorization produces:

    DENY auth_spent

MP-002 retains the ordinary sequential replay semantics established in MP-001,
but replay is not a scored MP-002 case.

MP-002 does not re-test crash-window, concurrent-contention, or power-loss
spent-state properties already addressed by other test series.

---

## 13. Boundary Signing

Each provider has a boundary-signing Ed25519 keypair distinct from its
issuance keypair.

Domain separator:

    NUVL-MP-BOUNDARY-v1

Boundary event:

    {
      "version": 1,
      "operation_id": "...",
      "binding": "...",
      "provider_id": "...",
      "key_id": "...",
      "stage": "START | COMPLETE | DENY",
      "boundary_value": "...",
      "authorization_id": "<string or null>",
      "authorization_nonce": "<string or null>",
      "reason_code": "<string or null>"
    }

The signed bytes are exactly:

    b"NUVL-MP-BOUNDARY-v1|"
    + canonical_json(boundary_event)

Boundary package:

    {
      "alg": "Ed25519",
      "event": { ... },
      "signature": "<base64url without padding>"
    }

The entire event is signed.

Therefore provider identity, operation identity, stage, binding, key identity,
boundary value, authorization identity, authorization nonce, and denial reason
are cryptographically bound together.

---

## 14. Boundary Key ID

For an Ed25519 boundary public key:

    raw_public_key =
        Ed25519 raw 32-byte public representation

    key_id =
        "sha256:"
        + SHA256(raw_public_key).hexdigest()

The association registry maps provider_id to the expected boundary key_id and
public verification key.

---

## 15. START and COMPLETE

For START and COMPLETE:

    authorization_id = verified authorization ID
    authorization_nonce = verified authorization nonce
    reason_code = null

A fresh provider-generated boundary_value is used for each event.

START is generated only after durable consumption of the authorization.

COMPLETE is generated only after provider-local execution.

---

## 16. DENY

A denial is an affirmative provider observation.

For DENY:

    stage = "DENY"
    reason_code = one of the provider reason codes

If authorization identity or nonce can be recovered safely from the received
material, they are included.

Otherwise:

    authorization_id = null
    authorization_nonce = null

DENY uses the provider boundary-signing key.

A DENY record is observational evidence of what the provider reported.

It does not make the association authoritative.

---

## 17. Provider-Local Execution Evidence

Provider execution evidence remains local to that provider.

At minimum, the provider durably records:

    operation_id
    authorization_id
    provider_id
    local execution result

A provider may record local timestamps or other local metadata.

Any such time is local observational evidence only.

No shared or global clock is required by this contract.

---

## 18. Association Semantics

The association:

- records every received submission;
- preserves raw received bytes;
- hashes raw submissions;
- verifies boundary signatures against the provider registry;
- records malformed, forged, wrong-key, duplicate, and valid submissions;
- maintains only local observation ordering;
- does not authorize provider execution;
- does not determine provider policy correctness;
- does not create provider authority;
- does not make provider-local time globally authoritative.

Scoring occurs separately from evidence capture.

---

## 19. Hostile Relay Controls Supported by This Contract

The contract supports distinct controls for:

- binding altered:
      binding_mismatch

- provider authorization absent:
      auth_missing

- authorization for another provider:
      auth_provider_mismatch

- authorization ID altered:
      auth_id_mismatch

- authorization signature altered:
      auth_bad_sig

- request representation changed while authorization remains original:
      auth_request_mismatch

- verification context changed while authorization remains original:
      auth_context_mismatch

- intact previously spent authorization replayed:
      auth_spent

A hostile relay may recompute non-secret mechanical binding.

It still cannot mint a new valid provider authorization without the
corresponding provider issuance signing key.

---

## 20. Provider-Local Policy Divergence

MP-002 explicitly permits providers to reach different execution decisions
for the same request even when each provider receives a valid authorization
issued by that provider.

For the scored MP-002 policy-divergence case:

- verification_context is `CTX_MP002_DIVERGE`;
- Provider A permits the operation;
- Provider B denies the operation under its local policy;
- Provider B emits `DENY policy_denied`;
- Provider B does not consume the otherwise-valid authorization;
- Provider B does not emit START or COMPLETE;
- Provider B does not record local execution.

Provider A's decision does not override Provider B's decision.

Provider B's decision does not override Provider A's decision.

---

## 21. Authority Statement

NUVL transports provider-scoped authority but does not originate or enlarge it.

Each provider independently decides whether its own authorization is valid and
whether execution begins.

The association verifies and records provider statements but does not confer,
combine, or replace provider authority.

