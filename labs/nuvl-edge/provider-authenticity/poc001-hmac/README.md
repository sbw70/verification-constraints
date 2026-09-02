# POC-001 — HMAC Bounded Disconnected Authority

## Overview

POC-001 tested a bounded provider-unavailable authorization path for NUVL.

The proof established a provider-first validation model in which normal requests were evaluated by the provider while it remained reachable. Before provider loss, the provider could issue a time-limited, request-bound, single-use artifact for use during a bounded disconnected window.

When the provider became unavailable, the Raspberry Pi NUVL boundary could validate that previously issued artifact and admit the corresponding request once.

The experiment tested whether provider loss could be handled without introducing unrestricted local fallback authority.

POC-001 used HMAC-SHA256 authentication and therefore intentionally preceded the asymmetric provider-authenticity model introduced in POC-002.

## Test Classification

**Category:** NUVL core — no architecture change.

**Capability:** Bounded disconnected authority.

**Use case:** A constrained endpoint requires a narrowly scoped action during temporary provider unavailability without receiving unrestricted local authorization capability.

## Tested Architecture

The tested path was:

```text
ESP32-S3
    |
    | Wi-Fi
    v
GL.iNet Mango GL-MT300N-V2
    |
    v
Raspberry Pi 5
NUVL boundary
    |
    v
Windows provider
```

Normal operation used a provider-first path:

```text
endpoint request
      |
      v
NUVL boundary
      |
      v
provider reachable
      |
      v
provider validates request
      |
      v
ACCEPT or DENY
```

The disconnected path was:

```text
provider unavailable
      |
      v
NUVL boundary
      |
      v
validate previously issued
bounded artifact
      |
      +---- invalid ----> DENY
      |
      +---- valid ------> ACCEPT ONCE
```

The disconnected artifact did not create a general local allow mode.

## Bounded Artifact

The provider implementation issued an HMAC-SHA256 authenticated artifact containing:

- action;
- context;
- unique nonce;
- issuance time;
- expiration time;
- maximum-use count;
- request representation.

The artifact was bound to the requested action and context.

The tested artifact specified:

```text
max_uses=1
```

The request representation was derived from the action and context and included in the authenticated artifact.

## Provider-First Operation

While the provider was reachable, the boundary attempted normal provider validation.

The provider returned acceptance only for the configured action and context.

Requests outside that configured scope were denied by the provider.

The bounded disconnected path was entered only after the normal provider request failed because the provider was unavailable.

## Provider-Unavailable Validation

During provider unavailability, the boundary evaluated the supplied artifact before admitting the request.

Validation included:

1. artifact presence;
2. artifact decoding;
3. HMAC authentication;
4. action binding;
5. context binding;
6. request-representation binding;
7. expiration;
8. single-use constraint;
9. nonce presence;
10. replay state.

A request was accepted through the disconnected path only after all checks succeeded.

The accepted disconnected result was identified by:

```text
decision=accepted
reason=bounded_artifact_valid_once
path=provider_unavailable_bounded_window
```

Failure of artifact validation produced a denied result through:

```text
path=provider_unavailable_fail_closed
```

## Tested Conditions

The POC-001 laboratory sequence exercised the following conditions:

| Condition | Expected behavior |
|---|---|
| Provider reachable with admissible request | ACCEPT |
| Provider unavailable with valid unexpired artifact | ACCEPT once |
| Replay of consumed artifact | DENY |
| Missing artifact | DENY |
| Artifact for wrong context | DENY |
| Artifact for wrong action | DENY |
| Expired artifact | DENY |
| Provider restored | Provider-backed ACCEPT restored |

The valid disconnected artifact was accepted once.

Subsequent use of the same artifact was denied as replay.

## Single-Use Enforcement

Single-use state was maintained by the Raspberry Pi boundary.

After successful disconnected validation, the artifact nonce was entered into the boundary's used-nonce state.

A subsequent request containing the same artifact was rejected as:

```text
artifact_replay
```

Expired nonce entries could later be removed from the in-memory used-nonce set.

POC-001 therefore demonstrated single-use behavior during the running boundary process.

It did not demonstrate durable spent-state persistence across boundary restart or power loss.

Persistent replay protection was addressed by later NUVL experiments.

## Fail-Closed Behavior

Provider unavailability did not independently authorize an action.

If the provider was unavailable and the supplied bounded artifact failed validation, the boundary returned a denied result.

Relevant denial conditions included:

```text
missing_artifact
artifact_decode_failed
artifact_signature_invalid
artifact_wrong_action
artifact_wrong_context
artifact_request_binding_invalid
artifact_expired
artifact_not_single_use
artifact_missing_nonce
artifact_replay
```

The tested disconnected path therefore required affirmative validation of previously issued bounded authority.

## HMAC Trust Placement

