# MD001 — Runtime Compatibility Review R1

## Purpose

This directory preserves the first runtime compatibility review for the MD001 physical-deployment application.

The review examined whether the frozen MD001 application could operate using the Python and cryptography versions already reported on the Dell, HP, and Raspberry Pi hosts.

Its objective was to avoid unnecessary dependency installation while preserving the original application source and its recorded hashes.

The review was conducted before physical host validation.

## Original review status

The recorded finding was:

`SOURCE_API_COMPATIBLE_CANDIDATES_HOST_VALIDATION_PENDING`

At the completion of this review:

- No physical host had been contacted.
- No application had been deployed.
- No service had been started.
- No firewall or network configuration had been changed.
- No physical test had been scored.

The review established candidate source/API compatibility, not verified runtime compatibility on the actual hosts.

## Dependency distinction

The frozen application specifies:

`cryptography==49.0.0`

The reported Linux installations used earlier versions.

| Host | Python | Reported cryptography | Review finding |
|---|---|---|---|
| Dell | 3.12.3 | 41.0.7 | Candidate |
| HP | 3.12.3 | 41.0.7 | Candidate |
| Raspberry Pi | 3.13.5 | 43.0.0 | Candidate |

These installations do not satisfy the literal version pin.

Source inspection found that the application used cryptographic APIs available in the reported versions.

The review therefore proposed an explicit deployment-runtime exception, subject to operator acceptance and successful validation on each actual host.

This was not a modification of the frozen dependency specification.

## Reviewed application components

The review inspected six Python modules:

- `md001.py`
- `observe.py`
- `runtime/artifact.py`
- `runtime/hub.py`
- `runtime/routes.py`
- `runtime/wire.py`

The review checked the application's use of:

- Ed25519 key generation.
- Signature creation and verification.
- PEM private-key serialization and loading.
- Raw public-key serialization.
- Canonical JSON encoding.
- HTTP transport.
- Process and evidence handling.
- Standard-library compatibility.

The frozen runtime source hashes matched the recorded runtime lock.

All 17 application-bundle content hashes matched the archive manifest.

## Desktop validation

The review included a local runtime probe.

Recorded result:

**18 PASS — 0 FAIL**

Environment:

- Python 3.14.3
- cryptography 49.0.0
- Windows desktop

A Python 3.12 grammar parse also passed for the shipped Python modules.

That grammar check did not execute the application under Python 3.12.

The original adapter and HTTP extraction tests were not rerun during this review.

## Deterministic compatibility fixture

`FIXTURE.json` contains a synthetic signing fixture generated using the frozen artifact implementation.

Its purpose was to support comparison of canonical encoding, signatures, and verification behavior across runtime environments.

The fixture uses explicitly disclosed synthetic test material.

It is not a deployment signing credential or a scored physical artifact.

The proposed Linux host probes required matching deterministic results.

## Proposed host validation

The review specified a separate validation procedure for each physical host.

The procedure required:

1. Verification of the original application archive and file hashes.
2. Identification of the actual system Python interpreter.
3. Verification of the installed cryptography package and import path.
4. Execution of the host-specific runtime probe.
5. Successful Ed25519 operations and deterministic fixture comparison.
6. Rejection of invalid signatures and malformed artifacts.
7. Preservation of the original application and dependency files.

The proposed acceptance result was:

`PROBE_PASS_NOT_SCORED`

with 20 passing checks per Linux host.

These were acceptance criteria, not results established by the original desktop review.

## Directory contents

| File or directory | Purpose |
|---|---|
| `REVIEW.md` | Compatibility findings and proposed runtime exception |
| `REVIEW_STATUS.json` | Recorded review status |
| `COMMANDS.md` | Proposed host staging, validation, and launch procedure |
| `PROPOSED_COMMANDS.ps1` | Reviewable PowerShell orchestration |
| `runtime_probe.py` | Runtime compatibility probe |
| `FIXTURE.json` | Synthetic deterministic signing fixture |
| `FIXTURE_SHA256.txt` | Fixture integrity record |
| `APPROVED_APP_FILES.json` | Frozen application file identities |
| `OFFLINE_FALLBACK.md` | Alternative if the installed runtimes are unsuitable |
| `local_validation/` | Original desktop probe evidence |
| `REVIEW_FILES_SHA256SUMS.txt` | Review-file integrity inventory |
| `REVIEW_BUNDLE_SHA256.txt` | Review archive digest |
| `MD001_RUNTIME_REVIEW_R1.tar.gz` | Packaged review materials |

## Offline fallback

The review includes a separate offline dependency-installation plan.

That plan applies if the existing system packages cannot satisfy the approved runtime criteria or if exact cryptography 49.0.0 becomes mandatory.

The fallback was not executed during this review.

No dependency wheels were downloaded or installed as part of the recorded review.

## Relationship to physical MD001

This review supported preparation for the later physical MD001 experiment.

It does not independently establish that:

- The physical hosts passed their runtime probes.
- Application services started successfully.
- Network connectivity was verified.
- Firewall rules were enforced.
- Physical B01, N01, or B02 passed.

Those conclusions require evidence from the subsequent deployment and scored-test records.

## Preservation

This directory is a historical review artifact.

Do not modify its original:

- Review findings.
- Status records.
- Runtime probe.
- Synthetic fixture.
- Validation evidence.
- Source inventories.
- SHA-256 manifests.
- Packaged archive.

Any later compatibility revision should receive a separate identity.

## Verification boundary

Source/API compatibility is not equivalent to successful execution on a particular operating system, architecture, or installed cryptographic backend.

The review identified plausible runtime candidates and defined the checks required before deployment.

Its original status must remain distinct from the results of subsequent physical testing.
