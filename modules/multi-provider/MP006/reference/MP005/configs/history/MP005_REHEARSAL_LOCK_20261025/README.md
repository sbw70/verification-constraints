# MP005 — Historical Rehearsal Configuration Lock

## Purpose

This directory preserves the MP005 rehearsal configuration locked on October 25, 2026.

The files document an earlier configuration of the multi-provider restart-durability experiment.

They are retained within MP006's frozen MP005 reference dependencies for historical identification and verification.

They do not authorize new execution.

## Directory Contents

| File | Purpose |
|---|---|
| [MP005_CONTRACT.md](MP005_CONTRACT.md) | Historical experimental contract, acceptance criteria, deployment assumptions, and limitations |
| [MP005_RUN_MANIFEST.json](MP005_RUN_MANIFEST.json) | Historical session configuration, provider paths, test cases, and recorded status |
| [MP005_LOCK_SHA256SUMS.txt](MP005_LOCK_SHA256SUMS.txt) | Original configuration integrity lock |

## Historical Experiment

The contract defines provider-controlled authorization consumption across an idle forced process restart.

The intended verification sequence includes:

1. Consume valid provider-issued authority.
2. Record consumption in a durable hash-linked ledger.
3. Terminate the provider while idle.
4. Restart the same implementation using the existing persistent state.
5. Reject exact replay without additional execution.
6. Accept and execute separate fresh authority.

The original contract identifies two scored targets:

- `R01_PROVIDER_A_RESTART_DURABILITY`
- `R02_PROVIDER_B_RESTART_DURABILITY`

These are historical MP005 case identifiers, not MP006-R01 cases.

## Recorded Status

The run manifest records:

**Status:** `LOCKED_LIVE_DEFINITION`

It also retains:

- `live_rehearsal_status: NOT_RUN`
- `scored_status: NOT_RUN`

These fields describe the manifest's recorded state.

They must not be interpreted as the final disposition of subsequent MP005 campaigns.

Historical configuration records are not rewritten to reflect later results.

## Configuration Integrity

[MP005_LOCK_SHA256SUMS.txt](MP005_LOCK_SHA256SUMS.txt) preserves five SHA-256 identities:

- MP005 contract.
- Source manifest.
- Harness manifest.
- Implementation manifest.
- Run manifest.

The lock uses paths relative to the original MP005 root.

Only the contract, run manifest, and lock file are preserved directly in this historical directory.

The other referenced configuration files are located in the surrounding frozen MP005 reference.

Do not regenerate the lock or substitute later configuration versions when evaluating historical identities.

## Scope and Limitations

The historical contract concerns process-restart durability.

It does not establish:

- Physical power-loss persistence.
- Host reboot durability.
- Crash-window correctness.
- Concurrent double-spend resistance.
- Protection against rollback of the entire persistent history.
- Physical hardware execution.

Offline simulation results described in the manifest are supporting characterization, not additional scored live cases.

The locked addresses and paths are historical laboratory configuration values.

They are not deployment instructions.

## Preservation Rules

- Preserve all original file bytes.
- Do not change historical status fields.
- Do not modify recorded hashes.
- Do not replace these files with later R2 or R3 configurations.
- Do not execute historical launch procedures from this directory.
- Do not modify frozen MP005 dependencies to accommodate MP006.

Adding this README does not change the historical configuration lock.

## Related Documentation

- [Parent configuration history](../)
- [MP005 configuration documentation](../../README.md)
- [Historical scored R2 configuration](../MP005_SCORED_20261025_R2/)
- [MP006 reference dependencies](../../../)
