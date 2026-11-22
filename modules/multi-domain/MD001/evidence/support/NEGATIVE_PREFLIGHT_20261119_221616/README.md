# MD001 — Negative Preflight Evidence

## Overview

This directory preserves the negative preflight evidence collected before the MD001 scored experiments.

The preflight evaluates whether Domain B rejects a previously valid signed assertion after a field covered by the signature is modified at the Domain B ingress component.

The original signature is retained during the modification.

**Evidence directory:** `NEGATIVE_PREFLIGHT_20261119_221616`  
**Recorded execution:** November 20, 2026 UTC  
**Classification:** Non-scored negative preflight  
**Recorded outcome:** PASS — modified assertion rejected with `invalid_signature`

The negative preflight establishes that the configured verification path rejects the specific signed-field modification tested.

It is supporting operational evidence, not the scored N01 result.

## 1. Preflight Objective

The preflight evaluates four conditions:

1. A previously valid signed assertion reaches Domain B ingress without modification.
2. The ingress component changes a field covered by the original signature.
3. The modified assertion is forwarded to the Domain B verifier without replacing the signature.
4. The verifier rejects the modified assertion because the received content does not match the original signature.

The purpose is to confirm the negative verification path before conducting the scored mutation experiment.

## 2. Recorded Architecture

```text
Domain A — Original Signed Assertion
          |
          | Previously valid artifact
          v
Mechanical Relay
          |
          | Original bytes preserved
          v
Domain B — Ingress
          |
          | Modify event.outcome
          | SUCCESS -> FAILURE
          | Preserve original signature
          v
Domain B — Verifier
          |
          | Signature verification
          v
DENY — invalid_signature
```

The relay transports the assertion.

The Domain B ingress component introduces the modification.

The verifier evaluates the resulting artifact using previously provisioned verification material.

The modification does not involve issuing a replacement signature.

## 3. Original and Modified Artifacts

### Original Artifact

The negative preflight uses the original signed assertion from the positive preflight.

The original artifact has SHA-256:

```text
00181b7b3e917a1280bdc22ac504f2adbba089ce2b5be6a454f6f895c880a177
```

The ingress transport record identifies this digest as the artifact received before modification.

The original assertion is preserved in the positive preflight evidence directory:

```text
../PREFLIGHT_EXPORT_20261119_213249/
```

### Recorded Mutation

The ingress mutation record identifies:

| Property | Recorded value |
|---|---|
| Modified field | `event.outcome` |
| Original value | `SUCCESS` |
| Modified value | `FAILURE` |
| Signature replaced | `false` |
| Ingress mode | `tamper` |

The modified artifact has SHA-256:

```text
00f0d2507757a66c95c0c9e708852dc80e57222e36b4538369fae25503ae37d2
```

The modified artifact differs from the original assertion.

Because the original signature is retained, the modified content no longer corresponds to the signed content.

The test does not involve compromising or replacing the signing key.

## 4. Evidence Directory

The negative preflight evidence is organized by transport observation, mutation, and verifier response.

### Domain B Ingress

`SYS_NEGATIVE_PREFLIGHT_ingress_20261120T030908Z_99239/`

This directory contains `process.json` and six request-specific records identified by:

```text
86aadc3fe56249e8b93810c8dfc1801b
```

| File suffix | Purpose |
|---|---|
| `-ingress.bin` | Original assertion received at Domain B ingress |
| `-egress.bin` | Modified assertion forwarded to the verifier |
| `-mutation.json` | Recorded signed-field modification |
| `-transport.json` | Request transport metadata and ingress mode |
| `-downstream-response.bin` | Verifier response bytes |
| `-decision-or-response.json` | Parsed downstream verification decision |

The ingress transport record identifies:

| Property | Recorded value |
|---|---|
| HTTP method | `POST` |
| Path | `/verify` |
| Content length | 332 bytes |
| Destination | `PROVIDER_B` |
| Mode | `tamper` |

The ingress and egress binary records preserve the artifact before and after modification.

### Domain B Verifier

`SYS_PREFLIGHT_verifier_20261119T025903Z_96917/`

This directory contains:

- `process.json`
- `trust-provisioned.json`
- Request-specific ingress bytes
- Request-specific transport metadata
- Request-specific verification decisions

Two request identifiers are preserved.

| Request identifier | Recorded purpose |
|---|---|
| `c9c18a4f79d34f18af2d14258214ca08` | Original valid-artifact verification |
| `db4bf244e53f4bdcb8e2ada2f1cc048f` | Modified-artifact verification |

The first record provides the previously accepted baseline.

The second records rejection of the modified assertion.

Both responses identify the same verifier process instance:

```text
d4382a4f00024506948faa196a6ccf2e
```

This permits comparison of the positive and negative verification decisions within the recorded verifier instance.

### Relay Observation Evidence

| File | Purpose |
|---|---|
| `PI_INGRESS_ARTIFACT.bin` | Artifact observed at relay ingress |
| `PI_EGRESS_ARTIFACT.bin` | Artifact observed at relay egress |

These files preserve the relay-side transport observations.

### Network Evidence

| File | Purpose |
|---|---|
| `MD001_NEGATIVE_PREFLIGHT_20261120T030825Z.pcap` | Packet capture |
| `TCP_CONVERSATIONS.txt` | Extracted TCP conversation information |
| `TCP_PACKET_ANALYSIS.txt` | Packet-analysis record |
| `TSHARK_VERSION.txt` | Packet-analysis tool version |
| `stream_0.bin`, `stream_1.bin` | Extracted binary TCP streams |
| `stream_0.txt`, `stream_1.txt` | Text representations of extracted streams |

