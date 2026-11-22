# MD001 — Runtime Compatibility and Source-Integrity Review

## Overview

This directory preserves the MD001 R1 runtime compatibility review, its frozen-source verification records, synthetic cryptographic fixture, local validation results, and proposed Linux deployment procedure.

The review was created to address a dependency compatibility issue discovered during preparation for physical-network deployment.

The frozen application specified:

```text
cryptography==49.0.0
```

The designated Linux hosts had earlier distribution-provided versions installed.

Rather than modifying the frozen application or silently substituting dependencies, the review examined whether the existing source could operate with those exact installed environments.

**Review:** MD001_RUNTIME_REVIEW_R1  
**Organization:** Xer0trust LLC  
**Original finding:** `SOURCE_API_COMPATIBLE_CANDIDATES_HOST_VALIDATION_PENDING`  
**Desktop runtime validation:** 18 PASS / 0 FAIL  
**Original review classification:** Non-scored, no-network, no-service

The original review did not contact the Linux hosts.

Subsequent Linux runtime-probe evidence is preserved separately under the MD001 supporting evidence directory.

## 1. Review Objective

The review addressed four questions:

1. Did the frozen application require cryptographic APIs exclusive to version 49.0.0?
2. Could the existing application source operate with the installed Linux cryptography versions?
3. Could compatibility be evaluated without modifying the application or installing additional dependencies?
4. Could the proposed runtime exception be documented and independently validated before physical-network testing?

The review distinguished source-level API compatibility from actual runtime execution.

Finding compatible API names in source documentation does not establish that a particular host can import the package or execute the cryptographic operations.

Host-specific validation was therefore required.

## 2. Evidence Directory

```text
MD001_RUNTIME_REVIEW_R1/
|
|-- REVIEW.md
|-- COMMANDS.md
|-- PROPOSED_COMMANDS.ps1
|-- runtime_probe.py
|
|-- APPROVED_APP_FILES.json
|-- FIXTURE.json
|-- FIXTURE_SHA256.txt
|
|-- MD001_RUNTIME_REVIEW_R1.tar.gz
|-- REVIEW_BUNDLE_SHA256.txt
|-- REVIEW_FILES_SHA256SUMS.txt
|
|-- local_validation/
|   |-- desktop49/
|   |   |-- RESULTS.json
|   |   `-- SHA256SUMS.txt
|   |
|   `-- desktop49_final/
|       |-- RESULTS.json
|       `-- SHA256SUMS.txt
|
`-- README.md
```

### Principal Files

| File | Purpose |
|---|---|
| `REVIEW.md` | Compatibility findings and proposed runtime exception |
| `COMMANDS.md` | Revised deployment and validation procedure |
| `PROPOSED_COMMANDS.ps1` | Reviewable PowerShell staging and validation automation |
| `runtime_probe.py` | Non-scored runtime and cryptographic compatibility checks |
| `APPROVED_APP_FILES.json` | Approved application file identities and SHA-256 values |
| `FIXTURE.json` | Deterministic synthetic Ed25519 verification fixture |
| `FIXTURE_SHA256.txt` | Fixture integrity record |
| `MD001_RUNTIME_REVIEW_R1.tar.gz` | Runtime review package |
| `REVIEW_BUNDLE_SHA256.txt` | Review archive integrity record |
| `REVIEW_FILES_SHA256SUMS.txt` | Review-file integrity inventory |

The directory also preserves two desktop runtime-probe results.

## 3. Original Dependency Conflict

The frozen application requirements specified:

```text
cryptography==49.0.0
```

The reported Linux environments were:

| Host | Python | Cryptography |
|---|---|---|
| Dell | 3.12.3 | 41.0.7 |
| HP | 3.12.3 | 41.0.7 |
| Raspberry Pi | 3.13.5 | 43.0.0 |

Neither cryptography 41.0.7 nor 43.0.0 satisfies the literal version requirement.

The review explicitly rejected describing those installations as compliant with the original dependency pin.

