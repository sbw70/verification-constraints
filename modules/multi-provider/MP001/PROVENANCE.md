
# MP001 Provenance

This document records the origin, deployment, preparation, scored execution, and retained evidence state for MP001.

MP001 tested whether the multi-provider reference architecture retained provider-scoped authority separation when the principal roles were moved from a single Python process onto separate networked hosts.

The scored campaign was executed on 2026-10-09/10.

## Repository location

MP001 is published under:

`modules/multi-provider/MP001/`

The broader multi-provider module also contains the earlier single-process architectural reference.

MP001 is the physically separated-host implementation and evidence package.

## Tested topology

The frozen MP001 topology assigned the following roles.

### Coordinator / association

Host:

`Xer0trust`

IPv4:

`192.168.1.102`

Role:

- operator
- association recorder
- evidence collection

### NUVL intermediary

Host:

`nuvl-relay`

Hardware:

Raspberry Pi 3B+

IPv4:

`192.168.1.100`

Role:

stateless NUVL intermediary

### Provider A

Host:

`Xer0trust-3`

Hardware:

Dell Latitude E5450

IPv4:

`192.168.1.118`

Role:

independent Provider A

### Provider B

Host:

`Xer0trust2`

Hardware:

HP Laptop 14-dk1xxx

IPv4:

`192.168.1.106`

Role:

independent Provider B

### Requester / attacker

Hardware:

Chromebook

Role:

request generation and hostile-input generation

The retained environmental baseline is:

`evidence/MP001_PREDEPLOY_BASELINE.txt`

The frozen role assignment is:

`evidence/MP001_TOPOLOGY_FREEZE.txt`

## Authority separation

The implementation used separate provider-controlled authorization and execution state.

Provider A and Provider B had independent:

- authorization issuance keypairs
- boundary-signing keypairs
- authorization IDs
- authorization nonces
- spent state
- local execution logs
- runtime decision instances

The NUVL intermediary held no provider issuance private key and did not verify provider authorization.

The association held only provider boundary public keys for verification.

It did not possess provider authorization authority.

## Cryptographic contract

The normative MP001 contract is:

`configs/MP001_CONTRACT.md`

Scored contract SHA-256:

`7db3a52907af48d2524995e15b947600e534555758338cc38ce2594ff633ff4e`

The contract fixes:

- canonical JSON
- request representation
- verification context
- mechanical binding
- operation ID
- provider authorization construction
- authorization IDs
- Ed25519 authorization signatures
- provider validation order
- single-use behavior
- boundary-event representation
- boundary signatures
- association semantics

## Run manifest

The scored run definition is:

`configs/MP001_RUN_MANIFEST.json`

Final scored manifest SHA-256:

`37f2cea056bce67c209204467fa574c1d83307ec7e6df59815fb58eae20acf54`

The manifest preregistered:

- B01-B10 baseline cases
- N01 bad Provider A authorization
- N02 hostile relay mutation
- N03 forged boundary
- N04 duplicate boundary
- N05 one-provider-unavailable case
- N06 sequential authorization replay

It also explicitly excluded claims for:

- physical execution witness
- global cross-host clock authority
- implementation diversity
- crash-window replay persistence
- concurrent replay
- power-loss replay persistence

## Association recorder

Implementation:

`association/association_recorder.py`

Scored SHA-256:

`fad60dfc8df53337d2e41288c2c4973442258cae4240945ebbd0aa8920550bfc`

The recorder:

- preserved raw received boundary bytes
- hashed raw submissions
- verified provider boundary signatures
- retained malformed or invalid submissions
- detected exact signed-event duplicates
- chained local observation records
- remained non-authoritative for provider execution

## Provider registry

Registry:

`association/provider_registry.json`

Final scored SHA-256:

`59d739588427d87313e3434982d943a9c82bad26c3fe3deb7d5488efadb6088d`

The registry maps:

- `PROVIDER_A` to Provider A's boundary public key
- `PROVIDER_B` to Provider B's boundary public key

### Registry encoding correction

An earlier copy of `provider_registry.json` contained a UTF-8 byte-order mark.

