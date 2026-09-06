# SP-002 Results — Unauthorized Provider Substitution

## Result

**PASS**

SP-002 evaluated whether occupying the expected provider network and service position was sufficient to originate authority accepted by the NUVL boundary.

An unauthorized substitute provider reproduced the expected provider-facing representation and produced a structurally valid Ed25519-signed artifact using an unrelated signing key.

The Raspberry Pi boundary retained the legitimate provider public trust anchor throughout the substitution.

The substitute artifact was rejected because its signature did not verify against that trust anchor.

After restoration of the legitimate provider, verified issuance resumed through the same boundary.

## Test Sequence

### 1. Legitimate Provider Baseline

The legitimate provider was operating at:

    http://192.168.0.240:8091

A request was submitted through the Raspberry Pi boundary using:

    device_id: esp32-field-01
    context: field_led_demo
    requested_action: accept
    nonce: sp002-rerun-legitimate

Observed:

    artifact_id: 984c0e8fff05cf1f4692c38d
    decision: issued
    provider_verified: true
    reason: provider_signed_bounded_artifact

The returned artifact identified:

    alg: Ed25519
    provider_id: laptop-ed25519-provider-01
    decision: accepted
    max_uses: 1
    offline_allowed: true

**Result: PASS**

The legitimate provider's signed authority was accepted by the unchanged boundary.

### 2. Unauthorized Provider Substitution

The legitimate provider was stopped.

An unauthorized substitute provider was then started at the expected provider service position.

The substitute reproduced relevant provider-facing characteristics, including:

    provider_id: laptop-ed25519-provider-01
    context: field_led_demo
    alg: Ed25519
    max_uses: 1
    offline_allowed: true

The substitute used an unrelated Ed25519 private signing key.

The Raspberry Pi boundary trust anchor was not changed.

A new request was submitted using:

    device_id: esp32-field-01
    context: field_led_demo
    requested_action: accept
    nonce: sp002-rerun-unauthorized

Observed:

    artifact_id: 0c422920aea5d0a91289a9d0
    decision: denied
    provider_verified: false
    reason: invalid_provider_signature

**Result: PASS**

The substitute produced an artifact with the expected representation but did not produce authority accepted by the boundary.

### 3. Legitimate Provider Restoration

The unauthorized provider was stopped.

The legitimate provider was restarted without changing the Raspberry Pi boundary trust anchor.

A new request was submitted using:

    device_id: esp32-field-01
    context: field_led_demo
    requested_action: accept
    nonce: sp002-rerun-restored

Observed:

    artifact_id: a1dce6c1aa6dc9398eb4330b
    decision: issued
    provider_verified: true
    reason: provider_signed_bounded_artifact

**Result: PASS**

Verified provider issuance resumed after restoration of the legitimate provider.

## Observed Matrix

| Condition | Decision | Provider Verified | Reason | Result |
|---|---|---:|---|---|
| Legitimate provider | issued | true | `provider_signed_bounded_artifact` | PASS |
| Unauthorized substitute provider | denied | false | `invalid_provider_signature` | PASS |
| Legitimate provider restored | issued | true | `provider_signed_bounded_artifact` | PASS |

**Overall Result: PASS — 3/3 expected conditions observed.**

## Trust-State Control

The same Raspberry Pi verification boundary and legitimate Ed25519 public trust anchor remained in place during:

1. legitimate-provider baseline;
2. unauthorized-provider substitution;
3. legitimate-provider restoration.

The trust anchor was not replaced as part of the substitution condition.

This distinguishes SP-002 from a trust-anchor substitution test.

## Runtime Evidence

The retained runtime record is:

    evidence/sp002_rerun_evidence.log

The transcript captures the complete three-phase sequence:

1. legitimate provider accepted;
2. unauthorized substitute rejected;
3. legitimate provider restored and accepted.

Artifact identity and integrity information for the evidence file are maintained in `PROVENANCE.md` and `SHA256SUMS.txt`.

## Demonstrated Property

SP-002 demonstrated that, within the tested configuration, provider network position and provider-facing representation were not sufficient to obtain accepted provider authority.

The legitimate provider produced authority that verified against the configured trust anchor.

The unauthorized substitute reproduced the expected service position and artifact representation but signed with an unrelated key. The boundary rejected that authority with:

    provider_verified: false
    reason: invalid_provider_signature

The tested distinction was:

    provider position != provider authority

    provider representation != cryptographic authority

Possession of the expected address, service interface, artifact format, and provider identifier did not substitute for possession of signing material corresponding to the boundary's configured trust anchor.

## Supported Claim

SP-002 supports the bounded claim that, within the tested configuration:

- authority from the legitimate provider was accepted;
- a substitute provider occupying the expected provider position was rejected when its signature did not verify against the unchanged legitimate trust anchor;
- restoration of the legitimate provider restored verified issuance without changing the boundary trust anchor.

## Claim Boundary

SP-002 does not establish:

- protection of the Raspberry Pi trust-anchor file against privileged modification;
- security after arbitrary privileged compromise of the verification/enforcement boundary;
- endpoint-local Ed25519 verification;
- rejection of every possible replay of previously legitimate authority;
- transport-layer authentication of the provider connection;
- resistance to denial-of-service at the provider network position;
- resistance to every possible malicious intermediary behavior.

Those properties require separate evidence.