### Proposed Resolution

The review proposed:

- Preserve the frozen `requirements.txt`.
- Preserve the original application source.
- Preserve existing source hashes.
- Avoid installing additional dependencies.
- Use the installed system Python.
- Validate the exact installed cryptographic versions.
- Record the version difference as an explicit runtime exception.

The exception was limited to the designated host environments.

It was not a general claim that every cryptography version between 41 and 49 was supported.

## 4. Source Compatibility Review

The review examined all six shipped Python modules:

```text
md001.py
observe.py

runtime/artifact.py
runtime/hub.py
runtime/routes.py
runtime/wire.py
```

The frozen runtime components were checked against the existing runtime lock.

The application bundle's 17 content hashes were also checked against its original application manifest.

### Cryptographic API Surface

The application used established Ed25519 and serialization APIs.

| Operation | API |
|---|---|
| Key generation | `Ed25519PrivateKey.generate` |
| Public-key access | `public_key` |
| Signing | `sign` |
| Verification | `verify` |
| Private-key loading | `load_pem_private_key` |
| Private-key serialization | `private_bytes` |
| Public-key serialization | `public_bytes` |
| Public-key reconstruction | `Ed25519PublicKey.from_public_bytes` |
| Signature failure | `InvalidSignature` |

The review found these APIs available in the candidate cryptography versions.

### Standard-Library Dependencies

The application also used Python standard-library functionality for:

- JSON canonicalization.
- UTF-8 encoding.
- Base64 encoding.
- SHA-256 hashing.
- UUID generation.
- HTTP requests and responses.
- Socket handling.
- Threading.
- Argument parsing.
- File and directory operations.
- Timestamps.
- IP address handling.

No Python 3.14-specific language feature was identified in the reviewed source.

### Excluded Dependencies

The reviewed application did not require:

- X.509 certificate parsing.
- PKCS12.
- TLS certificate validation.
- New cryptography 49-only algorithms.
- Additional Rust build tooling.
- New convenience serialization APIs.

These findings supported the proposed compatibility exception.

They did not establish successful execution on the Linux hosts.

## 5. Proposed System-Python Runtime

The revised procedure specified:

```sh
/usr/bin/python3 -B -E -s
```

The options were intended to provide a controlled execution environment.

| Option | Purpose |
|---|---|
| `-B` | Prevent writing Python bytecode cache files |
| `-E` | Ignore Python environment variables |
| `-s` | Exclude the user site-packages directory |

The procedure required confirmation of the actual interpreter and imported cryptography module.

### Required Host Information

Each host validation was required to capture:

- Python version.
- Python executable path.
- Operating system.
- Architecture.
- Distribution package version.
- Distribution package status.
- Imported cryptography version.
- Cryptography module path.
- Cryptographic backend OpenSSL version.
- Application source hashes.

The review distinguished the distribution package version from the Python module's reported version.

An installed distribution package was not considered sufficient evidence that the selected interpreter could import it.

## 6. Deterministic Cryptographic Fixture

The review includes:

```text
FIXTURE.json
```

The fixture contains a deliberately public synthetic Ed25519 seed.

Its recorded seed is:

```text
000102030405060708090a0b0c0d0e0f101112131415161718191a1b1c1d1e1f
```

The fixture also contains:

- A fixed artifact identifier.
- A canonical signed assertion.
- The expected signature.
- A public trust mapping.
- A Base64-encoded artifact.

### Fixed Artifact Identifier

```text
00000000-0000-4000-8000-000000000001
```

### Producer

```text
DOMAIN_A
```

### Event

```text
LOCAL_SORT_V1
```

### Outcome

```text
SUCCESS
```

The fixture was generated using the frozen artifact implementation under the desktop cryptography 49 environment.

### Purpose

Each candidate host was required to:

