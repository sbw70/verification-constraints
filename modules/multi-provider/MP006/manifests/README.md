# MP006 — Build Manifests

## Purpose

This directory preserves the original MP006 build inventories and their accompanying documentation.

These records establish historical source and dependency identities. They are separate from the evidence generated during the physical power-loss experiment.

## Directory Structure

| Directory | Contents |
|---|---|
| [original/](original/) | Archived build inventories and original local-build documentation |

## Archived Manifests

The [original directory](original/) contains three files.

### SHA256SUMS.txt

[View original inventory](original/SHA256SUMS.txt)

The initial build inventory contains 56 SHA-256 entries.

It covers the original MP006 implementation, supporting documentation, configuration, local validation artifacts, and frozen MP005 dependencies.

### DEPLOYMENT_SHA256SUMS.txt

[View deployment inventory](original/DEPLOYMENT_SHA256SUMS.txt)

The later deployment inventory contains 57 SHA-256 entries.

Compared with the initial inventory:

- The MP006 configuration hash changed.
- The original root-level `SHA256SUMS.txt` was added to the inventory.
- The other 55 common entries retained their recorded hashes.

**Recorded deployment configuration SHA-256:**

`d7b4be8a0b42fed64f7ca2a17fc412280a84d7ea20d2421c0c786873756a63ea`

This hash matches the configuration identity recorded in the published R01 operator authorization.

### README.md

[View original build documentation](original/README.md)

Preserves the original implementation handoff and operating constraints.

Its local-build status statements reflect the time the document was written.

They are historical and do not supersede the subsequently recorded MP006-R01 experiment.

## Manifest Scope

Both inventories use paths relative to the original MP006 build root.

They were preserved under `manifests/original/` without rewriting their historical contents.

Consequently, verification requires the corresponding original file layout.

The deployment inventory references a root-level `SHA256SUMS.txt` that is not present at the current published MP006 root.

The original root README has also changed from the historical inventoried version.

A direct checksum check against the current repository may therefore report missing or changed files.

Such differences must be evaluated against the historical build rather than automatically classified as corruption of the original experiment.

Do not alter the archived inventories to force verification to pass.

## Frozen MP005 Dependencies

The archived inventories contain SHA-256 identities for the copied MP005 reference files.

The original implementation documentation identifies their source as commit:

`73713f6e9ed9c95251cc69ec88ef816cab771ac0`

The MP005 reference is retained as a dependency, not as a separate MP006 implementation.

Historical MP005 code, keys, configuration records, and documentation must remain distinguishable from MP006-specific source and evidence.

## Separation From Experiment Evidence

The completed physical power-loss experiment has its own evidence inventory:

[MP006-R01 SHA256SUMS.txt](../evidence/MP006_R01_RUN001/R01/SHA256SUMS.txt)

That inventory covers 79 original scored evidence files.

The archived build manifests do not replace it.

Likewise, documentation added after the experiment is not part of the original scored inventory.

## Preservation Rules

- Preserve archived manifest bytes and recorded hashes.
- Do not regenerate historical inventories after documentation changes.
- Do not modify frozen MP005 dependencies to satisfy a checksum.
- Do not treat historical local-build status as the current experiment result.
- Keep source-build verification separate from experiment-evidence verification.

## Navigation

- [Original build inventories](original/)
- [MP006 configuration](../configs/)
- [MP006 operator authorization](../authorizations/)
- [MP006 experiment evidence](../evidence/)
- [MP006 root](../)
