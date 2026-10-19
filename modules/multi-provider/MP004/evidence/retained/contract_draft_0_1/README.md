# MP004 Retained Contract Draft 0.1

This directory preserves the superseded MP004 contract and source inventory from before the scored test definition was locked.

These files are retained as historical test-definition evidence. They are not the contract or source manifest used to score MP004.

## Contents

- `MP004_CONTRACT.md` — draft version 0.1 of the independent offline re-verification contract.
- `MP004_SOURCE_MANIFEST.json` — the corresponding draft inventory of the selected MP003 source material.

At this stage, the contract already defined the central MP004 property: independently authenticate preserved provider boundary evidence from raw signed packages and pinned provider trust material without treating association-recorder classifications as verification inputs.

The draft also defined the planned control and negative cases, including signed-field tampering, signature tampering, wrong trust anchors, false summaries, and deliberately incorrect recorder metadata.

## Why this draft was superseded

The draft source inventory identified the selected MP003 material and verified the existing 67-entry scored evidence manifest, but it had not yet established that the copied MP003 source matched a specific published repository revision.

That publication comparison was completed before the MP004 test definition was frozen.

The locked source inventory records the published MP003 revision as verified and the locked contract records that all 111 selected source files matched the published source byte for byte.

The authoritative MP004 test definition is therefore in:

- `../../../configs/MP004_CONTRACT.md`
- `../../../configs/MP004_SOURCE_MANIFEST.json`
- `../../../configs/MP004_RUN_MANIFEST.json`
- `../../../configs/MP004_LOCK_SHA256SUMS.txt`

## Evidence meaning

This directory shows that the test definition existed in draft form before the final source comparison and contract freeze.

It also preserves the distinction between a working test definition and the later locked definition actually used for implementation and scoring.

No scored MP004 result should be interpreted against the files in this directory.

## Limits

This directory does not contain scored evidence, verifier output, or a valid alternative scoring definition.

It does not establish the MP004 result independently of the locked contract and scored evidence.

The draft's statements about source-publication equivalence reflect its pre-freeze state and were superseded by the completed source comparison recorded in the locked configuration.