1. Import its installed cryptography package.
2. Load the synthetic fixture.
3. Reconstruct the expected key material.
4. Produce the same canonical signed bytes.
5. Reproduce the expected deterministic Ed25519 signature.
6. Verify the original signature.
7. Reject a modified assertion.

This tests interoperability of the exact artifact and cryptographic operations used by MD001.

It does not establish general cryptographic security.

### Fixture Integrity

The recorded SHA-256 of `FIXTURE.json` is:

```text
44626cc7efe10c27626471b20f25eaae7afb6c0627bcd5e5fe079d4f7781fc3e
```

The fixture is public test material.

It is not a deployment signing credential.

## 7. Desktop Runtime Validation

Two desktop runtime-probe results are preserved.

### Initial Desktop Probe

```text
local_validation/desktop49/RESULTS.json
```

Recorded environment:

| Property | Value |
|---|---|
| Operating system | Windows 11 |
| Architecture | AMD64 |
| Python | 3.14.3 |
| Cryptography | 49.0.0 |
| Cryptographic OpenSSL | 4.0.1 |
| Passed | 18 |
| Failed | 0 |

Recorded status:

```text
PROBE_PASS_NOT_SCORED
```

### Final Desktop Probe

```text
local_validation/desktop49_final/RESULTS.json
```

The final probe also recorded:

```text
18 PASS
0 FAIL
```

The final result additionally preserved cryptography package and native binding identities.

### Final Cryptography Module Hash

```text
9ad86e52b4dde0544e0a9518ad322a863cfab3a4fd763019ad5ee7675a0c9b6a
```

### Final Native Binding Hash

```text
813b101f70efb79c388239ce82ac891e195a1e19eeaeb43c32d9bf425e7b51b8
```

These hashes identify the desktop cryptography components observed during validation.

They are not Linux package identities.

## 8. Desktop Probe Checks

The desktop runtime probe recorded 18 successful checks.

| Check | Result |
|---|---|
| Frozen application hashes | PASS |
| Fixture hash | PASS |
| Application imports and runtime lock | PASS |
| Configuration parsers | PASS |
| PEM/PKCS8 private-key loading | PASS |
| Raw public-key round trip | PASS |
| Ed25519 generation, signing, verification | PASS |
| Deterministic artifact and signature reproduction | PASS |
| Desktop fixture signature acceptance | PASS |
| Modified-signature rejection | PASS |
| Unknown-key rejection | PASS |
| Producer/key mismatch rejection | PASS |
| Malformed-artifact rejection | PASS |
| Repeated fresh verification without history | PASS |
| Canonical ordering independence | PASS |
| Frozen HTTP framing and observation | PASS |
| Unique artifact identifiers | PASS |
| Application source unchanged | PASS |

The recorded execution mode was:

```text
NON_SCORED_NO_NETWORK_NO_SERVICE_RUNTIME_PROBE
```

The desktop result recorded:

```text
requirement_pin_satisfied = true
```

That value applies to the desktop cryptography 49 environment.

It does not apply to the Linux compatibility candidates.

## 9. Proposed Linux Host Validation

The review defined separate runtime profiles for the three Linux hosts.

### Dell

```text
Python:       3.12.3
Cryptography: 41.0.7
Architecture: x86_64
```

### HP

```text
Python:       3.12.3
Cryptography: 41.0.7
Architecture: x86_64
```

### Raspberry Pi

```text
Python:       3.13.5
Cryptography: 43.0.0
Architecture: aarch64
```

The original review required 20 successful checks on each host.

The required result was:

```text
PROBE_PASS_NOT_SCORED
```

Because the Linux cryptography versions differed from the frozen pin, the expected result included:

```text
requirement_pin_satisfied = false
```

That field was not to be concealed or reinterpreted.

### Subsequent Host Evidence

The later MD001 supporting evidence preserves successful runtime probes for the Raspberry Pi and HP environments.

The recorded results were:

| Host profile | Passed | Failed |
|---|---:|---:|
| Raspberry Pi | 20 | 0 |
| HP | 20 | 0 |

