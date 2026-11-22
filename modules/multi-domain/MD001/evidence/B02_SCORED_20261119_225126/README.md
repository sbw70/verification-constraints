# MD001 B02 — Producer-Unavailable Verification

## Overview

B02 is the producer-unavailable scored run for MD001, the Multi-Domain Stateless Verification experiment.

The run examines whether Domain B can independently verify a previously issued, valid signed assertion after the originating Domain A producer has been physically disconnected from power.

The experiment uses the original signed assertion from B01. No new assertion is required from the producer during the B02 verification transaction.

**Scored evidence directory:** `B02_SCORED_20261119_225126`  
**Recorded execution:** November 20, 2026 UTC  
**Recorded outcome:** PASS — original assertion accepted with producer unavailable

B02 evaluates verification independence from the originating producer's continued availability.

It does not establish independent authorization issuance, durable execution authority, or replay prevention.

## 1. Test Objective

The experiment evaluates five observable properties:

1. Domain A produces a valid signed assertion during the earlier B01 run.
2. The original assertion remains available after the producer is shut down.
3. The producer is physically disconnected from power before B02 verification.
4. Domain B receives the original assertion through the relay without modification.
5. A verifier operating in Domain B independently validates the assertion using previously provisioned trust material.

The principal question is whether verification of an existing signed assertion requires the originating producer to remain operational.

The recorded test demonstrates that it does not for this implementation and assertion.

## 2. Recorded Architecture

```text
Domain A — Producer
10.10.10.10
       |
       | Original B01 assertion issued
       | before producer shutdown
       v
Previously Preserved Signed Artifact
       |
       | Producer physically powered off
       | No new issuance
       v
B02 Submission
       |
       v
Mechanical Relay
30.30.30.30:18081
       |
       | PROVIDER_B route
       v
Domain B — Ingress
40.40.40.40:18443
       |
       | Original artifact preserved
       v
Domain B — Verifier
       |
       | Previously provisioned
       | Domain A verification key
       v
Signature verification
       |
       v
ACCEPT
```

The relay forwards the assertion without originating or modifying its cryptographic authority.

Domain B retains its own verification configuration and evaluates the received assertion independently.

The originating producer is not part of the B02 verification path.

## 3. Producer Shutdown and Availability

### Physical Shutdown

The preserved shutdown record states:

```text
Shutdown initiated: 2026-11-19 22:52:33 EST
Operator confirmation: plug pulled.
Network verification: TCP port 22 failed; ping failed.
Observation recorded: 2026-11-19T22:55:07.6464252-05:00
```

The record documents operator-confirmed physical power disconnection.

The associated network check targeted:

```text
10.10.10.10:22
```

The recorded results were:

| Check | Result |
|---|---|
| ICMP ping | Failed |
| TCP port 22 | Failed |
| Operator power-disconnection confirmation | Recorded |

These observations support the producer-unavailable test condition.

The network checks independently establish that the tested address did not respond to the specified probes. They do not, by themselves, prove physical power loss; that condition is supported by the separate operator shutdown record.

### Verification After Shutdown

The B02 submission reused the previously issued signed assertion.

The sender's `submission.json` identifies:

```json
{
  "command": "resubmit",
  "endpoint": {
    "host": "30.30.30.30",
    "port": 18081
  }
}
```

The recorded artifact identity matches the original B01 assertion.

No new Domain A issuance is recorded as part of the B02 verification transaction.

## 4. Original Assertion and Trust Material

### Original Artifact

B02 uses the signed assertion originally produced during B01.

The preserved artifact has SHA-256:

```text
61f113905f6c89e382f2bbccc081fb871ff08f4304a61d970197a85d3f8bcc5a
```

The artifact is 332 bytes.

The original assertion is preserved in the B02 submission evidence and can be compared against the earlier B01 producer artifact.

### Verification Trust

Domain B uses previously provisioned Domain A verification material.

The preserved trust configuration identifies the Domain A signing-key fingerprint:

```text
sha256:ce33a41359734e4b748d162720a57ddbbf666e968cddc854aaba6f57591ad2c3
```

The associated public verification-key material is recorded in the published trust configuration.

The provisioning record identifies:

```text
operator out-of-band transfer; verify fingerprint on B
```

This establishes the recorded method for transferring and checking the verification trust material.

The verifier does not need to retrieve a new public key from the unavailable producer during the scored transaction.

### Disposable Test Key

The B02 publication includes:

```text
lab-key/
├── TEST_ONLY_private.pem
├── provisioning.json
└── trust.json
```

`TEST_ONLY_private.pem` is the original disposable laboratory signing key.

It is preserved for historical reproducibility and must not be treated as a production credential.

The private key is not required for verification of the already signed B02 assertion. The corresponding public verification material is sufficient.

