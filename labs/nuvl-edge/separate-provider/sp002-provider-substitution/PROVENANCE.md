# SP-002 Provenance — Unauthorized Provider Substitution

## Purpose

SP-002 evaluates whether control of the expected provider network and service position is sufficient to originate authority accepted by the NUVL verification boundary.

The test substitutes an unauthorized Ed25519 provider while preserving the expected provider-facing service, provider identifier, artifact structure, and request semantics. The verification boundary and its legitimate public trust anchor remain unchanged.

The resulting evidence isolates cryptographic signing authority from network position and provider representation.

---

## Test Architecture

SP-002 used three relevant trust components:

1. a separately hosted provider service;
2. a Raspberry Pi verification boundary;
3. an Ed25519 public trust anchor retained by the verification boundary.

The provider service was reachable by the boundary at:

`192.168.0.240:8091`

The verification boundary operated independently on the Raspberry Pi and identified the configured provider as:

`http://192.168.0.240:8091`

During the substitution phase, the service occupying that provider position changed. The boundary verification configuration did not.

---

## Provider Host

Provider services executed on a separate Linux host:

- Hostname: `Xer0trust2`
- Address: `192.168.0.240`
- Provider port: `8091`
- Python: `3.12.3`

The legitimate and unauthorized providers occupied the same host and service position sequentially.

Only one provider process occupied port `8091` during each test phase.

This arrangement allowed provider implementation and signing authority to change without changing the network destination used by the verification boundary.

---

## Verification Boundary

The Raspberry Pi boundary reported:

`poc004_persistent_replay_pi`

The SP-002 test used the separate-provider boundary derivative:

`sp001_separate_provider_boundary.py`

SHA-256:

`f35855d54933ee1f188576d9a8dc0eb9c30f8e7a5de821772f929df9cb801637`

The boundary was configured to contact:

`http://192.168.0.240:8091`

The same boundary implementation remained in service across the legitimate-provider baseline, unauthorized-provider substitution, and legitimate-provider restoration phases.

No SP-002 modification to the boundary verification logic was required.

---

## Legitimate Trust Anchor

Provider signatures were evaluated against the Ed25519 public key:

`poc002_ed25519_public.pem`

SHA-256:

`2fd9c44a0579b985bc44722313725c8a6fd532b665b617b3e5082efb14c49f63`

This public key represented the legitimate provider trust relationship at the verification boundary.

The trust anchor was not replaced during provider substitution.

The unauthorized provider key was not added to the boundary trust configuration.

This distinction is central to SP-002: the provider implementation and signing key changed while the verifier and configured trust relationship remained constant.

---

## Legitimate Provider

The legitimate provider implementation used for the baseline and restoration phases was:

`poc003_ed25519_provider_1h.py`

SHA-256:

`e7206aeb42a4b2f903cdf01d21604e2d19a7d0a2a79962e55982524de69c4d62`

The legitimate provider used the private Ed25519 signing key corresponding to the public trust anchor held by the Raspberry Pi boundary.

Relevant provider and artifact characteristics included:

- service port `8091`;
- provider identifier `laptop-ed25519-provider-01`;
- context `field_led_demo`;
- Ed25519 signatures;
- bounded artifact issuance;
- `max_uses: 1`;
- `offline_allowed: true`.

A legitimate provider artifact therefore possessed both the expected representation and a signature verifiable under the configured trust anchor.

---

## Unauthorized Substitute Provider

The substitution condition used:

`sp002_unauthorized_provider.py`

SHA-256:

`ad049085e8470b3fc17eb9089d3ade85db03bb05b21764f6d304a0c07d2f1703`

The substitute provider intentionally reproduced the provider-facing characteristics required to make network position and representation insufficient discriminators.

Relevant configuration included:

- host binding `0.0.0.0`;
- service port `8091`;
- provider identifier `laptop-ed25519-provider-01`;
- expected context `field_led_demo`;
- Ed25519 artifact signatures;
- `max_uses: 1`;
- `offline_allowed: true`.

The substitute could therefore occupy the expected provider service position and generate artifacts conforming to the expected provider representation.

Its signing authority was intentionally different.

---

## Unauthorized Signing Key

The substitute provider signed artifacts using:

`sp002_unauthorized_private.pem`

SHA-256:

`dfb7da42fa074f8f68916f52780e310c3797e4da2caa674c5b0427324f0ad57d`

This key is a disposable laboratory key created for the provider-substitution condition.

It does not correspond to the legitimate public trust anchor configured at the verification boundary.

The distinction between the legitimate and substitute providers therefore did not depend on provider address, port, provider identifier, artifact format, or claimed algorithm. It depended on whether the resulting signature established the configured cryptographic trust relationship.

---

## Execution Record

SP-002 was executed as a three-phase sequence.

### Phase 1 — Legitimate Provider Baseline

The legitimate provider occupied:

`192.168.0.240:8091`

The boundary processed a request containing:

- `device_id: esp32-field-01`
- `context: field_led_demo`
- `requested_action: accept`
- `nonce: sp002-rerun-legitimate`

Observed result:

- `artifact_id: 984c0e8fff05cf1f4692c38d`
- `decision: issued`
- `provider_verified: true`
- `reason: provider_signed_bounded_artifact`

