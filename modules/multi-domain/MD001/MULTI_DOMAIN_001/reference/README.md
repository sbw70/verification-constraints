# MD001 — Historical Source References

This directory contains source snapshots retained during development of the MD001 desktop baseline.

The snapshots document which earlier implementations were inspected, which components were reused, and which security boundaries were deliberately kept separate.

These are historical reference materials, not a collection of additional MD001 experiments.

## Reference inventory

| Directory | Source project | MD001 relationship |
|---|---|---|
| `MH001_R43/` | MULTI_HUB_001 R4.3 | Mechanical forwarding implementation reused |
| `MP005/` | Multi-provider authority persistence | Canonical encoding and cryptographic implementation patterns reviewed |
| `MP004/` | Earlier multi-provider verification | Design and verification reference |
| `MP006/` | Provider power-loss persistence | Evidence and validation conventions reviewed |
| `ESP_LOCAL_008/` | Signed endpoint directionality | Physical execution-boundary reference for a possible extension |

The directory also contains:

| File | Purpose |
|---|---|
| `SOURCE_INVENTORY.json` | Original source paths, retained paths, sizes, SHA-256 hashes, and available baseline comparisons |
| `MD001_R1_HANDOFF.txt` | Original operator-to-desktop implementation handoff |

## Source identity

`SOURCE_INVENTORY.json` identifies the MP005 reference checkout using commit:

```text
73713f6e9ed9c95251cc69ec88ef816cab771ac0
```

It also identifies the MH001 baseline as R4.3.

The inventory records 34 source files and their SHA-256 identities.

The historical local MD001 workspace did not have a conventional committed HEAD at the time of preparation. Its local source identity was therefore recorded using content hashes rather than an invented Git commit.

## Executed source reuse

The desktop baseline reuses the following MH001 modules:

- `MH001_R43/hub.py`
- `MH001_R43/wire.py`
- `MH001_R43/routes.py`

These implement mechanical forwarding, HTTP transport handling, and static route validation.

The baseline also copies the `canonical_bytes` function from the MP005 provider implementation without changing its function body.

Ed25519 signing and verification patterns were adapted for the new MD001 assertion format and domain-separation tag.

The complete MP005 provider authorization implementation was not imported into the MD001 verifier.

## Inspected but not executed

The MP004, MP006, and ESP-LOCAL-008 snapshots were retained for inspection and provenance.

They do not provide execution authority to MD001.

In particular, the MD001 assertion verifier does not import:

- Provider authorization-consumption logic.
- SPENT-state enforcement.
- Replay-denial ledgers.
- Endpoint firmware.
- Servo command clients.
- Physical execution handlers.

The presence of historical code in this directory does not mean that code participated in an MD001 test.

## Historical documentation

Several reference directories already contain their original READMEs, provenance records, source reviews, or manifests.

Those documents describe their respective source projects and historical test results.

They must not be interpreted as additional MD001 scored results.

For MD001's specific reuse decisions, consult:

[`../SOURCE_REUSE.md`](../SOURCE_REUSE.md)

For the original source-origin record, consult:

[`../PROVENANCE.md`](../PROVENANCE.md)

## Reference integrity

The retained snapshots were intended to preserve the original source bytes.

`SOURCE_INVENTORY.json` records each inventoried file's expected SHA-256 digest.

The desktop test harness checks retained reference files against the inventory and also checks the original source paths.

That second check depends on the original files being accessible at their recorded locations.

A public checkout may therefore contain the retained snapshots without satisfying every original-machine source-path check.

## Preservation rules

Do not:

- Edit retained reference source files.
- Replace original documentation with updated MD001 claims.
- Substitute new signing keys into historical fixtures.
- Remove the original handoff file.
- Rewrite historical source hashes or manifests.
- Execute historical deployment scripts as part of MD001 reproduction.

Any future adaptation should be implemented outside these retained reference snapshots and given its own source identity.

## Verification boundary

MD001 tests whether a signed assertion can be transported and independently verified without transferring verification authority to the intermediary.

The historical reference projects address related but distinct properties, including durable authorization consumption, provider independence, and endpoint-bound execution.

Those properties are not automatically inherited by MD001 merely because source files or implementation patterns were reused.

The MD001 result must be evaluated from MD001's own implementation and evidence.