POC-001 used a shared HMAC secret.

The provider required the secret to authenticate artifacts:

```text
provider
    |
    | shared HMAC secret
    |
    v
signed bounded artifact
```

The Raspberry Pi boundary required the same secret to verify those artifacts:

```text
provider                  Raspberry Pi boundary
   |                               |
   |                               |
   +------ shared HMAC secret -----+
```

This arrangement supported the behavioral objective of the initial bounded-disconnected-authority proof, but it did not preserve exclusive provider signing authority.

Possession of the HMAC secret gives the boundary the cryptographic material required both to verify and to generate valid HMAC authentication values.

Accordingly, POC-001 did **not** establish that the provider alone could originate cryptographically valid bounded artifacts.

That limitation directly motivated POC-002.

## Relationship to POC-002

POC-002 replaced the shared HMAC trust relationship with Ed25519 asymmetric signatures.

The transition was:

```text
POC-001

provider:
    shared HMAC secret

boundary:
    same shared HMAC secret

property:
    boundary can verify
    boundary also possesses material capable of minting


            ↓


POC-002

provider:
    Ed25519 private signing key

boundary:
    provider public verification key only

property:
    boundary can verify provider signatures
    boundary does not possess provider private signing key
```

POC-002 therefore addressed the principal trust-placement limitation identified by POC-001.

POC-003 subsequently combined asymmetric provider authority with bounded disconnected single-use behavior.

## Public Files

### `ddil_provider.py`

Original provider implementation retained from the July 11, 2026 test.

The retained publication copy is byte-identical to the original Windows test-host source identified in `PROVENANCE.md`.

The provider implements:

- normal provider validation;
- bounded-artifact issuance;
- action and context restrictions;
- HMAC-SHA256 artifact authentication;
- nonce generation;
- issuance and expiration times;
- single-use artifact declaration;
- request binding.

### `RESULTS.md`

Recorded POC-001 behavioral results and evidence limitations.

### `PROVENANCE.md`

Artifact provenance, original source hashes, cross-host boundary correspondence, and publication status.

### `SHA256SUMS.txt`

SHA-256 manifest for files distributed in this public directory.

## Publication Boundary

The Raspberry Pi enforcement-boundary implementation is not published in this directory.

The original tested boundary source survives independently on both the Windows test host and Raspberry Pi.

The two retained copies are byte-identical and have SHA-256:

```text
7bd3b443caf4c5b8d88b70db9cbb8b4ec28df6fcdbbe301ba7cb402cfbb2905d
```

The public provider source has SHA-256:

```text
97aad386e48813488047503030de277d165a4a9040d758d7679d330a7ba0ebeb
```

Artifact-level details are recorded in `PROVENANCE.md`.

## Evidence Status

The original interactive terminal transcript from the July 11, 2026 execution is not included in this package.

The surviving evidence includes:

- the original provider implementation;
- the original boundary implementation retained outside the public package;
- an independently retained byte-identical copy of the boundary implementation on the Raspberry Pi;
- contemporaneous laboratory records of the tested conditions and observed results;
- SHA-256 identification of the surviving source artifacts.

No reconstructed terminal output is presented as original runtime evidence.

## What POC-001 Supports

POC-001 supports the tested behavioral claim that a previously issued, bounded artifact could authorize one matching request during provider unavailability while invalid, expired, mismatched, missing, or replayed artifacts were denied.

The proof demonstrated:

- provider-first validation during normal availability;
- bounded disconnected acceptance;
- action binding;
- context binding;
- request binding;
- expiration enforcement;
- single-use declaration;
- running-process replay denial;
- fail-closed behavior without a valid bounded artifact;
- return to provider-backed operation after provider restoration.

## What POC-001 Does Not Support

POC-001 does not establish exclusive provider cryptographic issuance authority.

Because the provider and Raspberry Pi boundary shared the HMAC secret, the boundary possessed cryptographic material sufficient to generate HMAC-authenticated artifacts.

POC-001 also does not establish:

- asymmetric provider authenticity;
- direct cryptographic verification on the ESP32;
- persistent spent-state across restart or power loss;
- crash-safe spend persistence;
- multi-boundary double-spend resistance;
- exactly-once physical execution;
- security of the Raspberry Pi after arbitrary privileged compromise.

Those properties are outside the scope of this proof.

## Result

POC-001 established the initial bounded disconnected-authority behavior and exposed the shared-secret trust limitation that was removed in POC-002.

The proof sequence therefore progresses from bounded behavior to stronger authority separation:

```text
POC-001
HMAC bounded disconnected authority
        |
        | shared-secret limitation identified
        v
POC-002
Ed25519 provider authenticity
        |
        | asymmetric provider/boundary trust separation
        v
POC-003
Ed25519 bounded disconnected single-use authority
```
