# MD001 — Desktop Baseline Evidence

This directory preserves the evidence generated during the original MD001 desktop-baseline development and validation.

The evidence records local process execution, loopback transport, signed-artifact verification, mutation rejection, and independent re-verification after a simulated producer outage.

It does not contain the later MD001 physical scored campaign.

## Directory structure

| Directory | Contents |
|---|---|
| `offline/` | Original desktop validation attempts and their evidence |
| `physical/` | Historical placeholder for a planned physical extension |

The physical directory already contains its original README. That document describes the status of the desktop project when it was completed.

The later physical experiment is documented separately in the outer MD001 directory.

## Offline validation history

Three original run directories are retained.

### Initial infrastructure-blocked attempt

`offline/20261112T012548Z_f9d58244/`

The first attempt encountered a Windows sandbox restriction preventing a loopback socket connection.

Recorded outcome:

- 1 PASS
- 1 harness FAIL

The failure occurred before a cryptographic test-case decision.

This attempt remains part of the development history and must not be represented as a successful completed baseline.

### Subsequent successful validation

`offline/20261112T012609Z_1ff78364/`

This directory contains an earlier successful desktop validation run.

The original completion report records 21 PASS and 0 FAIL.

It is retained independently from the final selected run.

### Final selected baseline

`offline/20261112T025926Z_4d05fe22/`

This is the final run identified by the original STOP 1 completion report.

Recorded results:

| Measurement | Result |
|---|---|
| Passed checks | 21 |
| Failed checks | 0 |
| B01 | PASS |
| N01 | PASS |
| B02 | PASS |
| Deployment status | Not deployed |

The recorded status is:

`MD001_LOCAL_BUILD_VALIDATED_NOT_DEPLOYED`

These results describe desktop loopback simulations.

## Baseline scenarios

### B01 — Valid signed assertion

A producer completes the local sort operation and creates an Ed25519-signed assertion.

The artifact is conveyed through a mechanical relay.

Application-level observations compare the transmitted artifact bytes, and the verifier independently evaluates the signature and local acceptance criteria.

### N01 — Modified signed assertion

A downstream mutation adapter changes the signed outcome field without replacing the signature.

The verifier rejects the modified artifact.

The negative case tests signature integrity, not physical execution prevention.

### B02 — Producer unavailable

The original producer process is terminated.

The original verifier process is also terminated and replaced.

A fresh verifier process evaluates the retained B01 artifact without contacting the original producer.

This demonstrates independent re-verification under the simulated conditions.

It does not demonstrate physical producer power loss.

## Evidence contents

Individual run directories preserve applicable records including:

- Local operation results.
- Original signed artifacts.
- Canonical signed bytes.
- Disposable laboratory signing keys.
- Public-key trust configurations.
- Process identities and startup information.
- Relay and application-level transport observations.
- Original and modified artifact hashes.
- Verifier decisions.
- Test results.
- Source snapshots and build identities.
- SHA-256 manifests.

The exact contents of each attempt depend on how far execution progressed.

Do not assume an incomplete attempt contains the same evidence as a completed run.

## Integrity and provenance

Each completed run includes a `SHA256SUMS.txt` inventory.

The original desktop package also contains a root SHA-256 manifest and a separate manifest-digest record.

These establish recorded byte identities. They are not cryptographic signatures or independent attestations.

The original source inventory and provenance documentation identify the retained reference material and implementation baseline.

See:

- [`../COMPLETION.md`](../COMPLETION.md)
- [`../PROVENANCE.md`](../PROVENANCE.md)
- [`../SOURCE_REUSE.md`](../SOURCE_REUSE.md)

## Preservation requirements

Do not modify, delete, or replace:

- Historical run directories.
- Failed or incomplete attempts.
- Original test keys.
- Signed artifacts.
- Process observations.
- Results files.
- Historical manifests.
- Original source snapshots.

New documentation should remain outside the historical run directories.

A new validation attempt must receive a new run identity and its own evidence.

## Relationship to physical MD001

The desktop baseline preceded the physical MD001 deployment.

The physical campaign introduced independently operated hosts, network observations, and scored evidence that were not established by the original desktop simulation.

Those later results must be evaluated from the outer MD001 experiment directory.

The existence of later physical evidence does not change the historical classification of these desktop runs.

## Evidence boundary

The desktop baseline supports claims about the tested software behavior under loopback simulation.

It does not independently establish:

- Physical domain separation.
- Firewall enforcement.
- Physical producer power loss.
- Independent packet-capture reconstruction.
- Hardware execution isolation.
- Authorization consumption or replay prevention.

These distinctions must remain explicit when citing the evidence.
