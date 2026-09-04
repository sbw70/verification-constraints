# SP-001 — Results

## Test Objective

SP-001 evaluated whether the existing NUVL provider-controlled bounded-authority path continued to operate when the provider and its Ed25519 private signing key were moved to a physically separate host from the Raspberry Pi verification/enforcement boundary.

The test was limited to provider placement.

No change was made to the underlying provider-authenticity or bounded-authority model.

## Test Environment

### Separate Provider Host

Host:

`Xer0trust2`

Operating system:

Linux Mint

Provider implementation:

`poc003_ed25519_provider_1h.py`

Provider address:

`192.168.0.240:8091`

Provider interface:

`POST /issue-offline`

The provider host held the Ed25519 private signing key.

### NUVL Boundary

Platform:

Raspberry Pi 5

Boundary implementation:

`sp001_separate_provider_boundary.py`

Boundary address:

Port `8089`

Provider public verification key:

`/home/seth/poc002_ed25519_public.pem`

Provider private key present on Pi:

`False`

Persistent replay state:

`/home/seth/poc004_spent_state_archer.json`

## Source-Controlled Change

SP-001 used a derivative of the previously tested persistent-replay boundary.

The only functional source change was the provider network location:

    -PROVIDER_BASE = "http://192.168.0.50:8091"
    +PROVIDER_BASE = "http://192.168.0.240:8091"

The source diff confirmed no other implementation changes.

## Provider Source Integrity

Provider source on the Windows working system:

`poc003_ed25519_provider_1h.py`

SHA-256:

`e7206aeb42a4b2f903cdf01d21604e2d19a7d0a2a79962e55982524de69c4d62`

Provider source on `Xer0trust2`:

SHA-256:

`e7206aeb42a4b2f903cdf01d21604e2d19a7d0a2a79962e55982524de69c4d62`

Result:

**MATCH**

The provider source transferred to the separate host was byte-identical to the selected working copy.

## Test-Key Integrity

Ed25519 private test key on the Windows working system:

SHA-256:

`cfdd77949cea7df748af6f0c45e9b2b2755a825ce178bc6e51d7fd4671bbc999`

Ed25519 private test key on `Xer0trust2`:

SHA-256:

`cfdd77949cea7df748af6f0c45e9b2b2755a825ce178bc6e51d7fd4671bbc999`

Result:

**MATCH**

The private key used by the separate provider was byte-identical to the selected laboratory test key.

The associated public verification key was:

SHA-256:

`2fd9c44a0579b985bc44722313725c8a6fd532b665b617b3e5082efb14c49f63`

The keypair is test-only material and has no production or external trust relationship.

## Boundary Source Integrity

Original persistent-replay boundary:

`poc004_pi_boundary_persistent_archer.py`

SHA-256:

`a1ca45bdae628b318d208120c51c25ba8281fdd22fecd6d5e87a993e51a61e26`

SP-001 derivative:

`sp001_separate_provider_boundary.py`

SHA-256:

`f35855d54933ee1f188576d9a8dc0eb9c30f8e7a5de821772f929df9cb801637`

The hash change reflects the provider-address modification documented above.

## Provider Startup

The separate provider started successfully on `Xer0trust2`.

Observed output:

    POC003_ED25519_OFFLINE_PROVIDER
    Listening on 0.0.0.0:8091
    Issue: POST /issue-offline
    Private key: /home/seth/nuvl-provider/poc002_ed25519_private.pem

Result:

**PASS**

## Provider Reachability

The Raspberry Pi contacted the provider over the network.

A request to:

`http://192.168.0.240:8091/`

returned an application response:

    {"error":"not_found"}

This established that the Raspberry Pi reached the provider application rather than failing at the transport layer.

Result:

**PASS**

## Provider Input Validation

An incomplete request to:

`POST /issue-offline`

returned:

    {"error":"ValueError('missing_device_id')"}

This confirmed that the remote provider received and parsed the request.

Result:

**PASS**

## Direct Remote Issuance

The Raspberry Pi then sent a complete issuance request directly to the separate provider.

Request fields included:

    device_id: esp32-field-01
    context: field_led_demo
    requested_action: accept
    nonce: sp001-test-001

The provider returned an artifact containing:

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

`a60543fa0024d3ffa192aa3e`

A provider signature was present.

Result:

**PASS**

This established that the physically separate provider could issue signed bounded authority to the Raspberry Pi over the network.

## Boundary Startup

The SP-001 boundary started successfully.

Observed output:

    POC004_PERSISTENT_REPLAY_PI_BOUNDARY
    Listening on 0.0.0.0:8089
    Provider: http://192.168.0.240:8091
    Public key: /home/seth/poc002_ed25519_public.pem
    Private key present on Pi: False
    Replay state: /home/seth/poc004_spent_state_archer.json
    Persistent replay entries loaded: 0

