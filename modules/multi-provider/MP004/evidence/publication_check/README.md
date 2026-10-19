# MP004 Publication Verification

This directory contains post-score checks performed against the prepared MP004 publication tree.

These checks test whether the published package preserves the scored verifier, selected source material, fixtures, locked configuration, and reproducible case behavior. They are not a second scored campaign and do not expand the MP004 claim.

## Contents

### `MP004_STAGING_REPLAY_20261018_R1/`

A full replay of the MP004 verifier from the prepared publication tree.

The replay used the same locked run manifest and verifier implementation as the scored campaign and returned:

**PASS**

All seven defined cases reproduced their expected outcomes:

| Case | Expected property | Replay result |
|---|---|---|
| B01 | Authentic preserved provider evidence verifies | PASS |
| N01 | Signed-field tamper is rejected | PASS |
| N02 | Signature tamper is rejected | PASS |
| N03 | Wrong provider trust anchor is rejected | PASS |
| N04 | False summary is contradicted by authenticated provider evidence | PASS |
| N05a | Valid evidence remains valid despite false-negative recorder metadata | PASS |
| N05b | Tampered evidence remains invalid despite false-positive recorder metadata | PASS |

The replay also rechecked all 111 selected MP003 source files and all 67 entries in the MP003 scored checksum manifest.

### `portable_tests.txt`

Transcript of the nine supplementary verifier tests executed from the publication layout.

All nine passed.

The portable test copy changes only the test suite's root-path assignment so the same checks can run from the published directory structure. The verifier logic and scored semantics are unchanged.

### `publication_audit.json`

Machine-readable audit of the prepared publication tree.

The recorded audit passed checks covering:

- 144 copied files preserved unchanged;
- 86 nested checksum entries verified;
- four frozen lock hashes verified;
- six fixture hashes verified;
- scored verifier unchanged;
- original test suite unchanged;
- nine portable tests passed;
- full staging replay passed;
- no Python cache artifacts present.

## Evidence meaning

These artifacts show that packaging MP004 for publication did not change the verifier or alter the behavior of the scored case matrix.

The full replay independently reproduced the same expected distinctions demonstrated by the scored run: provider signatures remained verifiable from preserved raw evidence, signed tampering and wrong trust anchors were rejected, false summaries could not override authenticated provider evidence, and recorder classifications did not determine cryptographic validity.

This is reproduction and publication-integrity evidence. The authoritative MP004 result remains the original scored campaign under `../scored/`.

## What these checks do not establish

A successful publication replay does not create a second independent historical observation of the MP003 provider activity. It re-evaluates the same preserved source evidence using the published verifier and fixed inputs.

These checks do not establish:

- physical execution or physical non-execution;
- completeness of the historical evidence set;
- immutable storage;
- global chronology;
- independent verification of provider authorization-issuance signatures;
- historical request transmission;
- any execution authority for the verifier or association layer.

The verifier remains evidentiary only. Re-verification cannot originate, enlarge, or substitute provider authority.