Both recorded:

```text
PROBE_PASS_NOT_SCORED
```

Both also retained:

```text
requirement_pin_satisfied = false
```

These later results provide actual Linux runtime observations beyond the original desktop-only review.

They do not convert the original dependency versions into literal compliance with `cryptography==49.0.0`.

See:

```text
../../evidence/support/SUPPORT_EXPORT_20261119_231556/
```

## 10. Proposed Deployment Procedure

The review includes:

```text
COMMANDS.md
PROPOSED_COMMANDS.ps1
```

The PowerShell procedure was designed to stage and validate the application one host at a time.

The original order was:

1. Dell staging.
2. Dell validation.
3. Raspberry Pi staging.
4. Raspberry Pi validation.
5. HP staging.
6. HP validation.

The procedure required review of each host result before continuing.

### Preservation Requirements

The revised procedure prohibited:

- Overwriting existing application directories.
- Deleting previous evidence.
- Modifying the frozen source.
- Modifying `requirements.txt`.
- Reusing failed virtual environments.
- Unapproved package installation.
- Unapproved firewall changes.
- Unapproved DNS or routing changes.
- Automatic service startup.

The procedure was designed to stop when an expected file, version, or integrity condition did not match.

### Runtime Probe Restrictions

The probe was designed not to:

- Open network sockets.
- Start application services.
- Submit assertions.
- Change firewall rules.
- Modify the frozen application.
- Execute scored experiments.

It generated separate review evidence.

## 11. Runtime Review Versus Physical Preflight

The review explicitly separated runtime compatibility from network behavior.

### Runtime Probe

The runtime probe evaluated:

- Application integrity.
- Imports.
- Cryptographic operations.
- Canonical serialization.
- Trust binding.
- Selected malformed-input rejection.
- Configuration parsing.
- HTTP framing utilities.

### Physical Preflight

The later physical preflight required:

- Actual service startup.
- Correct socket bindings.
- Correct host routing.
- Relay forwarding.
- Domain B ingress behavior.
- Verifier response.
- Independent packet observation.
- Artifact byte equality.
- Positive and negative verification behavior.

Passing the runtime probe did not establish those physical-network properties.

The preflight evidence is preserved separately.

## 12. Source Integrity

The review includes:

```text
APPROVED_APP_FILES.json
```

This file records the approved SHA-256 identities of 17 application files.

The reviewed files include:

```text
COMMANDS.md
README.md
RUNTIME_LOCK.json
TEST_PLAN.md
VALIDATION.md
X01.md

configs/ingress.json
configs/ingress_N01.json
configs/relay.json
configs/verifier.json

md001.py
observe.py
requirements.txt

runtime/artifact.py
runtime/hub.py
runtime/routes.py
runtime/wire.py
```

The original review required those identities to remain unchanged.

The review did not authorize source modifications to accommodate older cryptography versions.

### Review Archive

The runtime review archive is:

```text
MD001_RUNTIME_REVIEW_R1.tar.gz
```

Its recorded SHA-256 digest is:

```text
dfaf9ab847048c5185d148fbf9227e6406486cb37793e5589923644aa3a0fdc7
```

The digest is preserved in:

```text
REVIEW_BUNDLE_SHA256.txt
```

### Verify the Review Archive

On Linux, from this directory:

```sh
sha256sum -c REVIEW_BUNDLE_SHA256.txt
```

The expected result is:

```text
MD001_RUNTIME_REVIEW_R1.tar.gz: OK
```

The review-file inventory is preserved separately in:

```text
REVIEW_FILES_SHA256SUMS.txt
```

These records establish file identities.

They do not independently establish application correctness or deployment success.

## 13. Independent Evidence Review

A reviewer can inspect the historical runtime review without executing the application.

### Step 1 — Review the Compatibility Finding

Inspect:

```text
REVIEW.md
```

Confirm the original finding:

```text
SOURCE_API_COMPATIBLE_CANDIDATES_HOST_VALIDATION_PENDING
```