Result:

**PASS**

This confirmed that the Raspberry Pi boundary had the provider public verification key and did not contain the provider private signing key.

## Boundary Health

Boundary health returned:

    {
      "boundary":"poc004_persistent_replay_pi",
      "public_key_loaded":true,
      "replay_state_path":"/home/seth/poc004_spent_state_archer.json",
      "replay_state_persistent":true,
      "spent_count":0,
      "status":"ok"
    }

Result:

**PASS**

## Boundary-Mediated Issuance

The following issuance request was submitted through the NUVL boundary:

    device_id: esp32-field-01
    context: field_led_demo
    requested_action: accept
    nonce: sp001-boundary-001

The boundary returned:

    artifact_id: d7823d8bc39976c42c71ceaf
    decision: issued
    provider_verified: true
    reason: provider_signed_bounded_artifact

The returned package identified the provider artifact as Ed25519-authenticated.

Result:

**PASS**

This demonstrated that the boundary successfully obtained authority from the physically separate provider and verified the provider signature before returning the bounded artifact.

## Fresh Artifact for Spend Test

A fresh bounded-authority artifact was issued with:

    nonce: sp001-spend-001

Artifact ID:

`a4c7425a7c3275cb376f0818`

The issuance response reported:

    provider_verified: true

Result:

**PASS**

## Bounded Spend

The fresh provider-signed package was then submitted to the boundary spend path with the matching spend request.

The boundary returned:

    artifact_id: a4c7425a7c3275cb376f0818
    decision: accepted
    max_uses: 1
    provider_contacted_for_spend: false
    provider_verified: true
    reason: offline_artifact_admissible
    replay_state_persisted_before_accept: true
    uses_consumed: 1

Result:

**PASS**

The successful spend established that:

- the artifact was authenticated as provider-issued;
- the provider was not contacted for the spend itself;
- the existing provider-defined bounds were enforced;
- the single permitted use was consumed;
- replay state was persisted before acceptance.

## Operator / Request-Shape Errors

Two command-entry errors occurred during interactive testing.

### Incorrect Endpoint

An initial request was sent to:

`/validate`

The selected boundary implementation exposes:

- `/issue`
- `/spend`

It does not expose `/validate`.

The request returned:

    {"error":"not_found"}

This was an operator endpoint-selection error and did not exercise the authorization path.

### Incorrect Spend Payload Shape

An initial `/spend` request submitted the artifact package at the wrong JSON level.

The boundary returned:

    decision: denied
    provider_verified: false
    reason: package_not_object

Inspection of the boundary interface showed that `/spend` requires:

    {
      "package": {...},
      "spend_request": {...}
    }

The request was corrected and the subsequent spend passed.

This was an operator request-shape error before cryptographic validation and was not treated as a functional test failure.

## Result Summary

| Test Condition | Result |
|---|---|
| Provider source transferred byte-identically | PASS |
| Test private key transferred byte-identically | PASS |
| Separate provider started | PASS |
| Pi reached provider application | PASS |
| Provider parsed remote request | PASS |
| Direct remote Ed25519 issuance | PASS |
| SP-001 boundary started | PASS |
| Public verification key loaded | PASS |
| Provider private key absent from Pi | PASS |
| Boundary-mediated issuance | PASS |
| Provider signature verified | PASS |
| Fresh bounded artifact issued | PASS |
| Single bounded spend accepted | PASS |
| Provider not contacted during spend | PASS |
| Replay state persisted before acceptance | PASS |

## Overall Result

**SP-001: PASS**

SP-001 demonstrated that the existing Ed25519 provider-controlled bounded-authority path continued to function when the provider and its private signing key were placed on a physically separate host from the Raspberry Pi verification/enforcement boundary.

The successful authority path was:

    Separate provider host
            |
            | signed Ed25519 bounded authority
            v
    Raspberry Pi NUVL boundary
            |
            | provider_verified = true
            | bounds enforced
            v
    single admissible spend
            |
            v
    ACCEPT

## Supported Claim

SP-001 supports the following claim:

> A provider-controlled Ed25519 authority source can operate on a physically separate host from the NUVL verification/enforcement boundary while preserving provider-authenticated bounded authority.

## Current Limitations

The completed SP-001 run does not yet demonstrate:

- failure to obtain new authority when the separate provider is unavailable;
- restoration after separate-provider outage;
- rejection of an unauthorized substitute provider;
- malicious forwarder resistance;
- endpoint-side Ed25519 verification;
- resistance to arbitrary compromise of the Pi boundary;
- production key-management or infrastructure security.

Those conditions are outside the completed SP-001 result.
