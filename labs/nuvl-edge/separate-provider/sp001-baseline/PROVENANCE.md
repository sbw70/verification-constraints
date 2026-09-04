# SP-001 — Provenance

## Purpose

This document records the source, host, file-integrity, and publication provenance associated with SP-001.

SP-001 evaluated NUVL operation with the provider and Ed25519 private signing key hosted on a physically separate machine from the Raspberry Pi verification/enforcement boundary.

The purpose of this document is to distinguish:

- original working files;
- transferred test files;
- SP-001-specific derivatives;
- cryptographic test material;
- independently verified cross-host copies;
- published reproduction artifacts.

## Test Date

SP-001 separate-provider setup and execution occurred on:

`2026-09-02`

## Systems

### Windows Working System

Working directory:

`C:\Users\holiw\esp32-main`

This system contained the selected provider implementation and laboratory Ed25519 key material before transfer to the separate provider host.

### Separate Provider Host

Hostname:

`Xer0trust2`

Operating system:

Linux Mint

Provider working directory:

`/home/seth/nuvl-provider`

Network address during SP-001:

`192.168.0.240`

The provider service executed on this host.

### NUVL Boundary Host

Platform:

Raspberry Pi 5

Hostname:

`xer0trust-pi`

Network address during SP-001:

`192.168.0.94`

The NUVL verification/enforcement boundary executed on this host.

## Provider Source

Selected provider implementation:

`poc003_ed25519_provider_1h.py`

### Windows Working Copy

SHA-256:

`e7206aeb42a4b2f903cdf01d21604e2d19a7d0a2a79962e55982524de69c4d62`

### Separate Provider Copy

Path:

`/home/seth/nuvl-provider/poc003_ed25519_provider_1h.py`

SHA-256:

`e7206aeb42a4b2f903cdf01d21604e2d19a7d0a2a79962e55982524de69c4d62`

Result:

**MATCH**

The provider implementation transferred to `Xer0trust2` was byte-identical to the selected Windows working copy.

## Ed25519 Private Test Key

File:

`poc002_ed25519_private.pem`

### Windows Working Copy

SHA-256:

`cfdd77949cea7df748af6f0c45e9b2b2755a825ce178bc6e51d7fd4671bbc999`

### Separate Provider Copy

Path:

`/home/seth/nuvl-provider/poc002_ed25519_private.pem`

SHA-256:

`cfdd77949cea7df748af6f0c45e9b2b2755a825ce178bc6e51d7fd4671bbc999`

Result:

**MATCH**

The private key used by the physically separate provider was byte-identical to the selected laboratory test key.

## Ed25519 Public Verification Key

File:

`poc002_ed25519_public.pem`

SHA-256:

`2fd9c44a0579b985bc44722313725c8a6fd532b665b617b3e5082efb14c49f63`

The Raspberry Pi boundary used this public key to verify provider-issued Ed25519 signatures.

The private signing key was not present on the Raspberry Pi during SP-001.

Boundary startup reported:

    Private key present on Pi: False

## Test-Key Publication Status

The Ed25519 keypair used for SP-001 is laboratory test material.

The keypair has no production, operational, account, identity, or external trust relationship.

The private key may be published intentionally with the SP-001 reproduction package.

Publication of the private key does not expose operational authority because no operational system relies on this keypair.

The published keypair must therefore be interpreted as reproducibility material, not protected credential material.

## Boundary Source

Original source:

`/home/seth/poc004_pi_boundary_persistent_archer.py`

SHA-256:

`a1ca45bdae628b318d208120c51c25ba8281fdd22fecd6d5e87a993e51a61e26`

SP-001 derivative:

`/home/seth/sp001_separate_provider_boundary.py`

SHA-256:

`f35855d54933ee1f188576d9a8dc0eb9c30f8e7a5de821772f929df9cb801637`

## Boundary Derivation

The SP-001 boundary was created from the previously tested persistent-replay boundary.

The provider network location was changed from:

    PROVIDER_BASE = "http://192.168.0.50:8091"

to:

    PROVIDER_BASE = "http://192.168.0.240:8091"

A source diff confirmed that this provider-location change was the only modification between the selected source boundary and the SP-001 derivative.

The resulting SHA-256 change is therefore attributable to that source modification.

## Provider Configuration

The provider source used:

    HOST = "0.0.0.0"
    PORT = 8091
    EXPECTED_CONTEXT = "field_led_demo"