### Step 2 — Review the Proposed Exception

Confirm that the original frozen dependency was retained:

```text
cryptography==49.0.0
```

Confirm that the Linux versions were treated as explicit exceptions rather than satisfying the literal requirement.

### Step 3 — Verify the Fixture

Inspect:

```text
FIXTURE.json
FIXTURE_SHA256.txt
```

Confirm the fixture identity and public-test classification.

### Step 4 — Review Desktop Validation

Inspect:

```text
local_validation/desktop49/RESULTS.json
local_validation/desktop49_final/RESULTS.json
```

Confirm:

```text
passed = 18
failed = 0
status = PROBE_PASS_NOT_SCORED
```

### Step 5 — Review Application Identities

Inspect:

```text
APPROVED_APP_FILES.json
```

Compare the recorded hashes against the frozen application package.

### Step 6 — Review Subsequent Host Results

Inspect:

```text
../../evidence/support/SUPPORT_EXPORT_20261119_231556/
```

Compare the recorded host versions and runtime-probe results against the original proposed profiles.

### Step 7 — Review Physical Preflight Separately

Inspect:

```text
../../evidence/support/PREFLIGHT_EXPORT_20261119_213249/

../../evidence/support/NEGATIVE_PREFLIGHT_20261119_221616/
```

These directories preserve subsequent network and verification observations.

They are not part of the original desktop runtime review.

## 14. Relationship to Scored Experiments

The runtime review was one stage in the MD001 preparation sequence.

| Stage | Purpose | Classification |
|---|---|---|
| Original desktop implementation | Establish assertion and verification behavior | Non-scored |
| Deployment package | Prepare physical application deployment | Non-scored |
| Runtime review | Evaluate installed Linux compatibility | Non-scored |
| Linux host probes | Validate selected installed runtime environments | Non-scored |
| Physical preflight | Confirm network transport and verification | Non-scored |
| B01 | Valid assertion verification | Scored |
| N01 | Modified assertion rejection | Scored |
| B02 | Producer-unavailable verification | Scored |

The runtime review supports confidence in the application environment.

It is not independent evidence that the scored experiments succeeded.

The scored-run directories remain the primary sources for those results.

## 15. Scope and Limitations

The runtime review supports the following findings:

- The reviewed source did not require an identified cryptography 49-exclusive API.
- The frozen application remained unchanged.
- The original dependency pin remained unchanged.
- The desktop cryptography 49 environment passed 18 defined checks.
- A deterministic synthetic fixture was preserved.
- Exact Linux runtime profiles were defined.
- Subsequent Raspberry Pi and HP probes passed their recorded checks.
- The Linux probes did not satisfy the original literal dependency pin.

The review does not establish:

- General compatibility across arbitrary cryptography versions.
- Production support for older dependency versions.
- Successful execution under every Linux configuration.
- Complete security of the cryptographic implementation.
- Physical-network forwarding.
- Firewall isolation.
- Physical producer shutdown.
- Replay prevention.
- Durable authorization consumption.
- Physical execution enforcement.
- Resistance to signing-key compromise.

The original review's pending-host-validation status must be interpreted as a historical status.

The later host probes provide additional evidence without rewriting the original review.

## 16. Conclusion

The MD001 runtime review addressed a concrete deployment compatibility problem without modifying the frozen application.

It distinguished the original cryptography 49 dependency requirement from the installed Linux runtime profiles.

The desktop review completed with:

```text
18 PASS
0 FAIL
```

Subsequent Linux supporting evidence recorded:

```text
Raspberry Pi: 20 PASS / 0 FAIL
HP:           20 PASS / 0 FAIL
```

The Linux results remained explicitly classified as non-scored and did not satisfy the original literal dependency pin.

The preserved source hashes, deterministic fixture, runtime reports, and review manifests support independent inspection of the compatibility decision.

The later physical-network experiments provide separate evidence of the application's deployed verification behavior.
