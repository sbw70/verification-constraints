# MD001 — Offline Test Harness

This directory contains the original MD001 desktop-baseline test harness.

`run_offline.py` orchestrates the producer, verifier, mechanical relay, observation adapters, and negative-test mutation adapter as separate local processes.

All network communication in this baseline uses loopback transport. This harness does not perform the later physical-network experiment.

## Requirements

- Python with local subprocess and loopback socket access.
- `cryptography==49.0.0`, as specified in the parent requirements file.
- The baseline source files and retained reference inventory.
- Access to the original source paths recorded in `reference/SOURCE_INVENTORY.json` for the full source-integrity checks.

The harness creates disposable Ed25519 test credentials for each run. No operational signing credentials are required.

## Run the baseline

From the outer MD001 experiment directory:

```sh
python -B MULTI_DOMAIN_001/tests/run_offline.py
```

The harness creates a new directory under:

```text
MULTI_DOMAIN_001/evidence/offline/<UTC_TIMESTAMP>_<RANDOM_ID>/
```

It does not overwrite an existing run directory.

A successful invocation returns exit code zero when all recorded checks pass. The resulting `RESULTS.json` is the authoritative record for that particular invocation.

## Test sequence

### B01 — Valid assertion delivery

The producer sorts `[9, 1, 4, 2]` and confirms the result `[1, 2, 4, 9]`.

It records completion and generates a signed `LOCAL_SORT_V1` assertion.

The harness sends the artifact through the frozen MH001 relay with external application-level observation taps.

It compares the artifact digest at the producer, relay-adjacent observations, and verifier ingress.

The verifier must accept the assertion after performing an Ed25519 signature check.

These observations use loopback application taps, not independent physical packet capture.

### N01 — Signed-field modification

The harness sends the original valid artifact through an unchanged relay to a separate mutation adapter.

The adapter changes `event.outcome` from `SUCCESS` to `FAILURE` without replacing the signature.

The verifier must reject the modified assertion with `invalid_signature`.

The harness also checks that the original and modified artifacts differ and that the original signature was retained.

### B02 — Producer unavailable, fresh verifier

The harness terminates the producer process and records an unsuccessful loopback connection attempt.

It terminates the original verifier and launches a new verifier process.

The original B01 artifact is sent through another relay instance to the new verifier.

The harness checks that:

- The producer is unavailable in the simulation.
- The verifier process identity has changed.
- The retained artifact reaches the new verifier unchanged.
- The new verifier accepts it after a fresh signature check.

A repeated submission is also tested to confirm another signature verification occurs.

This is a process-restart simulation, not physical power removal.

## Supporting checks

In addition to the three baseline scenarios, the harness checks:

- Valid and invalid Ed25519 signatures.
- Unknown signing keys and mismatched producer bindings.
- Malformed and noncanonical artifacts.
- Deterministic canonical encoding.
- Artifact identifier generation.
- Valid signatures that fail local event criteria.
- Verification without network or file access.
- Absence of execution-related imports in the verifier.
- Retained reference-source integrity.
- Relay observation consistency.
- Saved decision and response consistency.

These supporting checks do not constitute additional scored physical scenarios.

## Evidence output

Each run preserves a collection of files that includes:

| Evidence | Purpose |
|---|---|
| `RESULTS.json` | Individual checks, observed values, totals, and run status |
| `SHA256SUMS.txt` | SHA-256 inventory of files generated during the run |
| `build_identity.json` | Source and reference-inventory identities |
| `build_snapshot/` | Copies of the baseline source and requirements |
| `producer/` | Local operation and signed artifact |
| `test_keys/` | Disposable laboratory private key |
| `trust.json` | Locally provisioned public-key mapping |
| `trust_provisioning.json` | Public trust provisioning record |
| `B01-response.json` | Original verification response |
| `N01-response.json` | Modified-artifact rejection response |
| `B02-response.json` | Fresh-verifier response and process comparison |
| Process and adapter directories | Transport observations, decisions, and logs |

The harness also records Python, platform, and cryptography version information in its results.

A failed or interrupted attempt must remain distinguishable from a successful run.

## Recorded baseline

The original STOP 1 completion report identifies:

- Final run: `20261112T025926Z_4d05fe22`
- 21 PASS
- 0 FAIL
- Status: `MD001_LOCAL_BUILD_VALIDATED_NOT_DEPLOYED`

Those figures describe the historical desktop baseline, not a fresh invocation and not the later physical experiment.

The original completion report also preserves earlier attempts, including an infrastructure-blocked run.

See [`../COMPLETION.md`](../COMPLETION.md) for the historical totals, hashes, and limitations.

## Reproduction limitations

The harness requires access to original source locations for its full reference-integrity checks.

A standalone copy of the retained reference files may be sufficient for some implementation functions but does not satisfy every source-origin check performed by this harness.

Fresh runs generate new keys, identifiers, timestamps, process identities, and evidence hashes. These values are not expected to match the historical run.

The preserved historical evidence should not be edited to force a hash match.

## Security boundary

The harness tests verification of signed assertions, not authorization to execute an operation.

It does not establish physical host separation, power-loss persistence, replay-consumption enforcement, or production deployment security.

The later physical MD001 results must be assessed independently using their own scored evidence and provenance.
