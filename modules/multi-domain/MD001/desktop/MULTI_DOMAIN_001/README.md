# MD001 — Desktop Reference Implementation

## Overview

This directory preserves the original desktop implementation and offline validation package for MD001 — Multi-Domain Stateless Verification.

The implementation evaluates whether a signed assertion originating in one technical domain can be transported through a mechanical intermediary and independently verified in another domain without transferring authorization authority to the intermediary.

The desktop implementation established the application contract, verification behavior, source provenance, and preliminary test results before physical-network deployment.

**Implementation:** MD001 R1  
**Organization:** Xer0trust LLC  
**Original completion date:** November 12, 2026 UTC  
**Original build status:** `MD001_LOCAL_BUILD_VALIDATED_NOT_DEPLOYED`  
**Final offline validation:** 21 PASS / 0 FAIL

The original desktop build was a local loopback simulation.

The later physical-network experiments are documented separately under the MD001 scored evidence directories.

## 1. Implementation Objective

The desktop implementation was developed to evaluate four principal properties.

1. A producer can create a signed assertion describing a completed local operation.
2. A mechanical intermediary can transport that assertion without interpreting or modifying its signed content.
3. A receiving domain can independently validate the assertion using locally provisioned verification material.
4. Verification does not require the originating producer to remain available or the verifier to maintain a history of previously observed assertions.

The implementation deliberately separates assertion verification from authorization and execution.

A valid signature establishes that the assertion corresponds to the provisioned signing key.

It does not independently establish that the asserted event occurred.

## 2. Architecture

The original desktop implementation uses a local simulation of the intended cross-domain architecture.

```text
Domain A
Producer
   |
   | Local operation
   | Signed assertion
   v
Mechanical Relay
   |
   | Byte-preserving transport
   v
Domain B
Verifier
   |
   | Parse assertion
   | Resolve provisioned key
   | Verify signature
   | Evaluate local criteria
   v
Verification Result
```

The relay does not possess the producer's signing authority.

The verifier does not issue authorization for the underlying operation.

The producer and verifier use compatible cryptographic primitives without sharing operational state.

### Principal Components

| Component | Responsibility |
|---|---|
| Producer | Performs the local operation and creates the signed assertion |
| Artifact module | Defines canonical encoding, signing, and verification behavior |
| Mechanical relay | Forwards the HTTP request toward the configured destination |
| Verifier | Validates the assertion against locally provisioned trust |
| Test harness | Coordinates local simulation and records evidence |
| Evidence utilities | Preserve process identities, observations, and integrity records |

The architecture is assertion-oriented.

It does not incorporate the authorization-consumption or execution-state mechanisms used in other Xer0trust experiments.

## 3. Artifact Contract

The artifact format is defined in:

```text
ARTIFACT_CONTRACT.md
```

### Envelope

The transmitted envelope contains exactly two top-level fields:

```json
{
  "event": {},
  "signature": ""
}
```

The `event` object contains exactly six signed fields.

| Field | Type | Constraint |
|---|---|---|
| `version` | JSON integer | Exactly `1` |
| `producer_id` | String | Provisioned producer identity |
| `key_id` | String | SHA-256 fingerprint of the Ed25519 public key |
| `artifact_id` | String | Canonical UUID |
| `event_id` | String | Locally recognized event identifier |
| `outcome` | String | Locally recognized outcome |

The local experiment uses:

```text
producer_id = DOMAIN_A
event_id = LOCAL_SORT_V1
outcome = SUCCESS
```

Unknown fields and duplicate JSON keys are rejected.

### Signed Bytes

The signed message consists of a domain-separation prefix followed immediately by canonical UTF-8 JSON of the event.

```text
NUVL-MD001-ARTIFACT-v1|
```

There is no trailing newline or byte-order mark.

The implementation uses Ed25519 signatures.

The signature is represented as canonical, unpadded URL-safe Base64.

The complete transmitted envelope must satisfy the canonical encoding requirements.

### Artifact Hashing

The recorded artifact SHA-256 identifies the entire transmitted envelope, including the signature.

This is distinct from the canonical event bytes used as input to the signing operation.

The distinction matters when comparing artifacts at transport observation points.

## 4. Verification Behavior

The verifier performs the following operations:

1. Parses the received artifact.
2. Validates its structure and canonical representation.
3. Identifies the claimed producer and signing-key fingerprint.
4. Resolves the corresponding public key from locally provisioned trust.
5. Verifies the Ed25519 signature.
6. Evaluates the configured local event and outcome criteria.
7. Returns a verification decision.

