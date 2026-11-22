# MD001 — Deployment Package and Physical Test Procedure

## Overview

This directory preserves the MD001 R1 application deployment package and the original procedure for conducting physical-network verification experiments.

The package was prepared after successful local adapter validation and before deployment to the laboratory hosts.

It contains the application archive, integrity records, proposed operator commands, physical test requirements, and disclosure inventory.

**Project:** MD001 — Multi-Domain Stateless Verification  
**Organization:** Xer0trust LLC  
**Package:** MD001_DEPLOYMENT_R1  
**Original preparation status:** `LOCAL_ADAPTERS_VALIDATED_AWAITING_DEPLOYMENT_APPROVAL`

The original deployment package was not itself a scored experiment.

The subsequently completed physical-network B01, N01, and B02 experiments are documented separately in the MD001 evidence directories.

## 1. Purpose

The deployment package was prepared to support controlled execution of three physical-network experiments:

| Experiment | Objective |
|---|---|
| B01 | Transport and independently verify a valid signed assertion |
| N01 | Reject an assertion modified after signing |
| B02 | Verify an existing assertion after the originating producer becomes unavailable |

The package also defines supporting requirements for:

- Application integrity.
- Runtime compatibility.
- Public-key provisioning.
- Network isolation.
- Relay forwarding.
- Independent packet observation.
- Evidence preservation.
- Process identity.
- Operator approval and rollback.

The procedures distinguish successful transport from successful cryptographic verification.

They also distinguish verification of an assertion from authorization or execution of the underlying operation.

## 2. Package Contents

```text
MD001_DEPLOYMENT_R1/
|
|-- COMMANDS.md
|-- TEST_PLAN.md
|-- VALIDATION.md
|-- X01.md
|
|-- MD001_APPLICATION_R1.tar.gz
|-- DEPLOY_BUNDLE_SHA256.txt
|-- SHA256SUMS.txt
|
`-- README.md
```

### File Responsibilities

| File | Purpose |
|---|---|
| `COMMANDS.md` | Proposed installation, service, preflight, and scored-run commands |
| `TEST_PLAN.md` | Physical experiment requirements and evidence criteria |
| `VALIDATION.md` | Local adapter validation and original deployment gate |
| `X01.md` | Artifact and transport disclosure inventory |
| `MD001_APPLICATION_R1.tar.gz` | Frozen application deployment archive |
| `DEPLOY_BUNDLE_SHA256.txt` | Application archive digest |
| `SHA256SUMS.txt` | Historical package and application integrity inventory |

The application archive is a deployment artifact.

The scored-run evidence is preserved outside this directory.

## 3. Application Bundle Integrity

The deployment archive is:

```text
MD001_APPLICATION_R1.tar.gz
```

Its recorded SHA-256 digest is:

```text
496e8ccde848599868aee923dff292f2ed9d1994bd06f7a95e8e6233a50987d5
```

The digest is preserved in:

```text
DEPLOY_BUNDLE_SHA256.txt
```

### Verify the Archive

From the deployment directory on Linux:

```sh
sha256sum -c DEPLOY_BUNDLE_SHA256.txt
```

Expected result:

```text
MD001_APPLICATION_R1.tar.gz: OK
```

The archive digest identifies the preserved deployment package.

It does not independently attest to the security of the application or the correctness of its execution.

### Historical Integrity Inventory

`SHA256SUMS.txt` records hashes for the original application and deployment materials.

It includes the archive and the application files from which the deployment package was prepared.

Because this README is added after the historical inventory was generated, it is not part of that original hash inventory.

Do not modify the historical manifest merely to incorporate this documentation.

A new manifest, if required, should be separately identified and dated.

## 4. Original Application Roles

The proposed physical deployment used three Linux hosts.

| Host | Role | Laboratory address |
|---|---|---|
| Dell | Domain A producer | `10.10.10.10` |
| Raspberry Pi | Mechanical relay | `30.30.30.30` |
| HP | Domain B ingress and verifier | `40.40.40.40` |

The controller coordinated installation, observation, and evidence custody.

### Request Path

```text
Domain A — Dell
10.10.10.10
     |
     | Signed assertion
     v
Mechanical Relay — Raspberry Pi
30.30.30.30:18081
     |
     | Forwarded assertion
     v
