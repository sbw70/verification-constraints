# Pre-Run State

This directory contains four provider state files captured during pre-test setup, from the first MP003 attempt (`MP003_SCORED_20261015`).

They are retained as provenance for the provider reset that preceded the R2 scored campaign. They are not scored evidence.

## Contents

| File | Bytes | SHA-256 |
|---|---|---|
| `provider_a_execution_before_reset.jsonl` | 338 | `e7bbcb98ed79f775677cdb99e2deb8e5a7a35456e9a25919683c5556e1cd7f72` |
| `provider_a_spent_state_before_reset.json` | 137 | `3a3cb3b55a338583072364d2f0d4c6e3a93dd7e46768909eaf4582085ac78135` |
| `provider_b_execution_before_reset.jsonl` | 338 | `a01739f1c6ce183243ac6ef7e2686b6c41e7874649e01c6b222d8ec3d41a6fc0` |
| `provider_b_spent_state_before_reset.json` | 137 | `2a404880ce87ab86e3882fe65bd67dabd516e131f606939639a4a479b8b01bfc` |

## What they contain

Each provider holds exactly one execution record and one spent authorization:

- Provider A: authorization `a6fd6f0495346baea8f728120be4da655b9e3a1653666a4e6793e797e8f1e2e4`
- Provider B: authorization `52d0874f009fda1833d940530848969a642266a1ba7565c534b2e71e8fbdf25f`

These are the first attempt's B01 authorizations (see `../retained_partial/`). The state reflects that B01, not contamination from before MP003.

## Relationship to the retained B01 files

The JSON content of each file here is identical to the corresponding `*_after_B01` file in `../retained_partial/B01_CONTROL/`.

The bytes are not identical:

- Every file here ends in `CRLF` (`0d 0a`).
- The original provider files end in `LF` (execution logs) or have no trailing newline (spent state).

The extra 1–2 bytes come from capturing provider output through a Windows shell. As a result, these files have different SHA-256 values from the `*_after_B01` files.

The operator notes record two sets of hashes for this state, labeled "residual" and "recovered". Both sets match the `*_after_B01` files in `../retained_partial/B01_CONTROL/`, not the files in this directory.

## Timing

These files were captured during pre-test setup on 2026-10-15, after the first attempt's B01 and before the R2 scored campaign began. MP003 setup and pre-test work spanned more than one session, and the capture time has no bearing on any scored result.

## Interpretation

These files confirm that each provider held exactly one execution and one spent authorization after the first attempt's B01, and that this was the only provider activity in that attempt.

They have no bearing on the MP003 compromise property. No compromised-key case ran in the first attempt, and provider state was reset before R2 began. R2's starting state is documented in the operator notes: both providers had clean spent state and no execution log.

## Related evidence

`../retained_partial/`

`../scored/`

`../../operator/MP003_OPERATOR_NOTES.txt`