That version produced SHA-256:

`49cb1204...`

The BOM was removed before scored execution.

The final locked registry hash is:

`59d739588427d87313e3434982d943a9c82bad26c3fe3deb7d5488efadb6088d`

Removing the BOM changed the file bytes and therefore its SHA-256.

It did not change:

- provider identities
- registered key IDs
- trusted public keys
- registry semantics

The final BOM-free registry was the version used for scored execution.

## Provider A implementation

Runtime:

`provider_a/provider_a.py`

Scored SHA-256:

`c875582b275f270b8e68af69ed4ee84896e83815cdf33b7d7c5ccc813fe2e606`

Authorization mint:

`provider_a/mint_authorization_a.py`

Scored SHA-256:

`1a485e8a5d3de854cb31303b8d3bf1339ef72cb9b42f308490bd02519e76d7ec`

Provider A authorization and boundary key material originated on the Provider A host.

Published laboratory key files are:

- `provider_a_issuance_private.pem`
- `provider_a_issuance_public.pem`
- `provider_a_private.pem`
- `provider_a_public.pem`

These are MP001 test keys retained for examination and reproducibility of the published laboratory run.

They are not production credentials.

## Provider B implementation

Runtime:

`provider_b/provider_b.py`

Scored SHA-256:

`7759ae8604515ef711ea8cde7b867c3b8faf19e26aedbd48c29d6099fd804fa1`

Authorization mint:

`provider_b/mint_authorization_b.py`

Scored SHA-256:

`1b3ba1314761a5489817c660cdc4d62e65ba77deae2bfce2fdce48c228f98deb`

Provider B authorization and boundary key material originated on the Provider B host.

Published laboratory key files are:

- `provider_b_issuance_private.pem`
- `provider_b_issuance_public.pem`
- `provider_b_private.pem`
- `provider_b_public.pem`

These are MP001 test keys retained for examination and reproducibility of the published laboratory run.

They are not production credentials.

## NUVL intermediary implementation

Implementation:

`intermediary/nuvl_multi_relay.py`

Scored SHA-256:

`09d458cc8e3e13706b5463deffea0e14fcd784011a629623a09b9bd5ee04d6f4`

The relay:

- hashed the opaque request bytes
- carried the verification context
- computed the non-secret mechanical binding
- selected the provider-specific authorization transport value
- forwarded Provider A and Provider B artifacts independently
- returned HTTP 204 without waiting for provider completion

It did not:

- possess provider issuance private keys
- validate provider authorization
- maintain provider spent state
- originate provider authority
- enlarge provider authority

## Pre-run evidence

Several preparation sessions are intentionally retained.

They are not part of the scored result.

### `PRE_RUN_ASSOC_SMOKE_001.jsonl`

Association recorder startup and clean-session smoke.

No provider submissions were recorded.

### `PRE_RUN_BOUNDARY_SMOKE_001.jsonl`

Early boundary-path attempt.

No provider submissions were recorded.

It is retained rather than removed from the preparation history.

### `PRE_RUN_BOUNDARY_SMOKE_002.jsonl`

Produced signed Provider A and Provider B `DENY auth_missing` boundary statements using an earlier recorder state.

This run exposed a recorder extraction issue that was corrected before scoring.

### `PRE_RUN_BOUNDARY_SMOKE_003.jsonl`

Repeated the missing-authorization boundary test using the final recorder and final run-manifest state.

Both provider denials verified successfully.

### `PRE_RUN_FULL_PATH_001/`

Successful end-to-end integration smoke before scoring.

It retained:

- request
- Provider A authorization
- Provider B authorization
- provider-local execution records
- provider spent state
- four valid association boundary submissions

This established that the complete deployed path was operating before the scored campaign began.

## Scored campaign

The scored campaign is retained under:

`evidence/MP001_SCORED_20261009/`

The campaign scorecard records:

- B01-B10 — PASS
- N01 — PASS
- N02 — PASS
- N03 — PASS
- N04 — PASS
- N05 initial attempt — RETAINED_MISFIRE
- N05 retry — PASS
- N06 — PASS
- SCORECARD_ASSERTIONS — PASS

