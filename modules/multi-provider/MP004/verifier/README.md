# MP004 Independent Verifier

This directory contains the verifier used for MP004 and the supplementary tests that exercise its failure handling.

The verifier's role is evidentiary only.

It independently evaluates preserved provider boundary packages from MP003. It does not authorize execution, recreate provider authority, or rely on the association recorder to determine whether a provider signature is valid.

## Contents

### `verify_mp004.py`

The verifier used for the MP004 preflight and scored run.

It independently:

- loads the locked MP004 configuration and source inventory;
- verifies the fixed MP003 source files and scored checksum inventory;
- loads the pinned Provider A and Provider B boundary public keys;
- derives each provider key ID from the raw Ed25519 public key;
- decodes the preserved raw provider packages;
- validates the fixed package and event schema;
- reconstructs the canonical signed event bytes;
- verifies Ed25519 provider boundary signatures;
- derives request binding and operation identity where required by the scored manifest;
- evaluates the B01 and N01–N05 case matrix;
- compares independently derived results with recorder metadata only after verification;
- writes per-record, per-case, fixture, comparison, metadata, summary, and checksum outputs.

The verifier does not import or invoke the MP003 association recorder.

### `test_verify_mp004.py`

The original nine-test supplementary suite preserved from the MP004 implementation.

It uses the original laboratory root path and is retained unchanged.

The tests cover:

- successful verification without recorder metadata;
- rejection of unknown provider identity;
- rejection of boolean substitution for integer version `1`;
- detection of a signed Unicode-field change;
- rejection of duplicate JSON keys;
- rejection of non-finite JSON values;
- rejection of padded signature encoding;
- rejection of a swapped provider trust anchor;
- rejection of paths escaping the MP004 workspace.

### `test_verify_mp004_portable.py`

Publication-portable copy of the same nine-test suite.

The test bodies are unchanged. The only adaptation is that the MP004 root is derived from the test file's location instead of using the original absolute laboratory path.

This file supports reproduction from the published directory structure. It is not the test-suite file whose hash was locked before the scored run.

## Trust model

The verifier pins separate Ed25519 boundary identities for the two providers.

Provider A:

`sha256:e4664ee3b7bb0012fb7d8f763c9df74594d8a6bec8488d97532a5846cc04b6ff`

Provider B:

`sha256:db764408aa319642363057d804f0c2a3d2c7dd22de86ae4a6d6549cb97f60225`

Each key ID is recomputed from the raw 32-byte public key.

A provider event must identify the provider and key expected by that pinned mapping before its signature can be accepted.

Event-supplied identity and recorder metadata cannot select an alternate verification key.

## Signature verification

The provider boundary event is canonicalized as UTF-8 JSON with:

- keys sorted;
- separators `,` and `:`;
- Unicode preserved;
- non-finite numbers rejected.

The signature input is:

`NUVL-MP-BOUNDARY-v1|` followed by the canonical event bytes.

The signature must be canonical unpadded base64url and decode to exactly 64 bytes.

Successful verification establishes that the event was signed by the holder of the pinned provider boundary private key.

It does not independently establish the physical truth of the event's contents.

## Recorder independence

The association record contains recorder-generated fields including:

- `sig_valid`
- `registry_match`
- `verification_code`
- `claimed_*`

Those fields are not inputs to the provider-signature decision.

The verifier first derives its own schema, trust, cryptographic, and contextual result from the raw provider package and locked source material.

Only after that result is fixed are recorder classifications compared with it.

This separation is directly exercised by N05a and N05b.

## Running the published verifier

From the MP004 root:

```text
python -m pip install -r requirements.txt
python verifier/test_verify_mp004_portable.py
python verifier/verify_mp004.py --manifest configs/MP004_RUN_MANIFEST.json --output evidence/preflight/MY_FRESH_REPRODUCTION
```

The requested output directory must not already exist.

A fresh run verifies the locked source material, reconstructs the fixed fixtures, executes the complete seven-case matrix, and writes a new reproduction directory.

It does not alter or replace the preserved scored run.

## Output status

A completed verifier run reports one of three statuses:

- `PASS` — every required case produced its expected result.
- `FAIL` — the run completed, but at least one required case produced the wrong result.
- `INCOMPLETE` — required source, lock, coverage, or other preconditions prevented a valid scored result.

For runs that reach the report-producing portion of the verifier, the corresponding exit codes are:

- `0` — PASS
- `1` — FAIL
- `2` — INCOMPLETE

Argument-parsing errors, an already-existing output directory, or some filesystem failures can terminate before normal result files are written.

## Campaign scope

`verify_mp004.py` is intentionally tied to the locked MP004 campaign.

It expects:

- the fixed MP003 source selection;
- the fixed 19-record association log structure;
- 17 provider `SUBMISSION` records;
- the locked provider identities;
- the defined event schema and denial vocabulary;
- the fixed MP004 case matrix and fixture recipes.

It is not presented as a general verifier for arbitrary future evidence formats.

## Limits

The verifier does not:

- authenticate historical request transmission;
- independently verify provider authorization-issuance signatures;
- prove physical execution or physical non-execution;
- establish that all relevant evidence was emitted or delivered;
- verify immutable storage;
- score the association hash chain;
- establish global chronology or synchronized clocks;
- protect historical authenticity after compromise of a provider boundary-signing key.

Provider-produced evidence, recorder storage, and later interpretation remain separate layers.

Independent verification of a provider statement does not give the verifier, association, or transport path any provider execution authority.