The provider required request fields including:

- `device_id`
- `context`
- `requested_action`
- `nonce`

The accepted requested action was:

`accept`

The provider exposed:

`POST /issue-offline`

## Boundary Configuration

The SP-001 boundary reported:

    Listening on 0.0.0.0:8089
    Provider: http://192.168.0.240:8091
    Public key: /home/seth/poc002_ed25519_public.pem
    Private key present on Pi: False
    Replay state: /home/seth/poc004_spent_state_archer.json
    Persistent replay entries loaded: 0

The boundary therefore operated with:

- remote provider connectivity;
- local public-key verification;
- no provider private signing key;
- persistent spent-state enforcement.

## Direct Provider-Issuance Witness

Before boundary-mediated issuance, the Raspberry Pi sent a complete request directly to the provider at:

`http://192.168.0.240:8091/issue-offline`

The provider returned an Ed25519-signed artifact.

Observed artifact identifier:

`a60543fa0024d3ffa192aa3e`

Observed fields included:

    alg: Ed25519
    provider_id: laptop-ed25519-provider-01
    device_id: esp32-field-01
    context: field_led_demo
    requested_action: accept
    nonce: sp001-test-001
    max_uses: 1
    offline_allowed: true

This provides direct evidence that the separate provider host was performing signed issuance.

## Boundary-Mediated Issuance Witness

A subsequent issuance request was submitted through the Raspberry Pi boundary.

Observed artifact identifier:

`d7823d8bc39976c42c71ceaf`

Observed boundary result:

    decision: issued
    provider_verified: true
    reason: provider_signed_bounded_artifact

This establishes that the Pi received and successfully verified authority issued by the separate provider.

## Bounded-Spend Witness

A fresh artifact was issued for the spend path.

Artifact identifier:

`a4c7425a7c3275cb376f0818`

The subsequent spend returned:

    decision: accepted
    provider_verified: true
    provider_contacted_for_spend: false
    reason: offline_artifact_admissible
    replay_state_persisted_before_accept: true
    uses_consumed: 1

This establishes that the spend was authorized by previously issued provider authority rather than by a new provider interaction during execution.

## Operator Errors

Two interactive command-entry errors occurred during testing:

1. a request was sent to `/validate`, which is not exposed by the selected boundary implementation;
2. an initial `/spend` request placed the package at the wrong JSON level.

These requests returned application-level errors and did not exercise the intended cryptographic authorization path.

The requests were corrected before the successful SP-001 issuance and spend results.

They are documented for completeness and are not treated as functional test failures.

## Separate-Provider Availability Control

After the initial interactive SP-001 baseline, the separate-provider topology was exercised through a captured online → unavailable → restored control sequence.

The Raspberry Pi boundary remained running throughout the sequence.

No boundary restart or reprovisioning occurred between the three conditions.

### Online Precondition

The captured control began with the boundary operational and the separate provider reachable.

Boundary health reported:

    status: ok
    public_key_loaded: true
    replay_state_persistent: true

Provider status reported:

    provider_available: true
    provider_url: http://192.168.0.240:8091

A fresh issuance request using:

    nonce: sp001-evidence-online

returned:

    artifact_id: 4502634688e41c69557d9ad8
    decision: issued
    provider_verified: true
    reason: provider_signed_bounded_artifact

This established a successful provider-authenticated issuance immediately before the provider-unavailable condition.

### Provider-Unavailable Condition

The provider process on `Xer0trust2` was stopped while the Raspberry Pi boundary remained running.

Provider status then reported:

    provider_available: false
    provider_url: http://192.168.0.240:8091

A new issuance request using:

    nonce: sp001-evidence-offline

returned:

    artifact_id: null
    decision: denied
    provider_verified: false
    reason: provider_unavailable

No new provider artifact was returned.

This established that the running boundary did not obtain or originate new provider authority while the physically separate provider was unavailable.

### Provider Restoration

The same provider implementation was restarted on `Xer0trust2`.

The Raspberry Pi boundary remained running without restart.

Provider status returned to:

    provider_available: true
    provider_url: http://192.168.0.240:8091

A fresh issuance request using:

    nonce: sp001-evidence-restored

returned:

    artifact_id: d3ce2c5e0751d89e4a3f72ce
    decision: issued
    provider_verified: true
    reason: provider_signed_bounded_artifact

Verified issuance therefore resumed after provider restoration without restarting or reprovisioning the NUVL boundary.

