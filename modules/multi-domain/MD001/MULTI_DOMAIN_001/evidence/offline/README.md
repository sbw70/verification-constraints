# MD001 — Offline Validation Evidence

This directory preserves the original MD001 desktop-baseline validation attempts.

The tests used separate local processes, loopback HTTP transport, Ed25519-signed assertions, and the frozen MH001 mechanical relay.

These results predate the physical MD001 experiment.

## Recorded runs

| Run directory | Recorded result | Classification |
|---|---|---|
| `20261112T012548Z_f9d58244/` | 1 PASS, 1 harness FAIL | Infrastructure-blocked attempt |
| `20261112T012609Z_1ff78364/` | 21 PASS, 0 FAIL | Earlier successful validation |
| `20261112T025926Z_4d05fe22/` | 21 PASS, 0 FAIL | Final selected baseline |

All three directories are retained.

The initial failed attempt was not replaced or concealed.

## Final baseline

The original STOP 1 completion report identifies:

`20261112T025926Z_4d05fe22/`

as the final selected run.

Its recorded status is:

`MD001_LOCAL_BUILD_VALIDATED_NOT_DEPLOYED`

The final run completed 21 supporting checks with no failures.

Three baseline scenarios were evaluated.

### B01 — Valid signed assertion

A producer completed a local sort operation and generated an Ed25519-signed assertion.

The artifact passed through a mechanical relay.

Application-level observations recorded matching artifact hashes at the producer, relay-adjacent taps, and verifier ingress.

The verifier accepted the assertion after checking its signature and locally provisioned trust binding.

### N01 — Modified signed assertion

A downstream adapter changed the signed outcome field without replacing the signature.

The verifier rejected the modified artifact with `invalid_signature`.

This tested whether modification of a signed assertion could be detected.

### B02 — Independent re-verification

The producer process was terminated.

The original verifier process was terminated and replaced with a new process.

The retained B01 artifact was delivered to the new verifier.

The new verifier accepted the artifact after performing a fresh Ed25519 signature check.

The same artifact was also accepted on a repeated submission.

This behavior is consistent with the baseline's intentionally stateless verification design.

It is not evidence of replay-consumption enforcement.

## Supporting checks

The remaining checks addressed:

- Signature validity and rejection.
- Producer/public-key trust binding.
- Malformed artifact rejection.
- Canonical JSON encoding.
- Artifact identifier generation.
- Local acceptance criteria.
- Absence of network and file dependencies in the verifier.
- Separation from execution-related imports.
- Source integrity.
- Evidence and response consistency.

These checks supplement B01, N01, and B02.

They do not expand the physical scored-test matrix.

## Evidence interpretation

The original harness recorded:

- Signed artifact bytes.
- Operation completion records.
- Disposable signing credentials.
- Public trust configuration.
- Process identities.
- Application-level transport observations.
- Verifier decisions.
- Mutation records.
- Source snapshots.
- SHA-256 manifests.

The loopback observations are not independent physical packet captures.

Terminating a producer process is not equivalent to disconnecting power from a separate physical host.

## Reproduction

The original test harness is located at:

[`../../tests/run_offline.py`](../../tests/run_offline.py)

From the outer MD001 directory:

```sh
python -B MULTI_DOMAIN_001/tests/run_offline.py
```

A fresh invocation creates a new evidence directory.

It does not reproduce historical timestamps, process identifiers, random signing keys, or artifact hashes.

The harness also requires access to original source paths for its complete source-integrity checks.

## Integrity

Each historical run has its own recorded evidence and manifest.

The original package-level manifest identifies the retained files.

Do not modify:

- Historical results.
- Original or modified artifacts.
- Disposable test credentials.
- Process observations.
- Source snapshots.
- Run manifests.
- Failed-attempt records.

New documentation belongs outside the historical run directories.

## Scope

The offline evidence establishes the recorded behavior of the desktop simulation.

It does not establish:

- Physical network isolation.
- Firewall enforcement.
- Physical producer power loss.
- Independent hardware execution.
- Durable authority consumption.
- Production readiness.

For the original completion report, see:

[`../../COMPLETION.md`](../../COMPLETION.md)

For source provenance, see:
[`../../PROVENANCE.md`](../../PROVENANCE.md)

For the later physical experiment, return to the outer MD001 directory.
