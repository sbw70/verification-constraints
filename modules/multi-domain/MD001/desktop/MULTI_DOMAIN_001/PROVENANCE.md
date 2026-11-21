# Provenance

Authority: operator's MD-001 R1 final desktop handoff, local build and offline
validation only. A byte-identical handoff copy is retained in `reference/`.
Source inventory was the first build task. Frozen sources and historical evidence
were read and selected files copied unchanged; original directories were not edited.
Only `MULTI_DOMAIN_001/` was created for this work.

`reference/SOURCE_INVENTORY.json` records source identities, including R4.3 baseline
hash comparisons. The checkout commit is the published reference identity, while the
older `fa541618...` in MP005's historical manifest identifies its MP003 baseline.
It is not substituted for the hardened reference checkout revision. MP006 has no
separate Git commit in this outer workspace. ESP and MP004 snapshots derive from the
same reference checkout; actual file hashes are retained rather than assumed clean.

`src/artifact.py:canonical_bytes` is copied unchanged from MP005 provider_a.py.
Its exact source match was checked without importing provider code. Signing and
signature verification use the same cryptography Ed25519 primitives and pattern,
with a new assertion-only schema/tag. All validation, transport launch adapters,
simulation orchestration, and MD-001 documents are new. Mechanical relay sources
are byte-identical copies, with no added signature logic or hashing.

Shared source does not imply shared execution or authorization state. No historical
provider private key is loaded by this baseline. Every run creates and retains its
own explicitly disposable test signing key and public trust configuration.
Keys, signed payload bytes, original and mutated envelopes, process identities,
responses and logs remain within that uniquely identified run.

Initial attempt `20261112T012548Z_f9d58244` is retained as failed infrastructure
history: Windows sandbox denied a loopback socket connection (WinError 10013).
It is not a failed cryptographic claim or a scored physical run. Subsequent approved
loopback access enabled actual local validation. No prior run was overwritten.
See COMPLETION.md for the final run after test refinements.

Run manifests exclude themselves. The package root SHA256SUMS.txt covers all other
files including nested run manifests; MANIFEST_SHA256.txt separately records its
digest to avoid self-reference. Future added run files require a new package manifest.
No manifest is a signature or an independent attestation.