These records provide supporting network evidence for the negative preflight.

## 5. Recorded Results

### Original Artifact Identity

The Domain B ingress transport record identifies the original artifact SHA-256:

```text
00181b7b3e917a1280bdc22ac504f2adbba089ce2b5be6a454f6f895c880a177
```

This matches the artifact identity recorded during the positive preflight.

### Modified Artifact Identity

The ingress mutation record identifies:

```text
00f0d2507757a66c95c0c9e708852dc80e57222e36b4538369fae25503ae37d2
```

The verifier's rejection response identifies the same modified-artifact digest.

This establishes the recorded relationship between the ingress modification and the artifact evaluated by the verifier.

### Verification Decision

The verifier's preserved negative response records:

```json
{
  "accepted": false,
  "reason": "invalid_signature",
  "signature_checks": 1
}
```

The response identifies HTTP status:

```text
422
```

The earlier positive preflight response recorded:

```json
{
  "accepted": true,
  "reason": "accepted",
  "signature_checks": 1
}
```

The two decisions establish that the recorded verifier accepted the original assertion and rejected the modified assertion.

### Preflight Outcome

The preserved evidence establishes:

1. The original valid assertion reached Domain B ingress.
2. The ingress component recorded a modification to `event.outcome`.
3. The original signature was retained.
4. The modified artifact was submitted for verification.
5. The verifier performed a signature check.
6. The verifier rejected the modified artifact with `invalid_signature`.

**Negative preflight result: PASS for the recorded signed-field modification and rejection conditions.**

## 6. Independent Evidence Review

The historical negative preflight can be inspected without starting the laboratory services.

### Step 1 — Establish the Original Assertion

Inspect the positive preflight directory:

```text
../PREFLIGHT_EXPORT_20261119_213249/
```

Review the original `artifact.json` and `signed-bytes.bin`.

Confirm the original SHA-256 digest:

```text
00181b7b3e917a1280bdc22ac504f2adbba089ce2b5be6a454f6f895c880a177
```

### Step 2 — Review the Ingress Mutation

Open:

```text
SYS_NEGATIVE_PREFLIGHT_ingress_20261120T030908Z_99239/
```

Inspect the request-specific:

```text
-ingress.bin
-egress.bin
-mutation.json
-transport.json
```

Confirm the recorded modification:

```text
event.outcome:
SUCCESS -> FAILURE
```

Confirm:

```text
signature_replaced = false
```

### Step 3 — Compare Artifact Identities

Compare the original and modified artifact bytes.

The expected modified SHA-256 digest is:

```text
00f0d2507757a66c95c0c9e708852dc80e57222e36b4538369fae25503ae37d2
```

Confirm that the verifier received the modified artifact.

### Step 4 — Review the Verification Decision

Open:

```text
SYS_PREFLIGHT_verifier_20261119T025903Z_96917/
```

Inspect the request-specific decision record identified by:

```text
db4bf244e53f4bdcb8e2ada2f1cc048f
```

Confirm:

```text
accepted = false
reason = invalid_signature
signature_checks = 1
```

### Step 5 — Compare Against the Positive Baseline

Inspect the earlier decision record identified by:

```text
c9c18a4f79d34f18af2d14258214ca08
```

Confirm that the original assertion was accepted.

This establishes the recorded positive and negative behavior of the verifier.

### Step 6 — Review Network Evidence

Inspect:

```text
MD001_NEGATIVE_PREFLIGHT_20261120T030825Z.pcap
TCP_CONVERSATIONS.txt
TCP_PACKET_ANALYSIS.txt
```

Use the packet capture and extracted streams to cross-check the recorded transport observations.

These steps support independent inspection of the historical preflight.

A new execution requires the applicable runtime, configuration, dependencies, and trust material.

## 7. Relationship to Scored Experiments

The negative preflight preceded the scored N01 experiment.

| Experiment | Purpose |
|---|---|
| Positive preflight | Establish valid-artifact transport and acceptance |
| Negative preflight | Confirm rejection after a signed-field modification |
| B01 | Scored valid-artifact verification |
| N01 | Scored signed-field mutation and rejection |
| B02 | Scored verification with the originating producer unavailable |

The negative preflight and N01 exercise the same general failure condition but preserve distinct artifacts and evidence records.

The negative preflight uses the original positive-preflight assertion.

N01 uses the original B01 assertion.

Their artifact SHA-256 identities differ.

The negative preflight must not be counted as an additional scored N01 execution.

## 8. Scope and Limitations

The negative preflight demonstrates that the recorded verifier rejected an assertion after the specified signed-field modification.

The evidence supports:

- Receipt of the original signed assertion at Domain B ingress.
- Modification of `event.outcome` from `SUCCESS` to `FAILURE`.
- Retention of the original signature.
- Receipt of the modified artifact by the verifier.
- Rejection with `invalid_signature`.

It does not establish:

- Rejection of every possible artifact mutation.
- Resistance to compromise of the original signing key.
- Prevention of replay using an unchanged valid assertion.
- Durable authorization consumption.
- Execution-state persistence.
- Physical execution enforcement.
- Security against arbitrary verifier or trust-store compromise.
- Successful completion of the later scored N01 experiment.

The negative preflight is supporting operational evidence.

The separately preserved N01 scored-run directory provides the primary evidence for the MD001 signed-field mutation experiment.
