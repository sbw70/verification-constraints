# MD001 — Supporting Environment and Preflight Evidence

## Overview

This directory preserves supporting evidence collected during preparation and preflight validation of the MD001 Multi-Domain Stateless Verification experiment.

The evidence includes:

- Raspberry Pi runtime and application-integrity checks.
- HP Linux host runtime and application-integrity checks.
- Relay configuration and forwarding records.
- Domain B ingress transport and response records.
- Negative-preflight submission and rejection records.

**Evidence directory:** `SUPPORT_EXPORT_20261119_231556`  
**Evidence classification:** Supporting, non-scored  
**Recorded host-probe outcome:** 20 PASS / 0 FAIL on each host  
**Recorded positive transport response:** HTTP 200 — accepted  
**Recorded negative submission response:** HTTP 422 — invalid_signature

The directory supports reconstruction of the environment and preliminary verification behavior.

It does not constitute an additional scored experiment.

## 1. Purpose

The supporting export preserves evidence relevant to three questions:

1. Were the designated Linux hosts able to load and validate the frozen MD001 application?
2. Did the configured relay and Domain B ingress support the positive-preflight transport path?
3. Did the negative-preflight submission return the expected signature-rejection response?

The host probes and service observations address different aspects of these questions.

Host-probe success does not establish successful network transport.

Successful network transport does not independently establish the integrity of every deployed application component.

The evidence must therefore be interpreted according to the individual observation being examined.

## 2. Evidence Organization

```text
SUPPORT_EXPORT_20261119_231556/
|
|-- 20261119T023931Z_pi_3322/
|   |-- HOST_SHA256SUMS.txt
|   |-- dpkg-architecture.txt
|   |-- os-release.txt
|   |-- package-status.txt
|   |-- packages.txt
|   |-- probe.stdout.txt
|   |-- probe.stderr.txt
|   |-- uname.txt
|   `-- probe/
|       |-- RESULTS.json
|       `-- SHA256SUMS.txt
|
|-- 20261119T024743Z_hp_96824/
|   |-- HOST_SHA256SUMS.txt
|   |-- dpkg-architecture.txt
|   |-- os-release.txt
|   |-- package-status.txt
|   |-- packages.txt
|   |-- probe.stdout.txt
|   |-- probe.stderr.txt
|   |-- uname.txt
|   `-- probe/
|       |-- RESULTS.json
|       `-- SHA256SUMS.txt
|
|-- SYS_PREFLIGHT_relay_20261119T025854Z_3381/
|   |-- effective-hub-config.json
|   |-- process.json
|   `-- relay.jsonl
|
|-- SYS_PREFLIGHT_ingress_20261119T030123Z_96950/
|   |-- process.json
|   |-- 78c923dde38140dc870b739a5322511f-ingress.bin
|   |-- 78c923dde38140dc870b739a5322511f-egress.bin
|   |-- 78c923dde38140dc870b739a5322511f-transport.json
|   |-- 78c923dde38140dc870b739a5322511f-downstream-response.bin
|   `-- 78c923dde38140dc870b739a5322511f-decision-or-response.json
|
|-- SYS_NEGATIVE_PREFLIGHT_sender_20261120T031227Z_18420/
|   |-- artifact.json
|   |-- signed-bytes.bin
|   |-- submission.json
|   |-- response.bin
|   `-- result.json
|
`-- image-1795050771232.jpg
```

The image is retained as part of the historical export. It is not used as the primary evidence for the cryptographic verification results documented here.

## 3. Raspberry Pi Runtime Probe

### Evidence Directory

```text
20261119T023931Z_pi_3322/
```

The preserved `probe/RESULTS.json` identifies:

| Property | Recorded value |
|---|---|
| Profile | `pi` |
| Architecture | `aarch64` |
| Python | `3.13.5` |
| Cryptography | `43.0.0` |
| OpenSSL | `3.5.7` |
| Passed checks | `20` |
| Failed checks | `0` |
| Status | `PROBE_PASS_NOT_SCORED` |

The recorded platform identifies a Raspberry Pi Linux environment.

The application directory was:

```text
/home/seth/MD001_APPLICATION_R1
```

### Probe Classification

The probe identifies its operating mode as:

```text
NON_SCORED_NO_NETWORK_NO_SERVICE_RUNTIME_PROBE
```

The recorded result also contains:

```json
{
  "requirement_pin_satisfied": false,
  "passed": 20,
  "failed": 0,
  "status": "PROBE_PASS_NOT_SCORED"
}
```

The successful checks establish that the tested application and runtime passed the probe's defined conditions.

The `requirement_pin_satisfied` field remains false in the preserved result.

That field must not be silently converted into a successful dependency-pinning claim.

### Application and Cryptographic Checks

The recorded probe checks include:

