# MD001 N01 — Modified Assertion Rejection

## Overview

N01 is the negative-control scored run for MD001, the Multi-Domain Stateless Verification experiment.

The run examines whether Domain B rejects a previously valid, provider-signed operation-completion assertion after a signed field is modified during transport, without replacement of the original signature.

**Scored evidence directory:** `N01_SCORED_20261119_224654`  
**Recorded execution:** November 20, 2026 UTC  
**Recorded outcome:** PASS — modified artifact rejected with `invalid_signature`

N01 uses the valid assertion established in B01. The negative condition is introduced at Domain B ingress, after the artifact has traversed the mechanical relay.

## 1. Test Objective

The experiment evaluates four observable properties:

1. The original B01 assertion remains unchanged through the relay.
2. Domain B ingress modifies a field within the signed assertion while retaining its original signature.
3. The verifier receives the modified artifact rather than the original.
4. The verifier rejects the modified artifact because its signature is no longer valid for the received content.

The test distinguishes successful transport of the original assertion from cryptographic acceptance of a modified assertion.

## 2. Recorded Architecture

```text
Domain A — Original Signed Assertion
          |
          | Resubmitted without modification
          v
Mechanical Relay
30.30.30.30:18081
          |
          | Original artifact preserved
          v
Domain B — Ingress
40.40.40.40:18443
          |
          | Modify event.outcome
          | SUCCESS -> FAILURE
          | Preserve original signature
          v
Domain B — Verifier
          |
          v
Signature verification
          |
          v
DENY — invalid_signature
```

The recorded ingress transport mode is `tamper`.

The relay retains its forwarding role. The mutation occurs at the Domain B ingress component, not at the producer or relay.

The ingress record identifies an HTTP `POST` to `/verify` with the destination header `X-MH-Destination: PROVIDER_B`.

## 3. Original and Modified Artifacts

### Original Artifact

The N01 sender resubmits the valid assertion from B01.

The preserved original artifact has SHA-256:

```text
61f113905f6c89e382f2bbccc081fb871ff08f4304a61d970197a85d3f8bcc5a
```

The original artifact is recorded at:

- B01 producer output.
- N01 relay ingress.
- N01 relay egress.
- N01 Domain B ingress.

These observations establish that the original signed artifact reached the designated mutation point without a recorded byte change.

### Mutation

The ingress mutation record identifies the following operation:

| Property | Recorded value |
|---|---|
| Modified field | `event.outcome` |
| Original value | `SUCCESS` |
| Modified value | `FAILURE` |
| Signature replaced | `false` |
| Ingress mode | `tamper` |

The modified artifact has SHA-256:

```text
bae4f84d46d91e3b805890d8e683d9800798c4927343f4d266670824a9b21594
```

The mutation changes the content covered by the original signature. The original signature is retained, so the modified artifact no longer corresponds to the signed content.

The test does not involve generating a replacement valid signature.

## 4. Evidence Directory

The N01 evidence is organized by observation point and artifact identity.

### Sender — `N01_sender_20261120T034533Z_18525/`

| File | Purpose |
|---|---|
| `artifact.json` | Original signed assertion submitted for the negative case |
| `signed-bytes.bin` | Original signed bytes |
| `submission.json` | Resubmission endpoint and original artifact identity |
| `response.bin` | Returned response bytes |
| `result.json` | Parsed verification result |

The sender's `submission.json` identifies the `resubmit` command and the relay endpoint `30.30.30.30:18081`.

### Relay — `B01_relay_20261120T033236Z_5344/`

| File | Purpose |
|---|---|
| `effective-hub-config.json` | Recorded relay configuration |
| `process.json` | Relay process identity |
| `relay.jsonl` | Relay event log |

The relay evidence retains the original process-directory identifier. Its name does not imply that the N01 submission was part of the B01 scored case.

### Domain B Ingress — `N01_ingress_20261120T034412Z_99441/`

The ingress directory contains `process.json` and six request-specific files identified by the prefix:

`bbc4944fa9294ca2bb2ff346c1967d26`

| File suffix | Purpose |
|---|---|
| `-ingress.bin` | Original artifact received by Domain B ingress |
| `-egress.bin` | Modified artifact forwarded to the verifier |
| `-mutation.json` | Recorded field modification and signature-retention status |
| `-transport.json` | Request metadata and ingress mode |
| `-downstream-response.bin` | Response bytes received from the verifier |
| `-decision-or-response.json` | Parsed downstream verification response |

The ingress and egress binary records are the principal evidence of the content change at this boundary.

### Domain B Verifier — `B01_verifier_20261120T033407Z_99396/`

