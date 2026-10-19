# MP004 Configuration

This directory contains the locked test definition, fixed source inventory, run expectations, publication comparison, and implementation identity used by MP004.

These files define what was tested and what inputs were permitted to influence the scored result.

## Contents

### `MP004_CONTRACT.md`

Locked MP004 contract, revision 1.0.

It defines the claim under test:

**An independent offline verifier can authenticate preserved provider boundary events and evaluate the specified evidence assertions from raw signed packages and pinned provider trust material without using recorder classifications as verification inputs.**

The contract also fixes:

- the provider boundary-event schema;
- canonical JSON rules;
- Ed25519 signature input;
- provider-specific trust mapping;
- allowed denial reasons;
- source-selection rules;
- separation between cryptographic, trust, contextual, and interpretation results;
- the B01 and N01–N05 scored matrix;
- falsification conditions;
- required output files;
- explicit claim boundaries.

The contract distinguishes provider-produced evidence, recorder storage, and later interpretation.

Verification is evidentiary only and cannot create or enlarge provider authority.

### `MP004_SOURCE_MANIFEST.json`

Locked inventory of the MP003 source subset used by MP004.

It fixes 111 selected files by:

- relative path;
- byte length;
- SHA-256.

The inventory includes the preserved association log, provider trust material, MP003 configuration, scored evidence, and supporting source documentation needed by the MP004 verifier.

It also records that all 67 entries in the preserved MP003 scored checksum inventory were verified.

### `MP004_PUBLICATION_COMPARISON.json`

Records the comparison between the selected local MP003 source material and the published MP003 repository state at commit:

`fa541618b1a3bc58700a81b29129b17b35b1e0fc`

All 111 selected files matched the published Git blob identities.

This establishes that MP004's fixed source set corresponds to that published MP003 revision.

### `MP004_RUN_MANIFEST.json`

Locked pre-implementation input manifest for the scored campaign.

It fixes:

- the expected 17 provider `SUBMISSION` records;
- the raw provider-package SHA-256 for each record;
- the 15 records requiring contextual campaign assertions;
- source request and authorization paths;
- verification contexts;
- expected provider identities;
- expected lifecycle stages and denial reasons;
- expected bindings and operation IDs;
- expected authorization IDs and nonces;
- required case IDs;
- negative-fixture recipes and source records;
- output and source paths used by the verifier.

Records 2 and 3 are deliberately scoped as:

`authentication_only_retained_misfire`

They remain part of cryptographic coverage but are not treated as scored MP003 campaign outcomes.

Records 4 through 18 are checked for both authentication and their fixed campaign assertions.

### `MP004_LOCK_SHA256SUMS.txt`

SHA-256 lock file for the four pre-implementation definition files:

- `MP004_CONTRACT.md`
- `MP004_SOURCE_MANIFEST.json`
- `MP004_PUBLICATION_COMPARISON.json`
- `MP004_RUN_MANIFEST.json`

The verifier checks these hashes before evaluating the scored evidence.

This prevents later modification of the frozen test definition from silently changing the meaning of the run.

### `MP004_IMPLEMENTATION_MANIFEST.json`

Pre-scoring implementation identity recorded after verifier implementation and preflight validation.

It fixes:

- scored verifier SHA-256;
- original supplementary test-suite SHA-256;
- `cryptography` version;
- generated fixture-manifest SHA-256;
- confirmation that the frozen input definition remained unchanged.

Recorded verifier SHA-256:

`452111ef7b7f96e2f42d14a416605ba53ee5b878b3dc05ce2729f6dc9db096c7`

Recorded original test-suite SHA-256:

`3af53cc8caf1a71d12e0cb62f4c02afb008eb771468723192a70401c53ec72a3`

Recorded fixture-manifest SHA-256:

`8c79dd7812c73964bfe38c5ab527f63364996b85bf0a18971bc28b6243e423e6`

## Lock sequence

MP004 separates the test-definition lock from the implementation lock.

The pre-implementation files define:

- what source evidence is allowed;
- what records are examined;
- what outcomes are expected;
- how negative fixtures are constructed;
- what constitutes PASS, FAIL, or INCOMPLETE.

The implementation manifest then identifies the verifier and supplementary test suite that were used after that definition had been frozen.

This prevents the implementation from silently redefining the scored property after seeing the result.

## Fixed source coverage

The run manifest expects exactly:

- 19 total records in the preserved MP003 association log;
- 17 provider `SUBMISSION` records;
- record sequence numbers 2 through 18;
- 15 records with campaign-context assertions.

The two retained harness-misfire denials are authenticated but deliberately excluded from contextual success assertions.

No provider submission is silently discarded.

## Trust definition

The contract independently pins the provider boundary-key identities.

Provider A:

`sha256:e4664ee3b7bb0012fb7d8f763c9df74594d8a6bec8488d97532a5846cc04b6ff`

Provider B:

`sha256:db764408aa319642363057d804f0c2a3d2c7dd22de86ae4a6d6549cb97f60225`

The verifier derives these identifiers from the raw Ed25519 public keys.

Recorder metadata and event-supplied paths cannot substitute another provider's key.

## Scored cases fixed by the contract

The locked matrix contains seven required outcomes:

| Case | Fixed purpose |
|---|---|
| B01 | Authenticate all preserved provider packages and validate the 15 fixed campaign assertions |
| N01 | Detect modification of a signed event field |
| N02 | Detect modification of the provider signature |
| N03 | Reject the wrong provider trust anchor |
| N04 | Contradict a false unsigned summary with authenticated provider evidence |
| N05a | Ignore false-negative recorder classification |
| N05b | Ignore false-positive recorder classification |

Expected rejection is a PASS for the applicable negative case.

A tampered artifact being accepted would fail the case.

## Historical status fields

`MP004_RUN_MANIFEST.json` remains labeled:

`LOCKED_PRE_IMPLEMENTATION`

That describes when the file was frozen.

It is not a statement that implementation or scoring never occurred.

Likewise, statements in the locked contract describing verifier implementation or scoring as not yet performed record the state at contract freeze.

Later implementation identity and scored results are recorded separately in:

- `MP004_IMPLEMENTATION_MANIFEST.json`
- `../evidence/scored/`

The locked files are preserved rather than rewritten after the result.

## Path provenance

Some locked files contain absolute laboratory paths.

Those paths record the environment in which the test definition was prepared.

They are not required paths for reproduction from the published MP004 tree.

The publication-portable verifier workflow uses the repository-relative structure documented under `../verifier/`.

## Evidence meaning

This directory fixes the boundary around the MP004 experiment.

It shows:

- which historical MP003 bytes were accepted as source evidence;
- which provider trust material was authoritative for verification;
- which records and contextual assertions were mandatory;
- which negative transformations were required;
- what implementation was used for scoring.

The scored result should be interpreted against these locked definitions, not against later summaries or recorder classifications.

## Limits

These configuration files do not themselves prove that a scored case passed.

That evidence is under:

`../evidence/scored/`

They also do not establish:

- physical execution;
- evidence completeness;
- immutable storage;
- global chronology;
- independent issuance-signature verification;
- association hash-chain verification as part of the scored claim;
- authority for the verifier or association layer.

They define the test. They do not enlarge what the resulting evidence can prove.