The trust mapping has the following structure:

```json
{
  "DOMAIN_A": {
    "sha256:<fingerprint>": "<raw-public-key-hex>"
  }
}
```

The key identifier contained in an artifact does not establish trust by itself.

The verifier must locate the corresponding key in its own provisioned trust configuration.

### Rejection Conditions

The implementation rejects:

- Malformed artifacts.
- Unsupported or invalid structures.
- Unknown producers.
- Unknown signing keys.
- Invalid producer/key bindings.
- Invalid signatures.
- Assertions that fail local event or outcome criteria.
- Invalid local verification configuration.

The artifact contract specifies a maximum input size of 65,536 bytes.

### Stateless Verification

The verifier does not use:

- A previous-artifact history.
- A consumed-authority ledger.
- A cached authorization decision.
- A producer database.
- A live producer connection.
- A previous session.
- A timestamp or sequence counter.

Evidence records are generated downstream of the verification function.

They are not consulted when deciding whether an assertion is valid.

This is an intentional architectural constraint.

It also means that the verifier does not prevent repeated verification of an unchanged valid assertion.

## 5. Source Provenance

The original source review is documented in:

```text
PROVENANCE.md
SOURCE_REUSE.md
reference/SOURCE_INVENTORY.json
```

The source inventory records 34 inspected files, including their identities and SHA-256 values.

### MH001 Mechanical Relay

The implementation reuses three frozen MH001 R4.3 source files:

```text
reference/MH001_R43/hub.py
reference/MH001_R43/routes.py
reference/MH001_R43/wire.py
```

These files were retained without modification.

The desktop implementation supplies a new launcher to accommodate the MD001 topology.

The original MH001 command-line interface expected a two-hub arrangement and was not directly reused.

The relay retains its mechanical forwarding behavior.

No signature-verification or authorization logic was added to the frozen relay.

### MP005 Cryptographic Reference

The implementation references:

```text
reference/MP005/provider_a/provider_a.py
```

The `canonical_bytes` function was copied unchanged from the MP005 provider implementation.

The Ed25519 signing and verification patterns were adapted to the MD001 assertion schema and domain-separation tag.

The complete MP005 provider implementation was not imported.

No MP005 authorization or consumption state was transferred into MD001.

### Other Inspected Sources

The source review also examined:

- MP004 verification and evidence conventions.
- MP006 evidence and persistence-test conventions.
- ESP-LOCAL-008 physical endpoint and witness designs.

These sources informed compatibility review and experimental design.

They were not incorporated as active MD001 authorization or execution components.

### Reference Identity

The preserved source review identifies the MP005 reference checkout:

```text
73713f6e9ed9c95251cc69ec88ef816cab771ac0
```

The source inventory retains individual file hashes.

The reference commit and file hashes provide provenance for the inspected material.

They do not imply that the separate MD001 desktop build was committed under the same revision.

## 6. Implementation Files

### Core Source

```text
src/
├── artifact.py
└── service.py
```

`artifact.py` implements the assertion contract and cryptographic operations.

`service.py` provides the supporting service behavior used by the local implementation.

### Offline Test Harness

```text
tests/
└── run_offline.py
```

The offline harness coordinates the simulated producer, relay, ingress observations, verifier, and test cases.

### Reference and Preparation Utilities

```text
prepare_reference.py
manifest.py
requirements.txt
```

`prepare_reference.py` supports preparation of the retained source references.

`manifest.py` supports evidence-manifest verification.

`requirements.txt` records the Python dependency requirements for the desktop implementation.

### Documentation

```text
ARTIFACT_CONTRACT.md
COMPLETION.md
PROVENANCE.md
SOURCE_REUSE.md
```

These documents preserve the original implementation contract, completion status, provenance, and source compatibility review.

## 7. Offline Validation Evidence

The original desktop package preserves two offline validation attempts.

```text
evidence/offline/
├── 20261112T012548Z_f9d58244/
└── 20261112T025926Z_4d05fe22/
```

### Initial Attempt

The initial attempt recorded:

```text
LOCAL_VALIDATION_FAILED
```

Its result was:

| Property | Recorded value |
|---|---|
| Passed | 1 |
| Failed | 1 |
| Mode | `OFFLINE_LOOPBACK_SIMULATION_ONLY` |
| Physical network scored | `false` |

The failure occurred when the Windows sandbox denied a loopback socket operation.

