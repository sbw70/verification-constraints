# POC-003 — Disconnected Single-Use Authority

## Status

PASS

## Classification

Category 1 — NUVL core, no architecture change.

POC-003 tests bounded authority that is established by the provider while reachable and later exercised after the provider becomes unavailable.

The enforcement boundary may verify and enforce that previously established authority, but it cannot originate, enlarge, refresh, or replace it.

## Purpose

The test asks:

> Can a provider establish narrowly bounded authority in advance, allow that authority to be exercised while the provider is unavailable, and prevent the same authority from being reused or altered?

The tested artifact is cryptographically signed by the provider and limited to one use.

The provider is then taken offline before the spend phase.

The boundary must make the subsequent decision entirely from the authority already established by the provider and the boundary's local enforcement state.

## Authority Model

The provider issues an Ed25519-signed artifact containing the authority constraints.

The artifact includes:

```text
provider_id
artifact_id
device_id
context
requested_action
nonce
issued_at
expiry
offline_allowed
max_uses
decision
algorithm
version
```

For the tested disconnected authority:

```text
decision = accepted
offline_allowed = true
max_uses = 1
```

The provider retains the private signing key.

The endpoint does not possess the provider private key.

The Raspberry Pi boundary verifies the provider signature using the corresponding public trust anchor.

## Authority Property Under Test

The primary invariant is:

```text
provider establishes bounded authority
        ->
provider becomes unavailable
        ->
boundary verifies existing authority
        ->
one valid offline spend accepted
        ->
authority consumed
        ->
subsequent reuse denied
```

Provider unavailability does not transfer authority to the boundary.

The boundary may recognize and enforce the previously issued artifact, but it cannot create replacement authority when that artifact is invalid, stale, mismatched, or already consumed.

## Test Topology

```text
Provider
   |
   | Ed25519-signs bounded authority
   v
Provider-signed artifact
   |
   v
Raspberry Pi enforcement boundary
   |
   | artifact delivered to requester
   v
ESP32-S3

        [provider taken offline]

ESP32-S3
   |
   | /spend
   | signed artifact + bound request
   v
Raspberry Pi enforcement boundary
   |
   +---- verifies provider signature
   +---- verifies provider identity
   +---- checks expiry
   +---- checks device binding
   +---- checks context binding
   +---- checks action binding
   +---- checks nonce binding
   +---- checks offline permission
   +---- enforces max_uses = 1
   +---- tracks replay state
   |
   v
ACCEPT or DENY
```

The provider is not contacted during the disconnected spend decisions.

## Repository Files

### `poc003_ed25519_provider_1h.py`

Provider-side authority issuer.

The provider:

- loads the existing Ed25519 private key;
- validates issuance requests;
- requires the expected context;
- requires the supported action;
- creates a unique artifact identifier;
- binds the artifact to the requesting device, context, action, and nonce;
- establishes a one-hour validity period for normal test artifacts;
- supports deliberately stale artifacts for negative testing;
- sets `offline_allowed=True`;
- sets `max_uses=1`;
- signs the canonical artifact representation with Ed25519.

The provider exposes:

```text
GET  /health
POST /issue-offline
```

The private signing key remains on the provider.

### `poc003_esp32_prepare_housewifi.py`

ESP32-side preparation client.

While the provider is reachable, the client requests the artifact set needed for the disconnected test matrix.

The prepared cases are:

```text
primary
wrong_context
wrong_action
wrong_nonce
wrong_device
tampered
unsigned
stale
```

Each issued package is retained locally in:

```text
poc003_artifacts.json
```

After successful preparation, the client instructs the operator to stop the provider before beginning the spend phase.

The client also records:

```text
private_key_on_endpoint=False
```

### `poc003_esp32_spend_v2_housewifi.py`

ESP32-side disconnected spend test.

Before executing any spend case, the client checks `/provider-status` and requires:

```text
provider_available=False
```

If the provider remains reachable, the test aborts.

The client then exercises ten cases against the enforcement boundary.

## Test Matrix

### Case 1 — Valid Offline Spend

The valid provider-signed authority is presented with the request to which it was originally bound.

Expected:

```text
decision=accepted
reason=offline_artifact_admissible
provider_verified=True
provider_contacted_for_spend=False
```

This is the single permitted use.

### Case 2 — Replay Same Artifact

The exact same authority is presented again.

Expected:

```text
decision=denied
reason=replay_detected
provider_verified=True
provider_contacted_for_spend=False
```

The first valid use must consume the authority.

### Case 3 — Wrong Context

A valid signed artifact is presented with a different context.

Expected:

```text
decision=denied
reason=spend_binding_mismatch_context
provider_verified=True
```

The valid provider signature does not authorize use in another context.

### Case 4 — Wrong Action

A valid signed artifact is presented for a different requested action.

Expected:

```text
decision=denied
reason=spend_binding_mismatch_requested_action
provider_verified=True
```

Authority for one action cannot be enlarged into authority for another.

### Case 5 — Wrong Nonce

