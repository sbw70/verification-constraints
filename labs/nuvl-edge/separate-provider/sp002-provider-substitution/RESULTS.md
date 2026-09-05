# SP-002 Results — Unauthorized Provider Substitution

## Result

**PASS**

SP-002 demonstrated that occupying the expected provider network/service position was insufficient to originate authority accepted by the NUVL boundary.

An unauthorized substitute provider operated at the provider address and produced a structurally valid Ed25519-signed artifact using the expected provider representation. The Raspberry Pi boundary retained its existing legitimate public trust anchor.

The substitute artifact was rejected because its signature did not verify against that trust anchor.

After the legitimate provider was restored, verified issuance resumed through the same boundary.

---

## Test Sequence

### 1. Legitimate Provider Baseline

The legitimate provider was running at:

`http://192.168.0.240:8091`

A request was submitted through the Raspberry Pi boundary using:

- `device_id: esp32-field-01`
- `context: field_led_demo`
- `requested_action: accept`
- `nonce: sp002-rerun-legitimate`

Result:

- `artifact_id: 984c0e8fff05cf1f4692c38d`
- `decision: issued`
- `provider_verified: true`
- `reason: provider_signed_bounded_artifact`

The returned artifact identified:

- `alg: Ed25519`
- `provider_id: laptop-ed25519-provider-01`
- `decision: accepted`
- `max_uses: 1`
- `offline_allowed: true`

**Baseline result: PASS**

The legitimate provider's signed authority was accepted by the unchanged boundary.

---

### 2. Unauthorized Provider Substitution

The legitimate provider was stopped.

An unauthorized substitute provider was then started at the same provider service position.

The substitute preserved the expected provider-facing representation, including:

- `provider_id: laptop-ed25519-provider-01`
- `context: field_led_demo`
- `alg: Ed25519`
- `max_uses: 1`
- `offline_allowed: true`

The substitute used a different Ed25519 private signing key.

The Raspberry Pi boundary's legitimate public trust anchor was not replaced.

A new request was submitted through the boundary using:

- `device_id: esp32-field-01`
- `context: field_led_demo`
- `requested_action: accept`
- `nonce: sp002-rerun-unauthorized`

Result:

- `artifact_id: 0c422920aea5d0a91289a9d0`
- `decision: denied`
- `provider_verified: false`
- `reason: invalid_provider_signature`

**Unauthorized substitution result: PASS**

The substitute provider could produce an artifact with the expected structure and provider representation, but it could not produce authority accepted by the boundary because it did not possess the legitimate provider signing key.

---

### 3. Legitimate Provider Restoration

The unauthorized provider was stopped.

The legitimate provider was restarted without changing the Raspberry Pi boundary trust anchor.

A new request was submitted using:

- `device_id: esp32-field-01`
- `context: field_led_demo`
- `requested_action: accept`
- `nonce: sp002-rerun-restored`

Result:

- `artifact_id: a1dce6c1aa6dc9398eb4330b`
- `decision: issued`
- `provider_verified: true`
- `reason: provider_signed_bounded_artifact`

**Restoration result: PASS**

Verified authority issuance resumed after restoration of the legitimate provider.

---

## Observed Matrix

| Condition | Decision | Provider Verified | Reason | Result |
|---|---|---:|---|---|
| Legitimate provider | issued | true | provider_signed_bounded_artifact | PASS |
| Unauthorized substitute provider | denied | false | invalid_provider_signature | PASS |
| Legitimate provider restored | issued | true | provider_signed_bounded_artifact | PASS |

Overall:

`3/3 expected conditions observed — PASS`

---

## Boundary and Trust State

The test used the separate-provider boundary derivative:

`sp001_separate_provider_boundary.py`

SHA-256:

`f35855d54933ee1f188576d9a8dc0eb9c30f8e7a5de821772f929df9cb801637`

The boundary used the legitimate Ed25519 public trust anchor:

`poc002_ed25519_public.pem`

SHA-256:

`2fd9c44a0579b985bc44722313725c8a6fd532b665b617b3e5082efb14c49f63`

The trust anchor remained unchanged during provider substitution and restoration.

---

## Unauthorized Provider Artifacts

Unauthorized provider implementation:

`sp002_unauthorized_provider.py`

SHA-256:

`ad049085e8470b3fc17eb9089d3ade85db03bb05b21764f6d304a0c07d2f1703`

Unauthorized test signing key:

`sp002_unauthorized_private.pem`

SHA-256:

`dfb7da42fa074f8f68916f52780e310c3797e4da2caa674c5b0427324f0ad57d`

The unauthorized signing key is a disposable test key used only to reproduce the provider-substitution condition.

---

## Runtime Evidence

Clean rerun evidence:

`evidence/sp002_rerun_evidence.log`

Size:

`3527 bytes`

SHA-256:

`3420bcd631a0ffeae8d6086467df7c223d9d25c5fd3746b79dfad3ddb07bd148`

The evidence captures the legitimate baseline, unauthorized-provider rejection, and legitimate-provider restoration sequence.

---

## Demonstrated Property

SP-002 demonstrates that provider network position and provider representation are not sufficient to establish authority.

The enforcement boundary accepted authority from the legitimate provider whose signatures verified against the configured trust anchor and rejected authority generated by a substitute provider using a different signing key.

In this tested configuration:

`provider position != provider authority`

`provider identity representation != cryptographic authority`

Possession of the expected address, service interface, artifact format, and provider identifier did not allow the substitute provider to originate authority accepted by the boundary.

---

## Scope and Limitations

SP-002 specifically tests unauthorized provider substitution against an unchanged verification boundary and unchanged legitimate public trust anchor.

It does not independently demonstrate:

- protection of the Raspberry Pi trust-anchor file against privileged modification;
- resistance to arbitrary compromise of the verification/enforcement boundary itself;
- endpoint-local Ed25519 verification;
- rejection of every possible replay of a previously legitimate artifact;
- transport-layer authentication of the provider connection;
- protection against denial-of-service by an unauthorized provider occupying the expected network position.

Those properties require separate tests or controls.
