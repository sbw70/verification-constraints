# MP004 Preserved Source Evidence

This directory contains the fixed MP003 source material used by MP004 for independent offline re-verification.

MP004 does not recreate the MP003 campaign. It re-evaluates preserved evidence from that campaign.

## Contents

### `MP003/`

This directory contains the 111 selected MP003 files pinned by:

`../configs/MP004_SOURCE_MANIFEST.json`

The selected material includes:

- MP003 top-level documentation;
- locked MP003 configuration;
- the association provider registry;
- Provider A and Provider B boundary public keys;
- MP003 pre-run and preflight evidence;
- retained MP003 evidence;
- the complete selected MP003 scored evidence tree.

The source manifest records the relative path, byte length, and SHA-256 of every selected file.

## Source revision

The selected files were compared against the published MP003 repository state at commit:

`fa541618b1a3bc58700a81b29129b17b35b1e0fc`

The locked MP004 source comparison records all 111 selected files as matching that published revision byte for byte.

This fixes the historical source basis used by MP004.

## Source material used directly by the verifier

The verifier uses the preserved MP003 association log as the source of provider boundary packages:

`MP003/evidence/scored/association.jsonl`

The scored association log contains 19 total records.

MP004 evaluates the 17 `SUBMISSION` records, sequence numbers 2 through 18.

Records 1 and 19 are association session records and are not provider boundary submissions.

The verifier also uses fixed MP003 campaign artifacts identified by the locked MP004 run manifest to derive contextual expectations for the scored campaign records.

## Provider trust material

The preserved trust material includes separate Ed25519 boundary public keys for:

- `PROVIDER_A`
- `PROVIDER_B`

Only the public boundary keys are needed for MP004 signature verification.

The verifier independently derives each key identifier from the raw 32-byte public key and checks it against the provider-specific pinned value.

The association recorder's own trust decision is not used as the verifier's trust decision.

## MP003 scored integrity inventory

The preserved MP003 scored directory contains its original:

`evidence/scored/SHA256SUMS.txt`

MP004 verifies all 67 entries in that inventory before evaluating the case matrix.

This is separate from the MP004 source manifest:

- the MP004 source manifest fixes the selected source tree used by MP004;
- the MP003 scored checksum file verifies the integrity relationships already published inside the selected MP003 scored evidence.

## Immutability within MP004

Files under `source/MP003/` are inputs to MP004.

They are not fixture-generation targets.

All deliberately altered negative-case material is written under:

`../fixtures/`

This keeps preserved historical source evidence separate from synthetic MP004 test inputs.

## Scope of the copied source

`source/MP003/` is the selected source subset fixed for MP004.

It is not presented as a complete duplicate of every implementation file in the original MP003 module.

Some preserved MP003 documentation therefore refers to implementation paths outside this selected subset. Those documents remain unchanged because they are part of the published source context.

The original MP003 module remains the authoritative location for its complete implementation and publication structure.

## Evidence meaning

This directory fixes what historical material MP004 was allowed to examine.

It supports reproducibility of the MP004 result by tying the verifier to specific preserved MP003 bytes rather than to a moving repository state.

The source tree itself does not create a new provider event or a new execution claim.

MP004 authenticates and interprets the provider evidence already preserved here.

## Limits

Preserving and hashing this source material does not establish:

- that every historically relevant event was emitted or delivered;
- immutable storage at the time of the MP003 campaign;
- physical execution;
- global chronology;
- independent authentication of historical request transmission;
- independent verification of provider authorization-issuance signatures.

The source tree fixes the evidence examined by MP004. It does not expand what that evidence can prove.
