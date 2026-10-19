# MP004 — Independent Offline Re-verification

MP004 tests whether preserved provider boundary evidence can be authenticated and evaluated independently of the association recorder that originally stored and classified it.

Scored session:

`MP004_SCORED_20261018_R1`

Result:

**PASS**

All seven required cases produced their expected outcomes.

## Question under test

MP001–MP003 produced provider-signed boundary evidence while exercising multi-provider authority separation.

MP004 asks a different question:

**Can a later verifier determine what the providers actually signed without trusting the recorder's own verification result?**

The locked claim is:

> An independent offline verifier can authenticate preserved provider boundary events and evaluate the specified evidence assertions from raw signed packages and pinned provider trust material, without using recorder classifications as verification inputs.

The association remains a recorder of evidence.

The offline verifier remains an interpreter of evidence.

Neither is an execution authority.

## Result

The verifier processed all 17 provider `SUBMISSION` packages preserved in the MP003 scored association log.

All 17 authenticated under the independently pinned provider boundary keys.

Fifteen of those records belonged to the scored MP003 campaign and also satisfied their fixed contextual assertions.

The remaining two were signed `DENY auth_malformed` events from the retained MP003 harness misfire. They were included in cryptographic coverage but were not treated as successful MP003 campaign outcomes.

The scored negative matrix also passed:

| Case | Test | Result |
|---|---|---|
| B01 | Authenticate the preserved provider evidence and fixed campaign assertions | PASS |
| N01 | Modify a signed event field while retaining the original signature | PASS — rejected |
| N02 | Modify the provider signature while preserving the event | PASS — rejected |
| N03 | Verify a Provider A event using Provider B's trust anchor | PASS — rejected |
| N04 | Assert an unsigned false summary that Provider B executed C02 | PASS — contradicted by authenticated Provider B denial |
| N05a | Falsely label valid provider evidence invalid in recorder metadata | PASS — provider evidence remained valid |
| N05b | Falsely label tampered provider evidence valid in recorder metadata | PASS — provider evidence remained invalid |

For the negative cases, PASS means the expected rejection, disagreement, or contradiction occurred.

It does not mean the altered artifact was accepted.

## Evidence separation

MP004 preserves three distinct layers:

1. **Provider evidence** — the signed boundary package produced by a provider.
2. **Recorder evidence** — the association record that stores the package and adds fields such as `sig_valid`, `registry_match`, and `verification_code`.
3. **Later interpretation** — conclusions derived from the preserved evidence.

The verifier derives provider identity, schema validity, trust mapping, and signature validity from the raw provider package and pinned public key.

Only after that result is fixed does it compare its result with recorder-added classifications.

Recorder fields therefore do not determine whether a provider signature is valid.

N05a and N05b test this distinction directly.

## Provider-specific trust

MP004 uses separate Ed25519 boundary trust anchors for Provider A and Provider B.

Provider A key ID:

`sha256:e4664ee3b7bb0012fb7d8f763c9df74594d8a6bec8488d97532a5846cc04b6ff`

Provider B key ID:

`sha256:db764408aa319642363057d804f0c2a3d2c7dd22de86ae4a6d6549cb97f60225`

The verifier derives each key ID from the raw 32-byte public key.

Provider identity in the event does not permit one provider's key to substitute for another's.

N03 confirms that the unchanged Provider A package does not verify under Provider B's public key and that the normal trust loader refuses the swapped anchor.

## Relationship to MP003

MP004 uses preserved evidence from:

`MP003_SCORED_20261015_R2`

The selected MP003 source set contains 111 files and is fixed by `configs/MP004_SOURCE_MANIFEST.json`.

Those files were matched byte for byte against the published MP003 state at commit:

`fa541618b1a3bc58700a81b29129b17b35b1e0fc`

The verifier also checks all 67 entries in the preserved MP003 scored `SHA256SUMS.txt` before evaluating the case matrix.

MP004 does not rerun MP003.

It evaluates the evidence MP003 already produced.

## N04 interpretation boundary

N04 deliberately introduces an unsigned summary claiming that Provider B `EXECUTED` the MP003 C02 operation.

The preserved Provider B package for that operation independently authenticates as:

`DENY auth_provider_mismatch`

The supplied summary is therefore classified:

`contradicted_by_authenticated_denial`

That conclusion is intentionally narrow.

It establishes that the unsigned summary conflicts with the authenticated provider statement.

It does not convert a provider-signed denial into universal proof of physical non-execution.

## Repository structure

| Path | Role |
|---|---|
| `configs/` | Locked contract, source inventory, run definition, trust/source comparison, and implementation identity |
| `source/MP003/` | Fixed MP003 source evidence used by the verifier |
| `fixtures/` | Deliberately altered or misleading inputs for the negative cases |
| `verifier/` | MP004 verifier and supplementary tests |
| `evidence/preflight/` | Pre-scoring implementation validation |
| `evidence/scored/` | Authoritative MP004 scored run |
| `evidence/publication_check/` | Post-score reproduction and publication-integrity checks |
| `evidence/retained/` | Superseded test-definition material retained for provenance |
| `notes/` | Reproduction and publication notes relevant to interpretation |

Detailed README files within each directory describe the artifacts at that level.

## Reproduction

MP004 is an offline verification test.

It does not require the original providers, NUVL relay, association process, or other laboratory hosts to be running.

Python 3.10 or later is required. The scored run used Python 3.12.14 and `cryptography` 50.0.2.

From the MP004 directory:

    python -m pip install -r requirements.txt
    python verifier/test_verify_mp004_portable.py
    python verifier/verify_mp004.py --manifest configs/MP004_RUN_MANIFEST.json --output evidence/preflight/MY_FRESH_REPRODUCTION

The output directory must not already exist.

A fresh run:

- checks the locked MP004 definition;
- verifies the selected MP003 source bytes;
- verifies the MP003 scored checksum inventory;
- loads the pinned provider boundary keys;
- reconstructs the fixed negative fixtures;
- executes the seven-case matrix;
- writes per-record and per-case results.

A reproduction run does not replace or modify the preserved scored campaign.

## What MP004 establishes

For the preserved MP003 evidence examined here, MP004 demonstrates that:

- provider boundary signatures can be independently re-verified;
- provider-specific trust anchors remain distinct;
- modification of signed provider content is detectable;
- modification of a provider signature is detectable;
- recorder classifications are not required to determine cryptographic validity;
- recorder classifications cannot make invalid provider evidence valid or valid provider evidence invalid;
- later unsigned interpretation can be checked against authenticated provider statements.

This strengthens the evidence model established by the earlier multi-provider tests.

Provider authority remains provider-controlled.

NUVL may transport authority.

The association may preserve evidence.

A later verifier may authenticate and interpret that evidence.

None of those evidentiary functions creates, enlarges, transfers, or substitutes provider execution authority.

## Limits

MP004 does not establish:

- physical execution or physical non-execution;
- completeness of the historical evidence set;
- authentication of historical request transmission;
- independent verification of provider authorization-issuance signatures;
- immutable association storage;
- association hash-chain verification as part of the scored claim;
- global chronology or synchronized clocks;
- restart durability;
- crash or power-loss behavior;
- concurrent execution behavior;
- cross-provider atomicity;
- provider implementation diversity;
- resistance to compromise of a provider boundary-signing key or provider host.

A valid boundary signature authenticates the provider statement under the pinned key.

It does not, by itself, prove every real-world fact described by that statement.

See `RESULTS.md` for the scored outcome and `PROVENANCE.md` for source identity, preparation history, and evidence boundaries.
