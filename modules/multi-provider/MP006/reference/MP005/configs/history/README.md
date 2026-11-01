# MP005 — Historical Configuration Records

## Purpose

This directory preserves earlier MP005 configuration locks retained within the frozen MP006 reference dependencies.

Each subdirectory represents a distinct historical configuration.

These records establish which contract, run manifest, and integrity identities applied to the corresponding MP005 campaign.

They are not interchangeable with the final R3 configuration.

## Directory Structure

| Directory | Purpose |
|---|---|
| [MP005_REHEARSAL_LOCK_20261025/](MP005_REHEARSAL_LOCK_20261025/) | Historical rehearsal configuration |
| [MP005_SCORED_20261025_R2/](MP005_SCORED_20261025_R2/) | Subsequent scored-session configuration |

Each directory contains:

- `MP005_CONTRACT.md`
- `MP005_RUN_MANIFEST.json`
- `MP005_LOCK_SHA256SUMS.txt`
- `README.md`

## Configuration History

### Rehearsal Lock

[MP005_REHEARSAL_LOCK_20261025/](MP005_REHEARSAL_LOCK_20261025/)

Preserves the configuration associated with the earlier MP005 rehearsal.

The run manifest identifies separate rehearsal-state directories for Provider A and Provider B.

The contract defines the original restart-durability requirements and operator-controlled execution conditions.

### Scored R2 Lock

[MP005_SCORED_20261025_R2/](MP005_SCORED_20261025_R2/)

Preserves the scored-session revision.

The revised contract explicitly separates scored execution from earlier rehearsal state and evidence.

The run manifest identifies new scored-state directories for both providers.

The revision requires separate authorization and preservation of the existing rehearsal history.

## Integrity Comparison

Both historical locks contain five SHA-256 entries.

Comparing the rehearsal lock with the scored R2 lock:

| Configuration component | Changed |
|---|---|
| Contract | Yes |
| Run manifest | Yes |
| Source manifest | No |
| Harness manifest | No |
| Implementation manifest | No |

The unchanged manifest hashes establish continuity of the recorded source, harness, and implementation identities.

The changed contract and run manifest hashes distinguish the campaign configurations.

The subsequent R3 configuration also has different contract and run manifest identities.

## Historical Status

Both archived run manifests retain:

`LOCKED_LIVE_DEFINITION`

They also contain historical `NOT_RUN` fields.

These values describe the state recorded when the manifests were created.

They must not be retroactively changed to match later experimental outcomes.

Actual campaign results belong to the corresponding evidence records.

## Integrity Verification

The historical lock files use paths relative to the original MP005 root.

Only the contract, run manifest, and lock are stored directly in each historical directory.

The remaining referenced manifests reside in the surrounding MP005 configuration.

Verification must use the matching historical file versions.

Do not substitute the current R3 contract or run manifest when evaluating an earlier lock.

Adding README documentation does not alter the original configuration identities.

## Preservation Rules

- Preserve historical file bytes and SHA-256 values.
- Keep rehearsal, R2, and R3 configurations distinguishable.
- Do not rewrite historical status fields.
- Do not replace older contracts with newer revisions.
- Do not use historical authorization for another campaign.
- Do not execute archived deployment procedures.
- Do not modify frozen MP005 dependencies to accommodate MP006.

These files provide configuration provenance, not independent proof of execution.

## Relationship to MP006

MP006 retains the frozen MP005 reference for its provider implementation, verification functions, and supporting harness.

The historical configuration files remain available for source provenance.

MP006 uses its own reviewed configuration, operator authorization, persistent-state directories, and evidence.

The historical MP005 locks do not authorize MP006 execution.

## Related Documentation

- [MP005 configuration](../README.md)
- [MP005 reference root](../../)
- [MP006 configuration](../../../../configs/)
- [MP006 evidence](../../../../evidence/)