## 5. Evidence Directory

The B02 evidence is organized by submission, transport, verification, producer availability, and supporting host records.

### Submission — `B02_submit_20261120T035635Z_5534/`

| File | Purpose |
|---|---|
| `artifact.json` | Original signed assertion resubmitted during B02 |
| `signed-bytes.bin` | Original signed bytes |
| `submission.json` | Submission endpoint and artifact identity |
| `response.bin` | Returned response bytes |
| `result.json` | Parsed verification result |

The submission records the original B01 artifact identity.

### Relay — `B01_relay_20261120T033236Z_5344/`

| File | Purpose |
|---|---|
| `effective-hub-config.json` | Effective relay configuration |
| `process.json` | Relay process identity |
| `relay.jsonl` | Relay event log |

The relay directory retains its original process identifier from the earlier scored session.

Its inclusion in B02 preserves the relevant relay configuration and recorded forwarding evidence.

### Domain B Ingress — `B02_ingress_20261120T035825Z_99494/`

The ingress directory contains `process.json` and five request-specific records identified by the prefix:

`4fa8981e6acb471c85dc204e3de04998`

| File suffix | Purpose |
|---|---|
| `-ingress.bin` | Artifact received from the relay |
| `-egress.bin` | Artifact forwarded to the verifier |
| `-transport.json` | Transport metadata |
| `-downstream-response.bin` | Verifier response bytes |
| `-decision-or-response.json` | Parsed downstream response |

The ingress transport record identifies:

| Property | Recorded value |
|---|---|
| HTTP method | `POST` |
| Path | `/verify` |
| Mode | `pass` |
| Content length | 332 bytes |
| Destination | `PROVIDER_B` |

The ingress component operated in pass-through mode rather than mutation mode.

### Domain B Verifier — `B02_verifier_20261120T035716Z_99481/`

The verifier directory contains `process.json`, `trust-provisioned.json`, and three request-specific records identified by the prefix:

`7b8880a5375649f4a665ff99a7487e8d`

These preserve:

- Received artifact bytes.
- Transport metadata.
- Verification decision.
- Process identity.
- Provisioned verification trust.

The verifier's process-instance identifier differs from the earlier B01 verifier instance.

### Producer Availability Evidence

| File | Purpose |
|---|---|
| `PRODUCER_SHUTDOWN_RECORD.txt` | Operator-confirmed physical shutdown |
| `PRODUCER_OFFLINE_CHECK.txt` | Recorded network reachability checks |

These records establish the producer-unavailable condition used for B02 scoring.

### Host Environment Evidence

The directory:

`20261119T023809Z_dell_16438/`

contains supporting host-environment records.

| File | Purpose |
|---|---|
| `HOST_SHA256SUMS.txt` | Host evidence integrity inventory |
| `dpkg-architecture.txt` | Reported package architecture |
| `os-release.txt` | Operating-system identification |
| `package-status.txt` | Package-status information |
| `packages.txt` | Installed-package information |
| `probe.stdout.txt` | Host-probe standard output |
| `probe.stderr.txt` | Host-probe standard error |
| `uname.txt` | Kernel and system information |
| `probe/RESULTS.json` | Host-probe results |
| `probe/SHA256SUMS.txt` | Host-probe evidence hashes |

These records provide environmental context. They are not substitutes for the scored verification evidence.

### Transport and Comparison Evidence

| File | Purpose |
|---|---|
| `B02_BYTE_COMPARISON.json` | Cross-boundary artifact comparison |
| `MD001_B02_20261120T035603Z.pcap` | Packet capture |
| `PI_INGRESS_ARTIFACT.bin` | Artifact observed at relay ingress |
| `PI_EGRESS_ARTIFACT.bin` | Artifact observed at relay egress |
| `TCP_CONVERSATIONS.txt` | Extracted TCP conversation information |
| `TCP_PACKET_ANALYSIS.txt` | Packet-analysis record |
| `TSHARK_VERSION.txt` | Packet-analysis tool version |
| `stream_0.bin`, `stream_1.bin` | Extracted binary TCP streams |
| `stream_0.txt`, `stream_1.txt` | Text representations of extracted streams |

## 6. Recorded Results

### Artifact Integrity

`B02_BYTE_COMPARISON.json` records identical artifact content at four observation points:

| Observation point | Bytes | SHA-256 agreement |
|---|---:|---|
| Original B01 producer output | 332 | Match |
| B02 relay ingress | 332 | Match |
| B02 relay egress | 332 | Match |
| B02 verifier ingress | 332 | Match |

All four observations identify the same SHA-256 digest:

```text
61f113905f6c89e382f2bbccc081fb871ff08f4304a61d970197a85d3f8bcc5a
```