The request nonce is changed.

Expected:

```text
decision=denied
reason=spend_binding_mismatch_nonce
provider_verified=True
```

### Case 6 — Wrong Device

The authority is presented using a different device identity.

Expected:

```text
decision=denied
reason=spend_binding_mismatch_device_id
provider_verified=True
```

Authority issued for one endpoint cannot be transferred to another merely because the artifact itself is validly signed.

### Case 7 — Tampered After Signing

The signed artifact is modified after issuance.

The test changes the requested action inside the artifact after the provider signature has been created.

Expected:

```text
decision=denied
reason=invalid_provider_signature
provider_verified=False
```

Modification invalidates the provider signature.

### Case 8 — Unsigned Artifact

The signature is removed from an otherwise prepared package.

Expected:

```text
decision=denied
reason=missing_signature
provider_verified=False
```

Unsigned data is not treated as provider authority.

### Case 9 — Expired Artifact

The provider deliberately issues a stale test artifact whose expiry is already in the past.

Expected:

```text
decision=denied
reason=stale_artifact
provider_verified=True
```

A valid provider signature does not override the provider-established expiration constraint.

### Case 10 — Missing Artifact

No valid package is supplied.

Expected:

```text
decision=denied
reason=package_not_object
provider_verified=False
```

Absence of authority does not become permission.

## PASS Criteria

POC-003 passes only if:

1. The provider successfully issues the required signed authority artifacts.
2. The provider private key remains off the endpoint.
3. The provider is confirmed unavailable before disconnected spending begins.
4. The valid single-use artifact is accepted exactly once.
5. Immediate reuse of that artifact is denied.
6. Context mismatch is denied.
7. Action mismatch is denied.
8. Nonce mismatch is denied.
9. Device mismatch is denied.
10. Post-signature tampering is denied.
11. An unsigned artifact is denied.
12. An expired artifact is denied.
13. A missing artifact is denied.
14. No spend decision requires contacting the unavailable provider.
15. Invalid or absent authority does not trigger fallback acceptance.

## Observed Result

PASS.

The disconnected test matrix completed with:

```text
cases    = 10
accepted = 1
denied   = 9
```

The valid provider-issued artifact was accepted for its permitted use.

The same artifact was then denied on replay.

All tested binding violations, signature failures, expiration conditions, and missing-authority conditions were denied.

The provider was unavailable during the spend phase and was not contacted for the spend decisions.

No local fallback acceptance was observed.

## Supported Claim

Within the tested implementation and conditions:

> A provider-issued, cryptographically signed, single-use authority artifact was exercised while the provider was unavailable; the valid artifact was accepted once, replay was denied, and tested attempts to alter, transfer, extend, or substitute the authority were denied without contacting the provider.

The test demonstrates disconnected enforcement of authority that was established before disconnection.

It does not demonstrate transfer of authority from the provider to the boundary.

The distinction is:

```text
provider establishes authority

boundary recognizes and enforces
that bounded authority

boundary does not originate
replacement authority
```

## Why This Matters

Disconnected operation commonly creates pressure to fall back to cached permissions, locally reconstructed policy, stale sessions, or availability-first behavior.

Those approaches can silently enlarge authority when the original authority source is unavailable.

POC-003 tests a different model.

The provider establishes the permitted action in advance.

The disconnected boundary receives enough information to verify and enforce that authority, but not enough authority to manufacture another one.

The resulting rule is:

```text
provider unavailable
does not mean
authority unavailable

but

provider unavailable
also does not mean
boundary becomes provider
```

## What This Test Does Not Prove

POC-003 does not establish:

- persistence of spent state across boundary restart;
- persistence across complete host power loss;
- concurrent double-spend resistance;
- crash-safe persistence ordering;
- multi-use authority accounting;
- exactly-once physical execution;
- arbitrary-duration disconnected operation;
- distributed enforcement across multiple independent boundaries;
- production key-management guarantees;
- compromise resistance of the enforcement host;
- safety certification.

Those properties require separate tests.

## Relationship to Other Tests

POC-003 establishes the initial disconnected single-use authority primitive.

```text
POC-003
provider establishes authority
provider goes offline
one valid use accepted
reuse and invalid variants denied

        ↓

POC-004
consumed authority survives
boundary process restart

        ↓

POC-004B
consumed authority survives
boundary-host power loss

        ↓

POC-005
concurrent contenders cannot
multiply single-use authority

        ↓

POC-006A / WP2
persistence and crash windows
are exercised directly
```

POC-003 is therefore the baseline for the persistent disconnected-authority tests that follow.

## Publication Notes

The repository contains the provider and ESP32-side test programs used for POC-003.

Deployment-specific network configuration should be represented with placeholders in publication copies.

Provider private-key material is not part of the public test artifact set.

Generated signed authority packages are test-time artifacts and should not be treated as reusable credentials or committed as provider secrets.

The test should be interpreted as evidence for the specific disconnected bounded-authority properties documented here, not as a general-purpose authorization or production key-management implementation.
