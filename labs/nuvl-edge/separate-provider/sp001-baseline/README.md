# SP-001 — Separate Provider Baseline

## Purpose

SP-001 tests whether the existing NUVL provider-controlled bounded-authority model continues to operate when the provider and its private signing key are moved to a physically separate host from the NUVL verification/enforcement boundary.

The test changes provider placement without changing the underlying authority model.

## Architecture

SP-001 used three distinct roles:

    Separate Provider Host
    Linux Mint / Xer0trust2
    Ed25519 private signing key
    Provider service
            |
            | network
            v
    Raspberry Pi 5
    NUVL verification/enforcement boundary
    Ed25519 public verification key
    No provider private key
            |
            v
    Bounded execution path

The provider host and Raspberry Pi boundary operated as separate machines with separate execution environments.

## Components

### Provider Host

Host:

`Xer0trust2`

Provider implementation:

`poc003_ed25519_provider_1h.py`

Provider interface:

`POST /issue-offline`

The provider retained the Ed25519 private signing key and issued signed bounded-authority artifacts.

### NUVL Boundary

Platform:

Raspberry Pi 5

SP-001 boundary implementation:

`sp001_separate_provider_boundary.py`

The SP-001 implementation was derived from the previously tested persistent-replay boundary.

The provider address was changed to reference the physically separate provider host.

No provider private signing key was present on the Raspberry Pi.

The boundary retained the corresponding Ed25519 public verification key.

## SP-001 Source Change

The SP-001 boundary changed provider placement while preserving the existing verification and enforcement logic.

The functional source change was limited to the provider network location:

    Previous provider:
    http://192.168.0.50:8091

    SP-001 provider:
    http://192.168.0.240:8091

A source diff confirmed that the provider address was the only modification to the selected boundary implementation.

## Baseline Preconditions

Before the SP-001 transaction:

- the separate provider service was running;
- the provider was reachable from the Raspberry Pi;
- the provider private key was present on the provider host;
- the Pi boundary loaded the provider public key;
- the Pi reported no provider private key present;
- persistent replay state was available;
- the Pi boundary was listening on its configured interface.

The provider reported:

    POC003_ED25519_OFFLINE_PROVIDER
    Listening on 0.0.0.0:8091
    Issue: POST /issue-offline

The SP-001 boundary reported:

    POC004_PERSISTENT_REPLAY_PI_BOUNDARY
    Listening on 0.0.0.0:8089
    Provider: http://192.168.0.240:8091
    Public key: /home/seth/poc002_ed25519_public.pem
    Private key present on Pi: False
    Persistent replay entries loaded: 0

## Provider Reachability

Application-layer reachability from the Raspberry Pi to the separate provider was established before the authority test.

A request to the provider reached the remote application and received an application response.

A complete issuance request sent directly from the Pi to the separate provider subsequently returned an Ed25519-signed bounded-authority artifact.

The returned artifact identified:

- algorithm: `Ed25519`;
- provider: `laptop-ed25519-provider-01`;
- context: `field_led_demo`;
- device: `esp32-field-01`;
- requested action: `accept`;
- maximum uses: `1`;
- offline authority permitted: `true`.

This established that signed authority was being issued by the separate provider host.

## Boundary-Mediated Issuance

The NUVL boundary was then used to obtain authority from the separate provider.

The boundary returned:

    decision: issued
    provider_verified: true
    reason: provider_signed_bounded_artifact

The issued artifact was therefore accepted by the boundary only after successful provider-signature verification.

## Bounded Spend

A fresh provider-signed artifact was issued through the boundary and submitted to the bounded spend path.

The spend returned:

    decision: accepted
    provider_verified: true
    provider_contacted_for_spend: false
    reason: offline_artifact_admissible
    max_uses: 1
    uses_consumed: 1
    replay_state_persisted_before_accept: true

The provider was not contacted during the spend itself.

Authority for that action came from the previously issued and verified provider-signed artifact.

The boundary enforced the artifact's existing limits rather than originating new authority during execution.

## Result

**PASS**

SP-001 demonstrated successful provider-authenticated bounded authority with the provider executing on a physically separate host from the NUVL verification/enforcement boundary.

The demonstrated path was:

    Separate provider
            |
            | Ed25519-signed bounded authority
            v
    NUVL boundary
            |
            | signature verified
            | bounds enforced
            v
    admissible single-use spend
            |
            v
    ACCEPT

The Pi boundary possessed the provider public verification key but not the provider private signing key.

## Supported Claim

SP-001 supports the following claim:

> A provider-controlled Ed25519 authority source can operate on a physically separate host from the NUVL verification/enforcement boundary while preserving provider-authenticated bounded authority.

## What SP-001 Does Not Establish

SP-001 does not by itself establish:

- provider-unavailable fail-closed behavior in the separate-host topology;
- recovery after loss of the separate provider;
- rejection of an unauthorized substitute provider;
- resistance to a compromised network forwarder or relay;
- resistance to arbitrary compromise of the Pi enforcement boundary;
- Ed25519 verification directly at the ESP32 endpoint;
- production key-management security;
- production network security;
- high-availability provider operation.

These require separate controls or adversarial tests.

## Test Key Material

Ed25519 key material associated with this laboratory test may be published for reproduction.

The keypair is test-only material.

It has no production, operational, account, identity, or external trust relationship.

Publication of the test private key does not transfer any operational authority because no operational system relies on that key.

## Evidence

SP-001 evidence and provenance are documented separately in:

- `RESULTS.md`
- `PROVENANCE.md`
- `evidence/`

Published artifact integrity is recorded in:

- `SHA256SUMS.txt`

## Relationship to Prior NUVL Testing

SP-001 builds on the previously demonstrated NUVL Ed25519 and bounded-authority path.

It does not replace the earlier provider-authenticity, disconnected-authority, persistent replay, double-spend, or crash-durability tests.

The new variable introduced by SP-001 is physical separation of the provider authority source from the NUVL verification/enforcement boundary.
