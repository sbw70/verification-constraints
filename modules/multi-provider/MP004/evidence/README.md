# MP004 Evidence

This directory contains the evidence produced and retained for MP004 independent offline re-verification.

MP004 is an evidence-authentication test. It does not exercise provider execution authority directly. Its purpose is to determine whether preserved provider boundary evidence can be independently authenticated and evaluated without relying on the association recorder's own verification classifications.

## Directory structure

### `preflight/`

Contains the complete pre-scoring verification run and supplementary verifier tests.

The preflight exercised the same seven-case matrix later used for scoring and returned PASS.

It is implementation-preparation evidence, not the authoritative scored result.

### `scored/`

Contains the authoritative MP004 scored campaign:

`MP004_SCORED_20261018_R1`

All seven required cases passed.

This directory is the primary evidence source for the MP004 result.

### `publication_check/`

Contains post-score checks against the prepared publication tree.

These include:

- a full verifier replay;
- portable supplementary tests;
- publication-integrity auditing.

The staging replay reproduced the same seven expected case outcomes.

These checks demonstrate reproducibility of the prepared publication package. They are not a second scored campaign.

### `retained/`

Contains superseded preparation material preserved for provenance.

The retained contract draft predates the final source comparison and contract lock and was not used for scoring.

## Scored property

The scored MP004 result supports the following narrow statement:

**Preserved provider boundary evidence from MP003 could be independently authenticated and evaluated from raw signed packages and pinned provider trust material without relying on association-recorder verification classifications.**

The scored matrix tested:

- valid preserved provider evidence;
- signed-field tampering;
- signature tampering;
- wrong provider trust anchors;
- an unsigned false external summary;
- false-negative recorder metadata;
- false-positive recorder metadata.

All required outcomes occurred.

## Evidence layers

MP004 keeps three evidence layers distinct:

1. **Provider-produced evidence** — the signed boundary packages emitted by Provider A and Provider B.
2. **Recorder storage and classification** — the association records that preserved those packages and added fields such as `sig_valid`, `registry_match`, and `verification_code`.
3. **Later interpretation** — conclusions drawn from the preserved evidence, including the MP004 verifier's independent result.

The verifier derives cryptographic validity from the raw provider package and pinned provider public key before comparing that result with recorder metadata.

Recorder classifications are therefore comparison data, not verification authority.

## Source integrity

The MP004 runs checked:

- 111 selected files copied from the published MP003 source set;
- all 67 entries in the MP003 scored evidence checksum manifest.

Per-run `SHA256SUMS.txt` files provide integrity inventories for their respective run directories.

The publication-wide integrity inventory is maintained at the MP004 module root.

## Negative-case interpretation

A PASS on a negative case means the expected rejection, contradiction, or metadata disagreement occurred.

It does not mean the altered artifact was accepted.

Examples:

- N01 and N02 pass because signature verification fails as expected.
- N03 passes because the wrong provider trust anchor is rejected.
- N04 passes because the false summary conflicts with authenticated provider evidence.
- N05a and N05b pass because recorder metadata cannot override the verifier's independently derived result.

## What this evidence establishes

The evidence demonstrates that, for the preserved MP003 provider boundary packages used by MP004:

- provider signatures can be re-verified independently;
- provider-specific trust anchors remain distinct;
- signed tampering is detectable;
- recorder classifications are not required to derive cryptographic validity;
- unsupported later interpretation can be checked against authenticated provider evidence.

The verifier and association remain evidentiary components.

Neither creates, enlarges, transfers, or substitutes provider execution authority.

## Limits

This evidence does not establish:

- physical execution or physical non-execution;
- completeness of the historical evidence set;
- authentication of historical request transmission;
- independent verification of provider authorization-issuance signatures;
- immutable association storage;
- association hash-chain verification as part of the scored MP004 claim;
- global chronology or synchronized clocks;
- crash, restart, power-loss, or concurrency behavior;
- cross-provider atomicity;
- provider implementation diversity;
- resistance to compromise of a provider boundary-signing key.

A valid provider boundary signature authenticates the signed provider statement.

It does not, by itself, prove every real-world fact that statement describes.