## Evidence Classification

SP-001 provenance consists of several evidence classes.

### Cryptographic File Integrity

SHA-256 comparison established byte identity for:

- provider source transferred from Windows to `Xer0trust2`;
- Ed25519 private test key transferred from Windows to `Xer0trust2`.

### Source Derivation

SHA-256 and source diff establish:

- identity of the original boundary source;
- identity of the SP-001 derivative;
- the provider-address change that created the derivative.

### Initial Runtime Observation

The initial interactive SP-001 execution established:

- provider startup;
- provider application reachability;
- remote request parsing;
- signed remote issuance;
- boundary startup;
- public-key loading;
- private-key absence on the Pi;
- boundary-mediated provider verification;
- successful bounded spend;
- persistence-before-accept behavior.

These observations were transcribed from the active test session.

### Captured Availability-Control Evidence

The subsequent separate-provider availability control was captured using a terminal transcript.

Evidence file:

`evidence/sp001_control_evidence.log`

SHA-256:

`13ea30307548cc0d4e80e19ce27dbc3b187d1b6bfa29f38572b05b459965b119`

The captured transcript records:

1. healthy Raspberry Pi boundary;
2. separate provider reachable;
3. successful verified issuance while the provider was online;
4. separate provider unavailable;
5. new issuance denied with `provider_unavailable`;
6. `artifact_id: null`;
7. `provider_verified: false`;
8. separate provider restored;
9. successful verified issuance resumed;
10. no Raspberry Pi boundary restart between the unavailable and restored conditions.

The transcript was captured after the initial interactive SP-001 baseline and is identified as a separate evidence-capture run.

It is not represented as the original SP-001 terminal transcript.

### Repository Documentation

The SP-001 repository package documents:

- test purpose;
- architecture;
- observed results;
- provenance;
- published source;
- test key material;
- captured runtime evidence;
- published file integrity.

## Runtime Evidence Status

SP-001 contains two runtime-evidence classes.

### Initial Baseline

The initial separate-provider baseline was observed interactively.

Its documented outputs were transcribed from the active test session.

A complete raw terminal transcript of that initial execution was not retained.

### Captured Availability Control

The subsequent online → unavailable → restored control was captured directly to:

`evidence/sp001_control_evidence.log`

The captured file was hashed immediately after the terminal transcript was closed.

SHA-256:

`13ea30307548cc0d4e80e19ce27dbc3b187d1b6bfa29f38572b05b459965b119`

This file provides direct retained evidence for the separate-provider availability and restoration control.

## Publication Artifacts

The SP-001 publication package may include:

    README.md
    RESULTS.md
    PROVENANCE.md
    provider/poc003_ed25519_provider_1h.py
    provider/poc002_ed25519_private.pem
    trust/poc002_ed25519_public.pem
    boundary/sp001_separate_provider_boundary.py
    evidence/sp001_control_evidence.log

`SHA256SUMS.txt` should be generated only after the final publication bytes are fixed.

The manifest should include every published SP-001 artifact except the manifest itself.

## Publication Boundary

SP-001 may publish the complete laboratory provider keypair because the keys are intentionally disposable test material.

Published source and key files should retain their exact tested bytes where possible.

If any source file is sanitized or otherwise modified for publication, the modified file must be treated as a publication derivative and assigned a new SHA-256 value.

Original tested-source hashes must not be attached to modified publication copies.

The captured evidence transcript should be published as the captured file rather than reconstructed manually.

## Supported Provenance Statement

The available provenance supports the following statement:

> SP-001 used a byte-verified provider implementation and byte-verified laboratory Ed25519 private key transferred to a physically separate Linux provider host. The Raspberry Pi boundary retained the corresponding public verification key without the provider private key. The SP-001 boundary was derived from the existing persistent-replay implementation by changing only the provider network location. The resulting separate-host path successfully produced, verified, and consumed provider-signed bounded authority. A subsequent captured control demonstrated that new issuance was denied when the separate provider was unavailable and resumed after provider restoration without restarting the Raspberry Pi boundary.

## Limitations

This provenance record does not establish:

- protection of the provider host against privileged compromise;
- protection of the Raspberry Pi against privileged compromise;
- production key custody;
- production identity assurance;
- resistance to malicious network intermediaries;
- endpoint-side signature verification;
- unauthorized provider substitution behavior;
- provider high-availability behavior.

Those properties require separate evidence.