The scored association session retained:

- 62 submissions
- 61 signature-valid submissions
- 1 signature-invalid submission
- 28 `START`
- 28 `COMPLETE`
- 6 `DENY`
- 33 Provider A submissions
- 29 Provider B submissions
- 1 duplicate

## N05 retained misfire

The initial N05 attempt was intended to test Provider A continuing while Provider B was unavailable.

The first attempt did not satisfy that precondition.

Provider B had not actually stopped.

During that attempt:

- Provider A executed
- Provider B consumed its authorization
- Provider B emitted `START`
- Provider B did not retain a corresponding execution record

The attempt was not deleted.

It is retained in the evidence and marked:

`N05_INITIAL_ATTEMPT=RETAINED_MISFIRE`

Provider B was then forcibly stopped and verified unavailable.

Fresh Provider A and Provider B authorizations were created.

The retry was executed as:

`N05_RETRY_001`

and passed the intended condition.

This retained history explains the final Provider B state:

- executions: 13
- spent authorizations: 14

Provider A finished with:

- executions: 14
- spent authorizations: 14

## Final provider-state hashes

Provider A execution log:

`9cd2b26247196d867f5b1fd8cca81aacff780a53f7f0885c352a14ed4f1edbf4`

Provider A spent state:

`88d2a5a6047a3748227ae71ade63a4531af81e2d2f291c8623ac928b8ea4c550`

Provider B execution log:

`da1eba172b0194c71d1ff81960e56be073c7c1c9b170a8bd5a85303c12c4769a`

Provider B spent state:

`84c79f21b91861c377645b85a411158b00bbb8809a097977228e6253ae1c4aab`

The values are retained in:

`evidence/MP001_SCORED_20261009/final_provider_hashes.txt`

## Association integrity

Final association record-chain hash:

`94f2b4985faf7b32eebb3acc356160f421bbc344848ccf3a139e0002fd6bc9f6`

SHA-256 of the retained scored `association.jsonl`:

`2b18fa2f54bc725e2511aca893887a68f44df942258d65e1185ad096e884c348`

These values are retained in:

- `association_final_record_hash.txt`
- `association_log_hash.txt`

## Scored evidence manifest

The scored campaign directory contains:

`SHA256SUMS.txt`

The manifest covers the frozen scored artifacts.

The manifest was verified after evidence collection before publication.

README files subsequently added for repository navigation and explanation are publication documentation, not original scored artifacts.

They are not retroactively part of the frozen evidence set.

## Frozen archive

The scored campaign was preserved as:

`evidence/MP001_SCORED_20261009_FINAL.tar`

Archive SHA-256:

`029cd08f6363ee694cb93f5ecfb83c37d447a1dec8d20b86bd1a09f752c562ca`

The value is retained in:

`evidence/MP001_SCORED_20261009_FINAL.tar.sha256`

The final archive hash was verified after creation.

## Evidence handling

Preparation artifacts, failed setup attempts, the N05 misfire, negative submissions, provider-local state, and association records were retained rather than normalized into a clean success-only history.

This distinction matters because MP001 separates:

- what was planned
- what was deployed
- what was observed
- what was scored
- what was excluded from the claim

The scored result should be evaluated from the retained evidence, not from the expected outcomes in the run manifest alone.

## Time semantics

MP001 records local UTC and local monotonic observations on multiple hosts.

Those values are useful for local evidence and troubleshooting.

They are not treated as a globally synchronized authoritative clock.

No MP001 result depends on proving exact cross-host chronology from those timestamps.

## Execution semantics

Provider `EXECUTED` and `COMPLETE` evidence in MP001 refers to software-local provider execution.

MP001 did not include an independent physical witness.

The campaign therefore does not claim independently witnessed physical consequence.

## Publication state

The repository includes the implementation, configuration, test key material, pre-run records, scored artifacts, integrity files, and explanatory documentation required to inspect the published MP001 experiment.

Later explanatory README, RESULTS, and PROVENANCE documentation describe the frozen evidence.

They do not alter the original scored artifacts or retroactively expand the MP001 claim.