The preserved error identifies:

```text
WinError 10013
```

The failed check was:

```text
harness_completed
```

The source-inventory comparison passed.

The failure was an infrastructure restriction, not a recorded failure of the cryptographic verification mechanism.

The attempt remains preserved and was not overwritten.

### Final Successful Attempt

The final run is:

```text
evidence/offline/20261112T025926Z_4d05fe22/
```

Its preserved `RESULTS.json` records:

```json
{
  "mode": "OFFLINE_LOOPBACK_SIMULATION_ONLY",
  "passed": 21,
  "failed": 0,
  "physical_esp_completed": false,
  "physical_network_scored": false,
  "status": "MD001_LOCAL_BUILD_VALIDATED_NOT_DEPLOYED"
}
```

The recorded environment was:

| Property | Recorded value |
|---|---|
| Operating system | Windows 11 |
| Python | `3.14.3` |
| Cryptography | `49.0.0` |
| Passed checks | 21 |
| Failed checks | 0 |

All 21 defined offline checks passed.

## 8. Offline Test Results

### B01 — Valid Assertion

The offline B01 simulation evaluated:

- Local operation completion.
- Assertion signing.
- Mechanical relay forwarding.
- Byte preservation.
- Independent signature verification.

The original artifact SHA-256 was:

```text
7534a478ad51ffd1ac2ca05bff2039813d0305a8e05174d572a1ffc3e021f64b
```

The producer, relay-adjacent observations, and verifier ingress recorded the same digest.

**Offline B01: PASS**

### N01 — Modified Assertion

The offline N01 simulation modified a signed field without replacing the original signature.

The modified artifact SHA-256 was:

```text
5b747613a2baa19ef6f2f69cf936c528c4f4b4c7ad9674ec014e5bda5b614b64
```

The verifier returned:

```json
{
  "accepted": false,
  "reason": "invalid_signature",
  "signature_checks": 1
}
```

**Offline N01: PASS**

### B02 — Producer-Unavailable Verification

The offline B02 simulation terminated the producer process and evaluated the previously issued assertion using a restarted verifier.

The preserved result identifies:

```text
Old verifier PID: 20908
New verifier PID: 25580
```

The producer-unavailable record identifies:

```json
{
  "simulated": true,
  "physical_power_off_observed": false
}
```

The original assertion was accepted by the restarted verifier.

One fresh Ed25519 signature check was recorded.

**Offline B02: PASS**

This was simulated process unavailability.

It was not a physical power-disconnection experiment.

## 9. Additional Validation Checks

The final offline run also passed checks covering:

- Valid Ed25519 signing and verification.
- Rejection after modification of a signed field.
- Unknown-key rejection.
- Producer/key mismatch rejection.
- Malformed-artifact rejection.
- Deterministic canonical encoding.
- Unique artifact identifiers.
- Rejection of signatures made with the wrong private key.
- Rejection of invalid signature bytes.
- Rejection when valid signatures fail local criteria.
- Absence of verification-history dependencies.
- Absence of producer-network dependencies during verification.
- Separation of verification from execution imports.
- Preservation of original reference sources.
- Relay transport observation consistency.
- Agreement between saved evidence and recorded responses.

The final `RESULTS.json` contains the individual check names and recorded observations.

The summary result was:

```text
21 PASS
0 FAIL
```

## 10. Evidence Integrity

The final offline run preserves:

```text
RESULTS.json
SHA256SUMS.txt
build_identity.json
build_snapshot/
```

The evidence also includes:

- Original producer operation.
- Original signed assertion.
- Exact signed bytes.
- Disposable test signing key.
- Public trust configuration.
- Relay observations.
- Modified assertion.
- Mutation record.
- Verifier ingress artifacts.
- Verification decisions.
- Process identities.
- Standard output and error.
- Source snapshots.

### Recorded Hashes

| Object | SHA-256 |
|---|---|
| Original offline artifact | `7534a478ad51ffd1ac2ca05bff2039813d0305a8e05174d572a1ffc3e021f64b` |
| Modified offline artifact | `5b747613a2baa19ef6f2f69cf936c528c4f4b4c7ad9674ec014e5bda5b614b64` |
| Final `RESULTS.json` | `667c676b3b90ea65e47d4a78ac62b9b605d632697a838f48f8215aed7548b6f7` |
| Final run `SHA256SUMS.txt` | `9ee74d9c81c1707ccb703cfa05f5eec7373ec9cc04778d137474ab4491927484` |