Domain B Ingress — HP
40.40.40.40:18443
     |
     | Local forwarding
     v
Domain B Verifier — HP
127.0.0.1:18444
     |
     | Signature verification
     v
Verification Decision
```

The Domain B verifier used locally provisioned public-key trust.

The relay did not receive the producer's private signing key.

The verifier did not require access to the producer's operational state.

## 5. Application Transport

The deployment procedure used HTTP requests carrying signed JSON assertions.

The relevant transport characteristics were:

| Property | Configuration |
|---|---|
| HTTP method | `POST` |
| Request path | `/verify` |
| Destination header | `X-MH-Destination: PROVIDER_B` |
| Relay listener | `30.30.30.30:18081` |
| Domain B ingress | `40.40.40.40:18443` |
| Domain B verifier | `127.0.0.1:18444` |

The laboratory transport used plaintext HTTP.

Port `18443` was not a TLS endpoint in this implementation.

The mechanical relay could modify HTTP framing and the Host header as required for forwarding.

The signed artifact body was required to remain unchanged.

The relay did not interpret the verification decision.

## 6. Original Local Validation

The deployment package records two successful final validation results.

### Adapter Integration

Evidence:

```text
../../validation/20261118T035328Z_c2e46f14/
```

Recorded result:

```text
12 PASS
0 FAIL
```

The checks covered:

- Producer operation and signing.
- Valid assertion submission.
- Byte-preserving relay transport.
- Invalid-signature rejection.
- Retention of the original signature during mutation.
- Verification after simulated producer unavailability.
- Repeated verification of the original assertion.
- Selected routing and ingress restrictions.
- Application source integrity.

The validation used local loopback substitutions.

It was not a physical-network experiment.

### Synthetic Stream Validation

Evidence:

```text
../../validation/20261118T035639Z_b8352e18/
```

Recorded result:

```text
6 PASS
0 FAIL
```

The checks covered:

- Exact extraction of a valid HTTP body.
- Rejection of truncated input.
- Rejection of an extra request.
- Rejection of an incorrect path.
- Rejection of an incorrect destination.
- Rejection of unsupported chunked framing.

The synthetic tests did not validate a physical packet capture.

### Combined Result

The original deployment validation report records:

```text
18 PASS
0 FAIL
```

This combines the final 12 adapter checks and six synthetic stream checks.

Earlier failed validation attempts remain preserved in the validation directory.

The final successful checks do not erase those historical failures.

## 7. Original Deployment Gates

The deployment package established explicit operator-controlled gates.

### Gate 1 — Deployment Approval

Before deployment, the operator was required to approve:

- Host identities.
- Installation directories.
- Runtime dependencies.
- Application ports.
- Network routes.
- Existing-service preservation.
- Trust provisioning.
- Evidence collection.

The original package did not authorize automatic deployment.

### Gate 2 — Physical Preflight

After approved deployment, the operator was required to verify:

- Actual network interfaces.
- Host routing.
- Listener bindings.
- Approved path connectivity.
- Direct Domain A-to-Domain B isolation.
- Public trust provisioning.
- Valid-artifact transport.
- Packet capture and artifact reconstruction.

A successful TCP connection alone was insufficient.

The preflight required application-level verification evidence.

### Gate 3 — Scored Execution

The scored experiments required separate approval after physical preflight.

Each scored run required fresh evidence directories and independent observations.

The original gate structure prevented local validation from being silently promoted into a physical-network PASS.

These gates describe the historical deployment procedure.

They are not instructions to repeat the completed experiments.

## 8. Runtime and Dependency Requirements

The original deployment instructions specified:

- Python 3.
- Python virtual environments.
- The application's recorded dependency requirements.
- The originally specified `cryptography` version.
- Verification of installed runtime versions.
- Verification of application file hashes.

The original instructions specified `cryptography==49.0.0`.

They also required stopping if the approved dependency configuration could not be satisfied.

No silent dependency substitution was authorized.

The later host-runtime evidence records the actual environments used during preparation and testing.

Those observed environments must be distinguished from the original proposed dependency configuration.

See:

```text
../../evidence/support/SUPPORT_EXPORT_20261119_231556/
```

## 9. Public-Key Provisioning

The deployment procedure required a new disposable laboratory signing key.

The private key remained under Domain A custody.

Only the public trust configuration was transferred to Domain B.

### Intended Separation

```text
Domain A
    |
    | Private signing key
    | Creates signed assertion
    v
