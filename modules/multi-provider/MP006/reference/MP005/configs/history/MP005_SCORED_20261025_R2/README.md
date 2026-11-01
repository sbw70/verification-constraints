# MP005 — Historical Scored R2 Configuration

## Purpose

This directory preserves the MP005 scored-session configuration revision dated October 25, 2026.

It records the transition from the earlier rehearsal configuration to a separately authorized scored campaign.

These files are historical MP005 dependencies retained within MP006's frozen reference.

They do not authorize new execution.

## Directory Contents

| File | Purpose |
|---|---|
| [MP005_CONTRACT.md](MP005_CONTRACT.md) | Scored-session contract, deployment correction, acceptance criteria, and limitations |
| [MP005_RUN_MANIFEST.json](MP005_RUN_MANIFEST.json) | Historical scored configuration, provider paths, cases, and status |
| [MP005_LOCK_SHA256SUMS.txt](MP005_LOCK_SHA256SUMS.txt) | SHA-256 integrity lock for the R2 configuration |

## Scored-Session Correction

The contract contains a superseding section:

**MP005 scored-session deployment correction (superseding lock)**

This correction separates scored execution from the earlier physical rehearsal.

The revised provider state directories are:

**Provider A:**

`/home/seth/MULTI_PROVIDER_005/live_state/scored/provider_a`

**Provider B:**

`/home/seth/MULTI_PROVIDER_005/live_state/scored/provider_b`

The previous rehearsal state and evidence remain separate.

The correction requires new session authorization, fresh state directories, and a separate association-recorder history.

It does not authorize execution or report a successful scored campaign.

## Recorded Test Cases

| Case | Provider | Objective |
|---|---|---|
| `R01_PROVIDER_A_RESTART_DURABILITY` | Provider A | Consumption persistence, restart, replay rejection, and fresh execution |
| `R02_PROVIDER_B_RESTART_DURABILITY` | Provider B | Same properties under Provider B |

The historical run manifest retains `NOT_RUN` status fields.

These are configuration-time records, not an independent determination of subsequent campaign results.

Actual outcomes must be established from the corresponding scored evidence.

## Configuration Integrity

[MP005_LOCK_SHA256SUMS.txt](MP005_LOCK_SHA256SUMS.txt) records five configuration identities.

Compared with the preceding rehearsal lock:

| Component | R2 comparison |
|---|---|
| Contract | Changed |
| Run manifest | Changed |
| Source manifest | Unchanged |
| Harness manifest | Unchanged |
| Implementation manifest | Unchanged |

**R2 contract SHA-256:**

`aa04ff6c437acafb8d8dfd63918f44a68ee4c9b843392c455fa17e6bbba4487d`

**R2 run manifest SHA-256:**

`664ab2724df066f1405fcd579590f8745dee83314745db021bc76d6aecd1da3c`

The integrity lock uses paths relative to the original MP005 root.

Only three historical files are stored directly in this directory. The remaining referenced manifests belong to the surrounding MP005 configuration.

Do not substitute later R3 files when verifying the historical R2 configuration.

## Authority Boundaries

The configuration identifies the intended experiment and deployment environment.

It does not originate provider authority.

Provider A and Provider B independently validate authorization, record consumption, and control execution.

The intermediary and association recorder do not obtain execution authority from these manifests.

The historical contract requires exact replay rejection without additional consumption or execution.

## Historical Limitations

The R2 contract addresses durability across an idle forced process restart.

It does not establish:

- Physical power-loss durability.
- Host reboot persistence.
- Concurrent double-spend resistance.
- Crash-window correctness.
- Resistance to rollback of the complete persistent history.
- Physical hardware execution.

The R3 simulation results referenced in the manifest remain supporting offline characterization, not additional scored R2 live tests.

## Preservation Rules

- Preserve the original contract, manifest, and lock bytes.
- Do not rewrite historical `NOT_RUN` fields.
- Do not replace R2 configuration with subsequent R3 revisions.
- Do not reuse historical operator authorization.
- Do not modify frozen MP005 dependencies.
- Do not regenerate historical hashes.

This README is additional documentation and is not part of the original configuration lock.

## Related Documentation

- [Previous rehearsal configuration](../MP005_REHEARSAL_LOCK_20261025/)
- [Configuration history](../)
- [MP005 configuration](../../README.md)
- [MP006 reference dependencies](../../../)
