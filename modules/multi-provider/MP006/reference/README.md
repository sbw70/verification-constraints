# MP006 — Frozen Reference Dependencies

## Purpose

This directory preserves the implementation dependencies inherited from MP005 and reused by MP006.

MP006 tests provider-controlled authority persistence across physical power interruption and host recovery.

Rather than implementing a new authorization or persistence mechanism, MP006 uses the previously validated MP005 provider implementation and verification functions.

The reference directory establishes implementation continuity between the experiments.

It is not a separate execution environment or evidence repository.

## Directory Structure

| Directory | Purpose |
|---|---|
| [MP005/](MP005/) | Frozen MP005 provider implementations, intermediary, association recorder, verification harness, configuration manifests, and supporting files |

The MP005 directory contains its own detailed documentation.

## Source Identity

**Reference source commit:**

`73713f6e9ed9c95251cc69ec88ef816cab771ac0`

The original MP006 build inventory identifies 48 unchanged MP005 reference files.

The original dependency identities are recorded in:

[Original Build SHA-256 Inventory](../manifests/original/SHA256SUMS.txt)

The historical inventory identifies the files included in the reviewed build.

Documentation added afterward is not retroactively included in that inventory.

### Provider A

MP006 uses the frozen MP005 Provider A implementation.

**SHA-256:**

`79e4994c955ca842af04a8fd650a33d49de040bab95b821ded9e63e16866f2b6`

The provider retains its existing:

- Authorization validation.
- Ed25519 signature verification.
- Durable consumption ledger.
- Spent-authority enforcement.
- Replay protection.
- Execution recording.
- Signed boundary signaling.

MP006 does not replace these mechanisms.

## Dependency Usage

The MP006 adapter is located at:

[mp006.py](../mp006.py)

It imports verification functions from:

- `MP005/harness/common.py`
- `MP005/harness/ledger_evidence.py`

It also loads the frozen Provider A implementation.

These dependencies support source verification, authorization preparation, persistent-state validation, signed boundary verification, and evidence scoring.

The adapter supplies MP006-specific configuration and persistent-state paths without changing provider authorization logic.

## Historical Reference Material

The frozen MP005 directory also preserves:

- Provider B implementation.
- NUVL intermediary.
- Association recorder.
- Laboratory cryptographic fixtures.
- Configuration and integrity manifests.
- Historical configuration revisions.
- R3 simulation and review source.
- The historical MP005 R3 scored-session authorization record.

These files establish the implementation context inherited by MP006.

The complete historical MP005 experiment remains in the original [MP005 project directory](../../MP005/).

The copied reference does not contain the entire historical MP005 evidence repository.

Historical authorization records do not authorize MP006 execution.

## Preservation Requirements

The reference dependencies must remain unchanged.

Do not:

1. Modify provider authorization or persistence algorithms.
2. Replace laboratory signing keys.
3. Alter historical configuration locks.
4. Disable source or harness integrity verification.
5. Execute archived MP005 simulation scripts inside this reference directory.
6. Use historical MP005 authorizations for new execution.
7. Write MP006 state or evidence into the frozen reference.
8. Repair verification failures by modifying frozen dependencies.

An implementation mismatch is a verification failure, not permission to change the expected source.

New documentation must remain distinguishable from the original frozen file inventory.

## Authority Boundaries

The reference implementation preserves independent provider authority.

Provider A and Provider B control their own authorization, consumption, and execution.

The NUVL intermediary transports provider-specific artifacts without acquiring execution authority.

The association recorder verifies and preserves signed boundary observations without authorizing execution.

The test harness evaluates evidence without overriding provider decisions.

These boundaries remain applicable when MP006 reuses the frozen implementation.

## Relationship to MP006 Evidence

The frozen reference establishes **which implementation was used**.

The MP006 evidence establishes **what happened during the experiment**.

These are separate requirements.

Source integrity alone does not demonstrate physical power-loss durability.

MP006-R01 recorded successful retention of consumed authority across the documented physical power interruption and recovery cycle.

That result is supported by its own persistent-state captures, process identities, signed boundary observations, and scoring records.

See:

[MP006 Results](../RESULTS.md)

[MP006 Provenance](../PROVENANCE.md)

[MP006-R01 Evidence](../evidence/MP006_R01_RUN001/)

## Scope

This directory provides frozen implementation dependencies.

It does not independently establish:

- Physical power-loss persistence.
- Correctness across every crash window.
- Full-history rollback resistance.
- Hardware execution attestation.
- Security against arbitrary host compromise.

Those properties require separately defined experiments and evidence.

## Related Documentation

- [Frozen MP005 Reference](MP005/README.md)
- [MP006 Main README](../README.md)
- [MP006 Source Review](../SOURCE_REVIEW.md)
- [MP006 Configuration](../configs/)
- [MP006 Original Manifests](../manifests/)
- [MP006 Results](../RESULTS.md)
- [MP006 Provenance](../PROVENANCE.md)