Mechanical Relay
    |
    | Signed assertion only
    v
Domain B
    |
    | Provisioned public key
    | Verifies signature
    v
Verification Result
```

The relay did not require the signing key.

The verifier did not require the private key.

The key fingerprint and trust configuration were to be compared out of band.

The deployment archive excluded the desktop preparation keys.

Test keys were not intended for operational use.

## 10. B01 — Valid Cross-Domain Verification

The physical B01 procedure required Domain A to:

1. Execute `LOCAL_SORT_V1`.
2. Record the operation result.
3. Generate the signed assertion.
4. Submit the assertion through the mechanical relay.

The expected local operation was:

```text
Input:  [9,1,4,2]
Output: [1,2,4,9]
```

The relay was required to forward the original artifact.

Domain B was required to verify the signature using provisioned trust.

### Required Evidence

The original test plan required:

- Producer operation record.
- Original signed assertion.
- Exact signed bytes.
- Producer submission record.
- Relay ingress observation.
- Relay egress observation.
- Verifier ingress observation.
- Verification response.
- Process and configuration identities.
- Physical-network packet capture.

### Required Result

```text
accepted = true
signature_checks = 1
```

The producer, relay ingress, relay egress, and verifier ingress artifacts were required to be byte-identical.

The scored B01 result is documented separately:

```text
../../evidence/B01_SCORED_20261119_223940/
```

## 11. N01 — Modified Assertion Rejection

The N01 procedure required reuse of the original B01 assertion.

The artifact was to traverse the mechanical relay unchanged.

Domain B ingress was then configured to modify a signed field.

### Mutation

```text
event.outcome

SUCCESS -> FAILURE
```

The original signature was retained.

The verifier was required to reject the modified artifact.

### Required Result

```text
HTTP 422
accepted = false
reason = invalid_signature
signature_checks = 1
```

The original and modified artifact hashes were required to differ.

The relay egress artifact was required to match the original.

The verifier ingress artifact was required to match the modified version.

The original test plan explicitly prohibited treating all N01 observation hashes as equal.

The scored N01 result is documented separately:

```text
../../evidence/N01_SCORED_20261119_224654/
```

## 12. B02 — Producer-Unavailable Verification

The B02 procedure required preservation of the original B01 assertion outside Domain A before shutdown.

The original producer was then to become physically unavailable.

### Required Observations

The test plan required:

1. Preservation of the original B01 artifact.
2. Independent artifact custody.
3. Operator observation of producer power-off.
4. Failed connection to the known producer endpoint.
5. Preservation of the original verifier process identity.
6. Restart of the verifier.
7. A new verifier process identity.
8. Resubmission of the original assertion without contacting the producer.
9. Fresh signature verification.

The producer's private signing key was not required for resubmission.

The relay was not permitted to create or resign the assertion.

### Required Result

```text
accepted = true
signature_checks = 1
```

The original artifact hash was required to remain unchanged.

The test plan distinguished a failed network probe from physical power-off evidence.

A failed connection alone was not sufficient to establish physical shutdown.

The scored B02 result is documented separately:

```text
../../evidence/B02_SCORED_20261119_225126/
```

## 13. Independent Packet Evidence

The deployment plan required physical packet capture on the Raspberry Pi.

The purpose was to establish independent observations of the assertion entering and leaving the relay.

### Observation Points

```text
Producer artifact
       |
       v
Relay ingress
       |
       v
Relay egress
       |
       v
