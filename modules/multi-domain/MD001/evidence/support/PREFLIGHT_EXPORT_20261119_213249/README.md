# MD001 — Positive Preflight Evidence

## Overview

This directory preserves the positive preflight evidence collected before the MD001 scored experiments.

The preflight evaluated whether a signed operation-completion assertion could traverse the configured relay and reach the Domain B verifier without modification.

The verifier was expected to accept the valid assertion using previously provisioned verification material.

**Evidence directory:** `PREFLIGHT_EXPORT_20261119_213249`  
**Recorded execution:** November 20, 2026 UTC  
**Classification:** Non-scored preflight  
**Recorded outcome:** PASS — artifact preserved and signature accepted

This evidence establishes a working transport and verification baseline before the scored experiments.

It is not a substitute for the independently recorded B01, N01, or B02 results.

## 1. Preflight Objective

The preflight evaluated four conditions:

1. The producer could generate a signed assertion describing a completed local operation.
2. The relay could forward the assertion toward Domain B.
3. The artifact remained byte-identical across the recorded transport observations.
4. The Domain B verifier could validate the signature and return an accepted response.

The purpose was to confirm the basic operational path before conducting the scored experiments.

## 2. Recorded Architecture

```text
Domain A — Producer
        |
        | Signed assertion
        v
Mechanical Relay
        |
        | Original bytes preserved
        v
Domain B — Ingress
        |
        | Forwarded assertion
        v
Domain B — Verifier
        |
        | Signature verification
        v
ACCEPT
```

The relay functions as a transport intermediary.

The verifier independently evaluates the signed assertion against its provisioned trust configuration.

The preflight does not grant the relay authority to originate, modify, or approve the assertion.

## 3. Recorded Operation

The producer's operation record identifies:

| Property | Recorded value |
|---|---|
| Event | `LOCAL_SORT_V1` |
| Boundary | `sort_completed` |
| Input | `[9,1,4,2]` |
| Observed output | `[1,2,4,9]` |

The producer generated a signed assertion associated with this recorded software operation.

The resulting artifact was submitted through the configured verification path.

The preflight evaluates assertion transport and verification. It does not independently establish the correctness of the underlying operation.

## 4. Evidence Directory

### Producer Evidence

`SYS_NON_SCORED_PREFLIGHT_20261120T022358Z_18216/`

| File | Purpose |
|---|---|
| `operation.json` | Recorded local operation |
| `artifact.json` | Original signed assertion |
| `signed-bytes.bin` | Bytes used for signing |
| `submission.json` | Submission metadata |
| `response.bin` | Returned response bytes |
| `result.json` | Parsed verification response |

These records establish the assertion submitted during the preflight and the response returned to the producer.

### Verifier Evidence

`SYS_PREFLIGHT_verifier_20261119T025903Z_96917/`

This directory contains:

- `process.json`
- `trust-provisioned.json`
- Request-specific ingress bytes
- Request-specific transport metadata
- Request-specific verification decision

The relevant request identifier is:

```text
c9c18a4f79d34f18af2d14258214ca08
```

The verifier evidence identifies the artifact received and the decision returned.

### Relay Observation Evidence

| File | Purpose |
|---|---|
| `PI_INGRESS_ARTIFACT.bin` | Artifact observed at relay ingress |
| `PI_EGRESS_ARTIFACT.bin` | Artifact observed at relay egress |
| `PREFLIGHT_BYTE_COMPARISON.json` | Cross-boundary byte comparison |

These files provide the principal evidence of artifact preservation.

### Network Evidence

| File | Purpose |
|---|---|
| `MD001_PREFLIGHT_20261120T021945Z.pcap` | Packet capture |
| `TCP_CONVERSATIONS.txt` | Extracted TCP conversation information |
| `TCP_PACKET_ANALYSIS.txt` | Packet-analysis record |
| `TSHARK_VERSION.txt` | Packet-analysis tool version |
| `stream_0.bin` | Extracted binary TCP stream |
| `stream_0.txt` | Text representation of TCP stream |
| `stream_1.bin` | Extracted binary TCP stream |
| `stream_1.txt` | Text representation of TCP stream |

The packet capture and extracted streams provide supporting transport evidence.

### Preserved Runtime Files

The directory also contains:

```text
observe.py

runtime/
├── artifact.py
├── hub.py
├── routes.py
└── wire.py
```