The verifier directory contains `process.json`, `trust-provisioned.json`, and request-specific verification records.

Two request identifiers are preserved:

- `066c3bc0df2b4aec91e7960fd38ff442` — earlier valid-artifact verification record.
- `4fe2a5c84f034b1db88144797866df8d` — modified-artifact verification record.

The earlier record provides a comparison with the previously accepted artifact.

The modified-artifact record preserves the received bytes, transport metadata, and rejection decision.

### Transport and Comparison Evidence

| File | Purpose |
|---|---|
| `ARTIFACT_HASH_COMPARISON.txt` | SHA-256 comparison across original and modified artifact observations |
| `MD001_N01_20261120T034149Z.pcap` | Packet capture |
| `PI_INGRESS_ARTIFACT.bin` | Artifact observed at relay ingress |
| `PI_EGRESS_ARTIFACT.bin` | Artifact observed at relay egress |
| `TCP_CONVERSATIONS.txt` | Extracted TCP conversation information |
| `TCP_PACKET_ANALYSIS.txt` | Packet-analysis record |
| `TSHARK_VERSION.txt` | Packet-analysis tool version |
| `stream_0.bin`, `stream_1.bin` | Extracted binary TCP streams |
| `stream_0.txt`, `stream_1.txt` | Text representations of extracted streams |

## 5. Recorded Results

### Artifact Identity Across Boundaries

`ARTIFACT_HASH_COMPARISON.txt` records the following:

| Observation point | Artifact identity |
|---|---|
| Original B01 producer output | Original |
| N01 relay ingress | Original |
| N01 relay egress | Original |
| N01 Domain B ingress | Original |
| N01 Domain B ingress egress | Modified |
| N01 verifier ingress | Modified |

The comparison establishes that the recorded modification occurred between Domain B ingress reception and forwarding to the verifier.

The modified artifact received by the verifier matches the modified artifact emitted by Domain B ingress.

### Verification Decision

The verifier's preserved response records:

```json
{
  "accepted": false,
  "reason": "invalid_signature",
  "signature_checks": 1
}
```

The response identifies the modified artifact SHA-256:

```text
bae4f84d46d91e3b805890d8e683d9800798c4927343f4d266670824a9b21594
```

The sender's `result.json` records:

| Field | Value |
|---|---|
| HTTP status | `422` |
| Accepted | `false` |
| Reason | `invalid_signature` |
| Signature checks | `1` |

The recorded rejection is attributable to signature verification of the modified artifact.

**N01 result: PASS for the recorded signed-field mutation and invalid-signature rejection case.**

## 6. Independent Evidence Review

A reviewer can inspect the historical negative-control result without starting the laboratory services.

1. Inspect the sender's `artifact.json`, `signed-bytes.bin`, and `submission.json` to establish the original signed artifact.
2. Compare the original artifact against `PI_INGRESS_ARTIFACT.bin`, `PI_EGRESS_ARTIFACT.bin`, and the Domain B ingress `-ingress.bin` record.
3. Inspect `-mutation.json` to identify the modified field, original value, replacement value, and signature-retention status.
4. Compare the ingress `-egress.bin` record with the verifier's modified-artifact `-ingress.bin` record.
5. Inspect the verifier's `-decision-or-response.json` for the `invalid_signature` decision.
6. Cross-check the recorded artifact identities using `ARTIFACT_HASH_COMPARISON.txt` and the packet-capture evidence.

The published runtime and trust configuration are required for an independent cryptographic re-evaluation or a new execution of the negative case.

Historical evidence inspection and fresh test execution are separate activities.

## 7. Scope and Limitations

N01 demonstrates that the recorded verifier rejected a modified signed assertion after a content change at Domain B ingress.

The evidence supports the following bounded conclusions:

- The original assertion was preserved through the recorded relay observations.
- The mutation occurred at the designated ingress component.
- The modified content reached the verifier.
- The verifier performed a signature check and rejected the modified artifact.
- The original signature was not replaced during the recorded mutation.

N01 does not establish:

- Detection of every possible artifact mutation or encoding variation.
- Resistance to compromise of the original signing key.
- Prevention of replay using an unchanged, valid assertion.
- Durable authorization consumption or execution-state enforcement.
- Detection of a compromised verifier or modified trust configuration.
- Physical execution enforcement.
- General security against arbitrary intermediary compromise.

N01 is therefore evidence of cryptographic rejection for the specific signed-field modification tested, rather than a general claim of protection against all cross-domain attacks.

The valid-artifact baseline is documented in B01. The producer-unavailable verification case is documented separately in B02.