The baseline established successful issuance through the configured provider trust relationship.

### Phase 2 — Unauthorized Provider Substitution

The legitimate provider was stopped and replaced by the unauthorized provider at the same provider service position.

The verification boundary and legitimate public trust anchor remained unchanged.

The boundary processed a request containing:

- `device_id: esp32-field-01`
- `context: field_led_demo`
- `requested_action: accept`
- `nonce: sp002-rerun-unauthorized`

The substitute returned an Ed25519-signed artifact using its unauthorized signing key.

Observed boundary result:

- `artifact_id: 0c422920aea5d0a91289a9d0`
- `decision: denied`
- `provider_verified: false`
- `reason: invalid_provider_signature`

The artifact was not admitted as provider-authorized authority.

### Phase 3 — Legitimate Provider Restoration

The unauthorized provider was stopped and the legitimate provider restored at the same provider service position.

No replacement of the legitimate public trust anchor was performed.

The boundary processed a request containing:

- `device_id: esp32-field-01`
- `context: field_led_demo`
- `requested_action: accept`
- `nonce: sp002-rerun-restored`

Observed result:

- `artifact_id: a1dce6c1aa6dc9398eb4330b`
- `decision: issued`
- `provider_verified: true`
- `reason: provider_signed_bounded_artifact`

Verified issuance resumed when the legitimate signing authority returned.

---

## Canonical Runtime Evidence

The publication-grade execution record is:

`evidence/sp002_rerun_evidence.log`

File size:

`3527 bytes`

SHA-256:

`3420bcd631a0ffeae8d6086467df7c223d9d25c5fd3746b79dfad3ddb07bd148`

The recording contains the legitimate baseline, unauthorized substitution rejection, and legitimate restoration sequence.

The terminal recording was closed immediately after completion of the three-phase sequence and hashed after capture terminated.

This file is the canonical SP-002 runtime evidence.

---

## Superseded Evidence Record

An earlier terminal recording named:

`sp002_substitution_evidence.log`

was generated during the original SP-002 execution.

That recording remained active during subsequent evidence-recovery activity. Commands used to inspect the recording were themselves captured into the same recording, producing unrelated content and recursive reproductions of portions of the file.

The original recording was therefore unsuitable as a bounded publication artifact.

It is superseded for publication purposes by `sp002_rerun_evidence.log`.

No SP-002 result is derived from reconstructed or fabricated terminal output.

---

## Relationship to Prior Provider-Authenticity Testing

SP-002 exercises a different trust failure from the earlier wrong-trust-anchor condition.

The prior trust-anchor substitution condition retained the legitimate provider while replacing the verification key presented to the boundary.

SP-002 performs the inverse:

- the legitimate verification boundary remains in place;
- the legitimate public trust anchor remains in place;
- the provider occupying the expected service position is replaced;
- the substitute signs with an unauthorized private key.

The two conditions independently exercise opposite sides of the provider/verifier trust relationship.

SP-002 therefore isolates provider substitution from verifier trust-anchor substitution.

---

## Evidence Interpretation

The observed result establishes that, within the tested architecture, successful provider impersonation at the network and representation layers did not establish provider authority.

The substitute possessed:

- the expected provider host position;
- the expected service port;
- the expected provider identifier;
- the expected context;
- the expected artifact structure;
- the expected Ed25519 algorithm declaration.

It did not possess the private signing key corresponding to the boundary's configured public trust anchor.

The boundary consequently returned:

`decision: denied`

`provider_verified: false`

`reason: invalid_provider_signature`

Restoration of the legitimate provider restored verified issuance without changing the trust anchor.

The evidence therefore supports the bounded claim that, in the tested configuration, provider position and representation were insufficient to originate accepted authority without the corresponding legitimate signing authority.

---

## Artifact Provenance

| Artifact | Role | SHA-256 |
|---|---|---|
| `sp001_separate_provider_boundary.py` | Verification boundary | `f35855d54933ee1f188576d9a8dc0eb9c30f8e7a5de821772f929df9cb801637` |
| `poc002_ed25519_public.pem` | Legitimate boundary trust anchor | `2fd9c44a0579b985bc44722313725c8a6fd532b665b617b3e5082efb14c49f63` |
| `poc003_ed25519_provider_1h.py` | Legitimate provider | `e7206aeb42a4b2f903cdf01d21604e2d19a7d0a2a79962e55982524de69c4d62` |
| `sp002_unauthorized_provider.py` | Unauthorized substitute provider | `ad049085e8470b3fc17eb9089d3ade85db03bb05b21764f6d304a0c07d2f1703` |
| `sp002_unauthorized_private.pem` | Unauthorized test signing key | `dfb7da42fa074f8f68916f52780e310c3797e4da2caa674c5b0427324f0ad57d` |
| `sp002_rerun_evidence.log` | Canonical runtime evidence | `3420bcd631a0ffeae8d6086467df7c223d9d25c5fd3746b79dfad3ddb07bd148` |

---

## Provenance Boundary

SP-002 establishes provenance for the tested provider-substitution condition and its associated artifacts.

It does not establish protection against privileged modification of the Raspberry Pi trust-anchor file, arbitrary compromise of the verification boundary, or endpoint-local Ed25519 verification.

Those properties are outside the SP-002 test boundary and require independent evidence.