The original provenance documentation describes a package-level SHA-256 inventory and a separate digest for that inventory.

The manifests are integrity records.

They are not cryptographic signatures or independent attestations.

## 11. Independent Evidence Review

The original desktop evidence can be inspected without rerunning the implementation.

### Step 1 — Review the Artifact Contract

Inspect:

```text
ARTIFACT_CONTRACT.md
```

Confirm the signed fields, canonicalization requirements, signature format, and trust mapping.

### Step 2 — Review Source Provenance

Inspect:

```text
PROVENANCE.md
SOURCE_REUSE.md
reference/SOURCE_INVENTORY.json
```

Confirm the source identities, reused components, and documented adaptations.

### Step 3 — Review the Initial Failed Attempt

Inspect:

```text
evidence/offline/20261112T012548Z_f9d58244/
```

Review `RESULTS.json` and `HARNESS_ERROR.txt`.

Confirm the recorded infrastructure failure.

### Step 4 — Review the Final Successful Run

Inspect:

```text
evidence/offline/20261112T025926Z_4d05fe22/
```

Confirm:

```text
passed = 21
failed = 0
physical_network_scored = false
```

### Step 5 — Review the Three Simulated Cases

Inspect:

```text
B01-observed_hashes.json
B01-response.json

N01-response.json

B02-producer-unavailable.json
B02-response.json
```

Compare these records with the corresponding preserved artifacts and verifier decisions.

### Step 6 — Verify Evidence Integrity

Review the final run's `SHA256SUMS.txt`.

Compare the retained build snapshot with the documented source identities.

A new execution requires a compatible runtime, the recorded application sources, and the applicable test dependencies.

## 12. Relationship to Physical-Network Experiments

The original desktop implementation was completed before the physical-network MD001 experiments.

| Stage | Environment | Classification |
|---|---|---|
| Desktop R1 | Windows loopback simulation | Non-scored |
| Later local validation | Local adapter and synthetic stream tests | Non-scored |
| Physical B01 | Laboratory network | Scored |
| Physical N01 | Laboratory network | Scored |
| Physical B02 | Laboratory network | Scored |

The original desktop build established implementation behavior and test readiness.

The later scored experiments provide separate evidence of behavior across the deployed laboratory network.

Their artifacts, process identities, and SHA-256 values are different.

The original desktop simulation must not be represented as a physical-network execution.

## 13. Scope and Limitations

The original desktop implementation demonstrates that the defined assertion-verification behavior passed its offline test conditions.

The evidence supports:

- Canonical signed-artifact generation.
- Ed25519 signature verification.
- Mechanical relay transport in the local simulation.
- Rejection of the tested signed-field modification.
- Verification after simulated producer-process termination.
- Verification using a restarted process.
- Selected malformed-artifact and trust-binding rejection behavior.
- Separation of verification logic from execution mechanisms.

It does not establish:

- Physical-network isolation between independently administered domains.
- Physical producer power loss.
- Firewall enforcement.
- Physical packet-capture reconstruction.
- Physical actuation or execution enforcement.
- Durable single-use authorization consumption.
- Replay prevention.
- Resistance to signing-key compromise.
- Production deployment readiness.

The verifier intentionally permits repeated verification of an unchanged valid assertion.

That behavior is consistent with the assertion-only contract.

It must not be interpreted as permission to repeat the underlying operation.

## 14. Original Completion Status

The original completion report records:

```text
MD001_LOCAL_BUILD_VALIDATED_NOT_DEPLOYED
```

The final desktop run passed all 21 defined offline checks.

The original project stopped at its designated deployment gate.

At that point:

- No physical-network scored run had been performed.
- No live network configuration had been changed.
- No physical execution command had been triggered.
- No ESP actuation evidence had been collected.

Those statements describe the original November 12 desktop handoff.

They do not describe the later state of the MD001 laboratory experiments.

The subsequent physical-network B01, N01, and B02 results are documented in their own evidence directories.

## 15. Conclusion

The MD001 desktop implementation established a bounded, assertion-oriented verification architecture using canonical signed artifacts, a mechanical relay, and independent verification against locally provisioned trust.

The original offline validation completed with:

```text
21 PASS
0 FAIL
```

The preserved source inventory, implementation contract, process records, test artifacts, and integrity manifests support independent review of that result.

The desktop evidence establishes the original implementation baseline.

The separately published physical-network scored experiments establish the subsequent laboratory observations.