These files preserve implementation material included in the original preflight export.

They are retained as historical source evidence.

The MD001 implementation documentation should identify the authoritative runtime and its source-integrity records. The copies in this directory should not automatically be treated as a separate implementation release.

## 5. Recorded Results

### Artifact Integrity

`PREFLIGHT_BYTE_COMPARISON.json` records identical artifact content at four observation points.

| Observation point | Bytes | SHA-256 agreement |
|---|---:|---|
| Producer | 332 | Match |
| Relay ingress | 332 | Match |
| Relay egress | 332 | Match |
| Verifier ingress | 332 | Match |

All four observations identify the same SHA-256 digest:

```text
00181b7b3e917a1280bdc22ac504f2adbba089ce2b5be6a454f6f895c880a177
```

The comparison record reports:

```json
{
  "equal": true
}
```

This establishes that the recorded artifact bytes remained identical across the identified observation points.

### Verification Decision

The verifier's preserved response records:

```json
{
  "accepted": true,
  "reason": "accepted",
  "signature_checks": 1
}
```

The response identifies the same artifact SHA-256 digest recorded in the transport comparison.

The producer's `result.json` records:

| Property | Recorded value |
|---|---|
| HTTP status | `200` |
| Accepted | `true` |
| Reason | `accepted` |
| Signature checks | `1` |

The verifier accepted the submitted assertion.

**Preflight result: PASS for the recorded valid-artifact transport and verification conditions.**

## 6. Independent Evidence Review

The historical preflight can be reviewed without starting the laboratory services.

### Step 1 — Inspect the Original Assertion

Open:

```text
SYS_NON_SCORED_PREFLIGHT_20261120T022358Z_18216/
```

Review:

- `operation.json`
- `artifact.json`
- `signed-bytes.bin`
- `submission.json`

These records identify the original operation and signed assertion.

### Step 2 — Compare Artifact Bytes

Inspect:

```text
PREFLIGHT_BYTE_COMPARISON.json
PI_INGRESS_ARTIFACT.bin
PI_EGRESS_ARTIFACT.bin
```

Compare the preserved artifacts against the producer output and verifier ingress record.

The expected SHA-256 digest is:

```text
00181b7b3e917a1280bdc22ac504f2adbba089ce2b5be6a454f6f895c880a177
```

### Step 3 — Inspect Verification Trust

Open the verifier evidence directory and inspect:

```text
trust-provisioned.json
```

This identifies the verification material configured for the preflight.

### Step 4 — Confirm the Decision

Inspect the verifier's request-specific decision record.

Confirm:

```text
accepted = true
reason = accepted
signature_checks = 1
```

Compare the artifact identity against the original producer assertion.

### Step 5 — Review Transport Evidence

Inspect:

```text
MD001_PREFLIGHT_20261120T021945Z.pcap
TCP_CONVERSATIONS.txt
TCP_PACKET_ANALYSIS.txt
```

Use the packet capture and extracted streams to cross-check the recorded transport observations.

These steps support independent inspection of the historical preflight.

A new execution requires the applicable runtime, configuration, dependencies, and provisioned trust material.

## 7. Relationship to Scored Experiments

The positive preflight preceded the scored MD001 experiments.

| Experiment | Purpose |
|---|---|
| Positive preflight | Establish a working valid-artifact transport and verification path |
| B01 | Record the scored valid-artifact baseline |
| N01 | Evaluate rejection after modification of a signed field |
| B02 | Evaluate verification after the originating producer becomes unavailable |

The preflight and B01 exercise related functionality but preserve distinct evidence records.

Their artifacts have different SHA-256 identities.

The preflight result must not be counted as an additional scored B01 execution.

## 8. Scope and Limitations

The preflight establishes that the recorded implementation successfully transported and verified a valid signed assertion under the tested configuration.

The evidence supports:

- Successful submission of the recorded signed assertion.
- Byte preservation across the identified observation points.
- Verification using provisioned trust material.
- An accepted verifier response.

It does not establish:

- Successful completion of the later scored experiments.
- Rejection of modified assertions.
- Verification after producer shutdown.
- Prevention of replay or duplicate execution.
- Durable authorization consumption.
- Physical execution enforcement.
- Security against compromise of the producer or signing key.
- Correct behavior under arbitrary network failures.
The preflight is supporting operational evidence.

The separately preserved scored-run directories provide the primary evidence for the MD001 experimental conclusions.