- Frozen application hashes.
- Fixture integrity.
- Python and cryptographic dependency checks.
- Application imports.
- Runtime-lock validation.
- Configuration parsing.
- PEM and PKCS8 key loading.
- Raw public-key serialization.
- Ed25519 signing and verification.
- Canonical artifact comparison.
- Known-signature verification.
- Modified-signature rejection.
- Unknown-key rejection.
- Producer-key mismatch rejection.
- Malformed-artifact rejection.
- Canonical ordering independence.
- HTTP framing and observer validation.
- Application immutability checks.

All 20 recorded checks passed.

These are local probe results, not scored cross-domain network transactions.

## 4. HP Linux Runtime Probe

### Evidence Directory

```text
20261119T024743Z_hp_96824/
```

The preserved `probe/RESULTS.json` identifies:

| Property | Recorded value |
|---|---|
| Profile | `hp` |
| Architecture | `x86_64` |
| Python | `3.12.3` |
| Cryptography | `41.0.7` |
| OpenSSL | `3.0.13` |
| Passed checks | `20` |
| Failed checks | `0` |
| Status | `PROBE_PASS_NOT_SCORED` |

The application directory was:

```text
/home/seth/MD001_APPLICATION_R1
```

### Probe Classification

The HP probe uses the same recorded mode:

```text
NON_SCORED_NO_NETWORK_NO_SERVICE_RUNTIME_PROBE
```

Its result includes:

```json
{
  "requirement_pin_satisfied": false,
  "passed": 20,
  "failed": 0,
  "status": "PROBE_PASS_NOT_SCORED"
}
```

The HP host passed all 20 defined probe checks.

As with the Raspberry Pi, the recorded result does not establish satisfaction of the dependency-pinning requirement.

### Cross-Platform Observation

The two host probes ran under different architectures and dependency versions.

| Property | Raspberry Pi | HP |
|---|---|---|
| Architecture | `aarch64` | `x86_64` |
| Python | `3.13.5` | `3.12.3` |
| Cryptography | `43.0.0` | `41.0.7` |
| OpenSSL | `3.5.7` | `3.0.13` |
| Passed | 20 | 20 |
| Failed | 0 | 0 |

Both probes report successful canonical-artifact and signature compatibility checks against the designated desktop fixture.

This supports compatibility of the tested application behavior across the two recorded host environments.

It does not establish compatibility with arbitrary operating systems, dependency versions, or hardware.

## 5. Application Integrity Evidence

Both host-probe results preserve SHA-256 values for the frozen MD001 application.

The recorded application files include:

```text
COMMANDS.md
README.md
RUNTIME_LOCK.json
TEST_PLAN.md
VALIDATION.md
X01.md

configs/
    ingress.json
    ingress_N01.json
    relay.json
    verifier.json

md001.py
observe.py
requirements.txt

runtime/
    artifact.py
    hub.py
    routes.py
    wire.py
```

The probe results contain individual application hashes under:

```text
application_sha256
```

The host directories also preserve:

```text
HOST_SHA256SUMS.txt
probe/SHA256SUMS.txt
```

These records support independent comparison of the captured application and probe artifacts.

The preserved hash inventories are evidence of the recorded files.

They do not establish the integrity of unrelated files or subsequent modifications to the application.

## 6. Relay Configuration and Evidence

### Evidence Directory

```text
SYS_PREFLIGHT_relay_20261119T025854Z_3381/
```

The directory contains:

```text
effective-hub-config.json
process.json
relay.jsonl
```

### Recorded Configuration

The effective configuration identifies:

```json
{
  "hub_id": "HUB_B",
  "listen": {
    "host": "30.30.30.30",
    "port": 18081
  },
  "timeout_seconds": 10
}
```

The configured routes include:

| Destination | Endpoint |
|---|---|
| `PROVIDER_A` | `127.0.0.1:42835` |
| `PROVIDER_B` | `40.40.40.40:18443` |

The positive-preflight transport path uses the configured `PROVIDER_B` destination.

The relay records establish the configured forwarding environment.

They do not establish that the relay possessed authority to issue or validate the signed assertion.

## 7. Positive-Preflight Ingress Evidence

### Evidence Directory

```text
SYS_PREFLIGHT_ingress_20261119T030123Z_96950/
```

The request identifier is:

```text
78c923dde38140dc870b739a5322511f
```

### Recorded Transport

The ingress transport record identifies:

| Property | Recorded value |
|---|---|
| Method | `POST` |
| Path | `/verify` |
| Content length | 332 bytes |
| Destination | `PROVIDER_B` |
| Mode | `pass` |

The recorded ingress artifact SHA-256 is:

```text
00181b7b3e917a1280bdc22ac504f2adbba089ce2b5be6a454f6f895c880a177
```

This matches the positive-preflight assertion.

### Recorded Response

The preserved response records:

```json
{
  "accepted": true,
  "reason": "accepted",
  "signature_checks": 1
}
```

The HTTP status was:

```text
200
```

The response identifies the same artifact SHA-256.

This supports the positive-preflight observation that the valid assertion reached Domain B and was accepted.