The comparison record reports:

```json
{
  "equal": true
}
```

The preserved comparison establishes that the original signed assertion was not modified across the recorded B02 observation points.

### Verification Decision

The verifier's preserved response records:

```json
{
  "accepted": true,
  "reason": "accepted",
  "signature_checks": 1
}
```

The response identifies the original B01 artifact SHA-256.

The sender's `result.json` records:

| Field | Value |
|---|---|
| HTTP status | `200` |
| Accepted | `true` |
| Reason | `accepted` |
| Signature checks | `1` |

The verifier recorded acceptance while the originating producer was unavailable under the documented test condition.

### Verifier Process Identity

The B02 verifier response identifies:

```text
process_instance:
e701195478694a8eabfff8ce7c5e95ae
```

The earlier B01 verifier response identified:

```text
process_instance:
f6e33415a02649fbbdad70a0b27d4323
```

The different identifiers establish that the recorded B02 verification response came from a different verifier process instance.

They do not, by themselves, establish the cause of the process change or prove loss of all verifier-local state.

### Scored Outcome

The recorded evidence establishes:

1. The original signed assertion was retained from B01.
2. The producer was reported physically disconnected from power.
3. Network checks against the producer failed.
4. The original artifact was resubmitted through the relay.
5. The artifact remained byte-identical across the recorded observation points.
6. Domain B verified the original assertion using provisioned trust material.
7. The verifier returned an accepted response.

**B02 result: PASS for the recorded producer-unavailable verification case.**

## 7. Independent Evidence Review

A reviewer can inspect the historical B02 result without starting the laboratory services.

### Step 1 — Establish Original Artifact Identity

Compare:

```text
B01_SCORED_20261119_223940/
  B01_sender_20261120T033737Z_18481/
    artifact.json
```

against:

```text
B02_SCORED_20261119_225126/
  B02_submit_20261120T035635Z_5534/
    artifact.json
```

The expected SHA-256 digest is:

```text
61f113905f6c89e382f2bbccc081fb871ff08f4304a61d970197a85d3f8bcc5a
```

### Step 2 — Review Producer Unavailability

Inspect:

```text
PRODUCER_SHUTDOWN_RECORD.txt
PRODUCER_OFFLINE_CHECK.txt
```

Confirm the recorded shutdown condition and unsuccessful network probes.

### Step 3 — Review Transport Integrity

Inspect:

```text
B02_BYTE_COMPARISON.json
PI_INGRESS_ARTIFACT.bin
PI_EGRESS_ARTIFACT.bin
```

Compare these observations with the preserved verifier-ingress artifact.

### Step 4 — Review Trust Provisioning

Inspect:

```text
lab-key/provisioning.json
lab-key/trust.json
```

Compare the recorded Domain A key identity with the verifier's `trust-provisioned.json`.

### Step 5 — Review Verification Decision

Inspect:

```text
B02_verifier_20261120T035716Z_99481/
```

Locate the request-specific decision record and confirm:

```text
accepted = true
reason = accepted
signature_checks = 1
```

Confirm that the returned artifact SHA-256 matches the original B01 assertion.

### Step 6 — Cross-Check Network Evidence

Inspect the packet capture and extracted TCP streams to correlate the recorded submission, forwarding path, and response.

These steps establish the historical evidence chain.

A fresh reproduction additionally requires the published implementation, runtime dependencies, network configuration, and trust provisioning described in the MD001 implementation documentation.

## 8. Scope and Limitations

B02 demonstrates that the recorded Domain B verifier accepted an existing signed assertion after the originating producer was reported physically powered off.

The evidence supports the following bounded conclusions:

- Verification of the existing assertion did not require a new interaction with the originating producer.
- The original assertion remained valid under the previously provisioned verification trust.
- The recorded relay and ingress path preserved the artifact bytes.
- The verifier accepted the original signature in a different recorded process instance.
- The producer-unavailable condition did not prevent verification of the previously issued assertion.

B02 does not establish:

- Issuance of new authority while the producer is unavailable.
- Authorization to repeat the underlying operation.
- Prevention of replay or duplicate execution.
- Durable single-use authority consumption.
- Persistence of execution-state records across power loss.
- Verification without previously provisioned trust material.
- Resistance to compromise of the original signing key.
- Physical execution enforcement.
- General availability under arbitrary network or provider failures.

In particular, acceptance of the original signed assertion must not be interpreted as authorization to execute the underlying operation again.

The verifier evaluates the authenticity of the preserved assertion. It does not establish that the originating operation was repeated or that a new execution decision was granted.

B02 therefore demonstrates verification independence from the originating producer's continued availability for the recorded assertion and trust configuration.

The valid-artifact baseline is documented in B01. The modified-assertion rejection case is documented in N01.
