# SP-001 — Results

## Test Objective

SP-001 evaluated whether the existing NUVL provider-controlled bounded-authority path continued to operate when the provider and its Ed25519 private signing key were moved to a physically separate host from the Raspberry Pi verification/enforcement boundary.

The principal test variable was provider placement.

The underlying provider-authenticity and bounded-authority model was unchanged.

## Test Environment

### Separate Provider Host

- Host: `Xer0trust2`
- Operating system: Linux Mint
- Provider implementation: `poc003_ed25519_provider_1h.py`
- Provider address: `192.168.0.240:8091`
- Provider interface: `POST /issue-offline`
- Ed25519 private signing key: provider host

### NUVL Boundary

- Platform: Raspberry Pi 5
- Boundary implementation: `sp001_separate_provider_boundary.py`
- Boundary port: `8089`
- Provider public verification key: `/home/seth/poc002_ed25519_public.pem`
- Provider private signing key present on Pi: `False`
- Persistent replay state: `/home/seth/poc004_spent_state_archer.json`

SP-001 used a derivative of the previously tested persistent-replay boundary configured to contact the provider at its separate network location.

Source lineage and artifact identity are documented in `PROVENANCE.md`.

## Baseline Establishment

### Separate Provider Startup

The provider started successfully on `Xer0trust2`.

Observed:

    POC003_ED25519_OFFLINE_PROVIDER
    Listening on 0.0.0.0:8091
    Issue: POST /issue-offline
    Private key: /home/seth/nuvl-provider/poc002_ed25519_private.pem

**Result: PASS**

### Provider Reachability

The Raspberry Pi contacted the provider application at:

    http://192.168.0.240:8091/

The provider returned:

    {"error":"not_found"}

The application response established network reachability to the separate provider process.

**Result: PASS**

### Provider Request Processing

An intentionally incomplete request to:

    POST /issue-offline

returned:

    {"error":"ValueError('missing_device_id')"}

This established that the separate provider received and parsed the remote request.

**Result: PASS**

## Direct Remote Issuance

The Raspberry Pi submitted a complete issuance request directly to the separate provider.

Request fields included:

    device_id: esp32-field-01
    context: field_led_demo
    requested_action: accept
    nonce: sp001-test-001

The returned artifact included:

    alg: Ed25519
    context: field_led_demo
    decision: accepted
    device_id: esp32-field-01
    max_uses: 1
    offline_allowed: true
    provider_id: laptop-ed25519-provider-01
    requested_action: accept
    nonce: sp001-test-001

Artifact ID:

    a60543fa0024d3ffa192aa3e

A provider signature was present.

**Result: PASS**

The physically separate provider successfully issued signed bounded authority to the Raspberry Pi over the network.

## Boundary Startup

The SP-001 boundary started successfully.

Observed:

    POC004_PERSISTENT_REPLAY_PI_BOUNDARY
    Listening on 0.0.0.0:8089
    Provider: http://192.168.0.240:8091
    Public key: /home/seth/poc002_ed25519_public.pem
    Private key present on Pi: False
    Replay state: /home/seth/poc004_spent_state_archer.json
    Persistent replay entries loaded: 0

**Result: PASS**

Boundary health subsequently reported:

    {
      "boundary":"poc004_persistent_replay_pi",
      "public_key_loaded":true,
      "replay_state_path":"/home/seth/poc004_spent_state_archer.json",
      "replay_state_persistent":true,
      "spent_count":0,
      "status":"ok"
    }

The boundary was operational with the provider public verification key loaded.

## Boundary-Mediated Issuance

An issuance request was submitted through the NUVL boundary:

    device_id: esp32-field-01
    context: field_led_demo
    requested_action: accept
    nonce: sp001-boundary-001

The boundary returned:

    artifact_id: d7823d8bc39976c42c71ceaf
    decision: issued
    provider_verified: true
    reason: provider_signed_bounded_artifact

**Result: PASS**

The boundary obtained authority from the physically separate provider and reported successful provider verification before returning the bounded artifact.

## Bounded Spend

A fresh provider-signed artifact was issued with:

    nonce: sp001-spend-001

Artifact ID:

    a4c7425a7c3275cb376f0818

Issuance reported:

    provider_verified: true

The artifact was then submitted to the boundary spend path with the matching spend request.

Observed:

    artifact_id: a4c7425a7c3275cb376f0818
    decision: accepted
    max_uses: 1
    provider_contacted_for_spend: false
    provider_verified: true
    reason: offline_artifact_admissible
    replay_state_persisted_before_accept: true
    uses_consumed: 1

**Result: PASS**

The observed spend established that:

- the artifact was accepted as provider-authenticated;
- the provider was not contacted for the spend;
- the bounded request conditions were enforced;
- the single permitted use was consumed;
- replay state was reported persisted before acceptance.

## Provider Availability Control

The separate-provider topology was then exercised through an online → unavailable → restored sequence.