The complete positive-preflight evidence is preserved separately in:

```text
../PREFLIGHT_EXPORT_20261119_213249/
```

## 8. Negative-Preflight Submission Evidence

### Evidence Directory

```text
SYS_NEGATIVE_PREFLIGHT_sender_20261120T031227Z_18420/
```

The directory contains:

```text
artifact.json
signed-bytes.bin
submission.json
response.bin
result.json
```

### Recorded Submission

The submission identifies:

```json
{
  "command": "resubmit",
  "endpoint": {
    "host": "30.30.30.30",
    "port": 18081
  }
}
```

The submitted original artifact SHA-256 is:

```text
00181b7b3e917a1280bdc22ac504f2adbba089ce2b5be6a454f6f895c880a177
```

This matches the positive-preflight artifact.

### Recorded Rejection

The returned response identifies the modified artifact SHA-256:

```text
00f0d2507757a66c95c0c9e708852dc80e57222e36b4538369fae25503ae37d2
```

The response records:

```json
{
  "accepted": false,
  "reason": "invalid_signature",
  "signature_checks": 1
}
```

The HTTP status was:

```text
422
```

This establishes that the sender received the expected rejection response.

The corresponding mutation and verifier evidence is preserved separately in:

```text
../NEGATIVE_PREFLIGHT_20261119_221616/
```

The supporting sender record must not be counted as an additional negative-preflight execution.

## 9. Independent Evidence Review

The historical supporting evidence can be inspected without starting the laboratory services.

### Step 1 — Review Host Results

Inspect:

```text
20261119T023931Z_pi_3322/probe/RESULTS.json

20261119T024743Z_hp_96824/probe/RESULTS.json
```

Confirm the recorded:

```text
passed = 20
failed = 0
status = PROBE_PASS_NOT_SCORED
```

Also confirm:

```text
requirement_pin_satisfied = false
```

### Step 2 — Review Host Integrity Records

Inspect the host-level and probe-level SHA-256 inventories.

Compare the recorded application hashes between the two host-probe results.

### Step 3 — Review Relay Configuration

Inspect:

```text
SYS_PREFLIGHT_relay_20261119T025854Z_3381/
```

Confirm the configured listener and `PROVIDER_B` destination.

Review the relay log and process record.

### Step 4 — Review Positive Ingress Evidence

Inspect:

```text
SYS_PREFLIGHT_ingress_20261119T030123Z_96950/
```

Confirm:

```text
mode = pass
accepted = true
reason = accepted
```

Compare the recorded artifact identity against the positive-preflight evidence.

### Step 5 — Review Negative Submission Evidence

Inspect:

```text
SYS_NEGATIVE_PREFLIGHT_sender_20261120T031227Z_18420/
```

Confirm:

```text
command = resubmit
accepted = false
reason = invalid_signature
```

Compare the original submitted artifact identity against the modified artifact identity returned by the verifier.

### Step 6 — Correlate the Preflight Records

Compare the supporting export against:

```text
../PREFLIGHT_EXPORT_20261119_213249/

../NEGATIVE_PREFLIGHT_20261119_221616/
```

The supporting export provides additional host, relay, ingress, and sender observations.

The dedicated preflight directories preserve the corresponding primary preflight evidence.

## 10. Relationship to Scored Experiments

The supporting export documents preparation and preliminary verification behavior.

| Evidence | Classification | Recorded result |
|---|---|---|
| Raspberry Pi runtime probe | Non-scored | 20 PASS / 0 FAIL |
| HP runtime probe | Non-scored | 20 PASS / 0 FAIL |
| Positive-preflight ingress | Non-scored | Accepted |
| Negative-preflight submission | Non-scored | Rejected — invalid_signature |
| B01 | Scored | Valid assertion accepted |
| N01 | Scored | Modified assertion rejected |
| B02 | Scored | Original assertion accepted with producer unavailable |

The supporting export must not be treated as an additional scored run.

Its purpose is to preserve environmental and operational evidence relevant to the scored experiments.

## 11. Scope and Limitations

The supporting export establishes that:

- Two designated Linux hosts passed the defined local runtime probes.
- The recorded application hashes were preserved.
- The configured relay exposed a route to `PROVIDER_B`.
- The positive-preflight ingress recorded an accepted verification response.
- The negative-preflight sender recorded an `invalid_signature` rejection.

The evidence does not establish:

- Satisfaction of the recorded dependency-pinning requirement.
- Successful execution of the later scored experiments.
- Correct behavior across arbitrary platforms or dependency versions.
- Prevention of replay or duplicate execution.
- Durable single-use authority consumption.
- Physical execution enforcement.
- Resistance to signing-key compromise.
- General security against arbitrary network or host compromise.

The host probes were explicitly classified as non-scored, no-network, no-service runtime checks.

The transport observations are separate supporting records.

The scored B01, N01, and B02 directories remain the primary sources for the MD001 experimental results.