Verifier ingress
```

The original test plan distinguished relay diagnostic hashes from independently observed packet data.

A relay egress hash records a send attempt.

It does not independently prove that the downstream host received the bytes.

### Capture Requirements

The physical procedure required:

- Identification of the actual capture interface.
- Complete packet capture.
- Capture tool and version.
- TCP flow identification.
- Direction-specific stream reconstruction.
- Complete HTTP message boundaries.
- Detection of ambiguous or incomplete reassembly.
- Extraction of original HTTP bodies.
- Byte comparison across observation points.

The provided `observe.py` utility was intended to process already reconstructed TCP streams.

It was not intended to perform packet reassembly itself.

### Evidence Standard

For B01, the original test plan required identical artifact bytes at all four observation points.

For N01, it required preservation of the original artifact through the relay and identification of the modified artifact at the verifier.

For B02, it required preservation of the original B01 artifact through the producer-unavailable resubmission path.

The corresponding scored directories preserve the later packet and artifact evidence.

## 14. X01 — Disclosure Inventory

The deployment package includes:

```text
X01.md
```

This document identifies information exposed by the assertion format and transport.

### Signed Assertion Fields

The six signed fields are:

```text
version
producer_id
key_id
artifact_id
event_id
outcome
```

The envelope also includes the signature.

These fields are intentionally disclosed to support verification.

The event identifier and outcome disclose the asserted event category and result.

They do not disclose the full underlying operation logic.

### Transport Metadata

The original X01 inventory identifies:

- IP addresses and ports.
- HTTP method and path.
- Host header.
- Content length.
- Content type.
- Destination header.
- Connection timing and behavior.
- HTTP response status.
- Verification decision.
- Artifact digest.
- Verifier process metadata.

The transport was plaintext.

The disclosure inventory does not claim confidentiality of the transmitted assertion.

### Evidence Metadata

The laboratory evidence also records:

- Process identities.
- Peer addresses.
- Timestamps.
- Artifact hashes.
- Ingress mode.
- Verification decisions.
- Diagnostic information.

These records are available to the operator possessing the evidence.

X01 is a bounded disclosure inventory, not a claim of absolute confidentiality.

## 15. Service Preservation and Rollback

The original procedure prohibited unnecessary changes to existing laboratory services.

It required:

- Separate foreground application processes.
- No unattended service installation.
- No automatic boot configuration.
- No unauthorized firewall changes.
- No changes to existing MP005 or MH001 services.
- Preservation of all generated evidence.
- Restoration of pass-mode ingress after N01.
- Operator review before any network modification.

The application rollback procedure consisted of stopping the MD001 foreground processes while preserving evidence.

It did not authorize deletion of previous run records.

These safeguards were part of the original deployment plan.

## 16. Relationship to Published Evidence

The deployment package is a historical implementation and procedure record.

It should be read alongside the subsequent evidence.

| Directory | Purpose |
|---|---|
| `../../validation/` | Local adapter and synthetic stream validation |
| `../../evidence/support/` | Physical-network preflight and environment evidence |
| `../../evidence/B01_SCORED_20261119_223940/` | Valid assertion verification |
| `../../evidence/N01_SCORED_20261119_224654/` | Signed-field mutation rejection |
| `../../evidence/B02_SCORED_20261119_225126/` | Producer-unavailable verification |

The original deployment documents describe intended procedures and acceptance criteria.

The scored evidence directories record what was subsequently observed.

A proposed procedure is not evidence that the procedure was executed.

## 17. Scope and Limitations

The deployment package establishes:

- The intended application configuration.
- The original test procedure.
- The original approval gates.
- The frozen deployment archive identity.
- The local validation results.
- The required physical evidence standard.
- The intended separation of signing, transport, and verification responsibilities.

It does not independently establish:

- Completion of physical deployment.
- Completion of the scored experiments.
- Actual firewall enforcement.
- Actual producer power loss.
- Successful physical packet reconstruction.
- Physical execution isolation.
- Replay prevention.
- Durable single-use authority consumption.
- Resistance to signing-key compromise.
- Production deployment readiness.

Those questions require separate evidence.

The later MD001 scored directories provide the relevant observations for the three completed physical-network experiments.

## 18. Conclusion

The MD001 R1 deployment package preserves the application archive, integrity records, physical test plan, proposed commands, and disclosure inventory used to prepare the laboratory experiments.

The original local preparation completed with:

```text
12/12 adapter checks passed
6/6 synthetic stream checks passed
```

The package then remained subject to operator-controlled deployment and scoring gates.

The subsequently completed B01, N01, and B02 experiments are documented separately.

This directory preserves the original deployment baseline without retroactively changing its historical status or treating planned procedures as completed observations.