The Raspberry Pi boundary remained running throughout the sequence.

### Online Precondition

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

**Result: PASS**

Verified issuance was operational immediately before provider removal.

### Provider Unavailable

The provider process on `Xer0trust2` was stopped while the Raspberry Pi boundary remained operational.

Provider status reported:

    provider_available: false
    provider_url: http://192.168.0.240:8091

A new authority request using:

    nonce: sp001-evidence-offline

returned:

    artifact_id: null
    decision: denied
    provider_verified: false
    reason: provider_unavailable

**Result: PASS**

No new provider artifact was issued while the separate provider was unavailable.

The observed path denied the request rather than substituting locally generated authority.

### Provider Restored

The same provider implementation was restarted on `Xer0trust2`.

Provider status returned to:

    provider_available: true
    provider_url: http://192.168.0.240:8091

The Raspberry Pi boundary was not restarted.

A fresh authority request using:

    nonce: sp001-evidence-restored

returned:

    artifact_id: d3ce2c5e0751d89e4a3f72ce
    decision: issued
    provider_verified: true
    reason: provider_signed_bounded_artifact

**Result: PASS**

Verified provider issuance resumed without restarting or reprovisioning the NUVL boundary.

## Availability-Control Evidence

The provider-availability sequence was repeated in a captured terminal transcript:

    evidence/sp001_control_evidence.log

The transcript records:

1. healthy boundary and reachable separate provider;
2. successful verified issuance;
3. provider removal;
4. denial of new issuance with `provider_unavailable`;
5. provider restoration;
6. resumption of verified issuance.

This transcript was captured separately from the initial interactive SP-001 baseline.

Artifact identity and integrity information for the evidence file are maintained in `PROVENANCE.md` and `SHA256SUMS.txt`.

## Non-Test Operator Errors

Two command-entry errors occurred during interactive setup.

An initial request was sent to `/validate`, which is not exposed by the selected boundary implementation and returned:

    {"error":"not_found"}

A subsequent `/spend` request supplied the artifact package at the wrong JSON level and returned:

    decision: denied
    provider_verified: false
    reason: package_not_object

The request was corrected to the required interface shape:

    {
      "package": {...},
      "spend_request": {...}
    }

The subsequent bounded-spend test passed.

These events occurred before the intended authorization conditions were exercised and are not classified as SP-001 functional failures.

## Consolidated Results

| Test Condition | Observed Result |
|---|---|
| Separate provider startup | PASS |
| Pi-to-provider application reachability | PASS |
| Remote provider request processing | PASS |
| Direct remote Ed25519 issuance | PASS |
| SP-001 boundary startup | PASS |
| Provider public key loaded | PASS |
| Boundary-mediated provider issuance | PASS |
| Provider verification reported | PASS |
| Bounded artifact spend | PASS |
| Provider not contacted during bounded spend | PASS |
| Replay state reported persisted before acceptance | PASS |
| Online control issuance | PASS |
| Provider unavailability detected | PASS |
| New authority denied while provider unavailable | PASS |
| No artifact returned while provider unavailable | PASS |
| Provider restoration | PASS |
| Verified issuance resumed without boundary restart | PASS |
| Availability-control evidence captured | PASS |

## Overall Result

**SP-001: PASS**

SP-001 demonstrated that the existing Ed25519 provider-controlled bounded-authority path continued to operate when the provider and its private signing key were placed on a physically separate host from the Raspberry Pi verification/enforcement boundary.

During provider unavailability, the running boundary denied acquisition of new provider authority:

    PROVIDER ONLINE
            |
            | signed Ed25519 authority
            v
    boundary verifies
            |
            v
    ISSUED


    PROVIDER UNAVAILABLE
            |
            v
    boundary remains operational
            |
            | no verified new provider authority
            v
    DENIED
    artifact_id: null


    PROVIDER RESTORED
            |
            | signed Ed25519 authority
            v
    same running boundary verifies
            |
            v
    ISSUED

After provider restoration, verified issuance resumed without boundary restart or reprovisioning.

## Supported Claims

SP-001 supports the bounded claim that, within the tested configuration:

- an Ed25519 provider authority source operated on a physically separate host from the NUVL verification/enforcement boundary;
- the boundary obtained and verified provider-signed bounded authority across that separation;
- an issued bounded artifact was accepted through the existing spend path without contacting the provider for the spend;
- loss of the separate provider prevented acquisition of new provider authority through the tested issuance path;
- provider unavailability did not result in locally substituted authority through that path;
- verified issuance resumed after provider restoration without restarting the boundary.

## Claim Boundary

SP-001 does not establish:

- rejection of an unauthorized substitute provider;
- resistance to a compromised or malicious network intermediary;
- security after arbitrary privileged compromise of the Raspberry Pi boundary;
- endpoint-local Ed25519 verification;
- production key-management security;
- production infrastructure or network security;
- provider high availability.

Unauthorized provider substitution is evaluated separately by SP-002.
