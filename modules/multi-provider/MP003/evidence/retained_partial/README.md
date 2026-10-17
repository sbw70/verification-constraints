# Retained Partial Campaign

This directory preserves the first MP003 scored attempt, session `MP003_SCORED_20261015`, unchanged.

It is not the scored MP003 result. The scored campaign is `../scored/` (session `MP003_SCORED_20261015_R2`). This directory is retained so the published record shows what happened before that campaign started, including operator errors.

## Summary

The first attempt ran one legitimate B01 control case. After that, provider state was mistakenly classified as pre-run contamination, the providers were reset, and the campaign was restarted as R2. No C01, C02, C03, or B02 case was run in this session.

Nothing in this directory is a property failure.

## Contents

- `PRE_RUN_MISFIRE_ASSOCIATION_WINDOW1.jsonl` — a short association log from the recorder accidentally being started in the wrong terminal window.
- `association.jsonl` — the association log for the first attempt.
- `B01_CONTROL/` — request, authorization packages, and post-B01 provider state for the first attempt's B01.

| File | SHA-256 |
|---|---|
| `PRE_RUN_MISFIRE_ASSOCIATION_WINDOW1.jsonl` | `e111618058e94219effb902d3b0c018e2eb64ce6923dd7d9069520a71d7ef34d` |
| `association.jsonl` | `4ded9a4a28fae61683bca34c292a4b79629c37923c029bbde7d9c996ad8195c5` |
| `B01_CONTROL/request.json` | `882a7d207f5b1ab04754204d7cef48050a22ac6dc718d407313fe6d28b3187a3` |
| `B01_CONTROL/provider_a_authorization.json` | `29b302f7e6f6a451957a62dd87e91a94512079735959b7848b27df1db5b6bcfe` |
| `B01_CONTROL/provider_a_authorization.json.b64` | `75ab641251bd1519827f096cbd717a426871a8993f7c5852bddfc3c13945046c` |
| `B01_CONTROL/provider_a_execution_after_B01.jsonl` | `74252f1809f9d4269b51c67277e59ed40d82ee6302c2496a31cde84c2aa3f948` |
| `B01_CONTROL/provider_a_spent_state_after_B01.json` | `399a1f28ca63dcdae18f0d0b23d19a1f117b44460914da9bc7b63e0cb443924d` |
| `B01_CONTROL/provider_b_authorization.json` | `7f09c6367787940fbf8c4e2a03220861b33573caa5b803c45b224bec7683b29e` |
| `B01_CONTROL/provider_b_authorization.json.b64` | `a68ca56df520471d9d60c0e257fa72c5810e7c3976d958296114cb73f81a6894` |
| `B01_CONTROL/provider_b_execution_after_B01.jsonl` | `d129e2779e9360497bc421fa840f65883ae626c0258e1fe80458656411c0320c` |
| `B01_CONTROL/provider_b_spent_state_after_B01.json` | `fdf42a4072bd5d8b46e31cef020d1dc022f245a94b70c28fc62a9105e3c3d1c5` |

This directory has no `SHA256SUMS.txt` of its own. The hashes above were computed from the retained files at publication.

## Sequence of events

Times are operator-local (UTC−4) unless noted.

1. **Recorder started in the wrong window.** The association recorder was started in Window 1 instead of Window 2 and stopped before any scored traffic. `PRE_RUN_MISFIRE_ASSOCIATION_WINDOW1.jsonl` contains only `SESSION_START` (19:02:36 UTC) and `SESSION_END` with `submission_count` 0 (19:06:08 UTC). Its hash chain verifies. Its `SESSION_START` carries the locked contract and manifest hashes.

2. **First-attempt session started.** `association.jsonl` begins with `SESSION_START` at 19:09:23 UTC, carrying the same locked contract and manifest hashes.

3. **B01 executed.** At 20:35:24 UTC both providers executed B01. Records 2–5 are Provider A `START`/`COMPLETE` and Provider B `START`/`COMPLETE`.

   - Request: `{"action":"mp003_test","nonce":"MP003-B01"}`, representation `882a7d20…`, context `CTX_MP003_B01`.
   - Operation ID: `d54eb3b904fd…`.
   - Provider A authorization: `a6fd6f0495346baea8f728120be4da655b9e3a1653666a4e6793e797e8f1e2e4`.
   - Provider B authorization: `52d0874f009fda1833d940530848969a642266a1ba7565c534b2e71e8fbdf25f`.

   This was a legitimate B01. It used the same request bytes and context later reused in R2, so it shares R2 B01's request representation and operation ID. Its authorizations are different because each mint generates a fresh nonce.

4. **State misclassified (21:52).** During a later state-cleanliness check, each provider was found to hold one execution and one spent authorization. These were initially recorded as pre-run residual state. That classification was wrong: they were this session's B01 results.

5. **Provider reset (22:00).** Provider spent state was reset and execution logs were removed before any C case. The first reset command produced malformed JSON because quoting was stripped across PowerShell/SSH. The files were then rewritten correctly using base64 transport. Provider state copies named `*_before_reset` are preserved in `../pre_run_state/`; their file timestamps (16:54–16:56) are earlier than this reset entry — see that directory's README.

6. **Reconstruction (22:18).** The operator reconciled the "residual" state against this session's B01 and corrected the classification in the operator notes. The `*_after_B01` files in `B01_CONTROL/` are that recovered state. Their JSON content is identical to the files in `../pre_run_state/`, but they are not byte-identical: each `pre_run_state` copy has 1–2 extra trailing bytes (a line ending added during capture), so their SHA-256 values differ.

7. **Restart as R2 (22:27).** Because provider state had been reset mid-session, this attempt was retained unchanged and a clean campaign was started as `MP003_SCORED_20261015_R2`.

## Open conditions recorded as-is

- **No `SESSION_END`.** `association.jsonl` ends at record 5. The first-attempt recorder was not stopped cleanly before the restart, so no `SESSION_END` or recorder-printed final hash exists for this session. The hash chain over records 1–5 verifies. Its last record hash is `15cf62abe288ee2e3392fbb660a86b68b901734bd08dff123c9ed0d43e9df6ef`.
- **Empty case folders.** The working copy of this directory also contained empty folders for C01, C02, C03, B02, and the final provider state, under two different naming schemes: `C01_A_AUTHORITY_AT_A`, `C01_COMPROMISED_A_TO_A`, `C02_A_AUTHORITY_TO_B`, `C02_PROVIDER_A_AUTH_TO_B`, `C03_B_LABEL_A_SIGNATURE`, `C03_CLAIM_B_SIGNED_BY_A`, `B02_PROVIDER_B_HEALTH`, `B02_POST_ATTACK_B_HEALTH`, `final_provider_a`, `final_provider_b`. They were empty because those cases never ran in this session. Git does not track empty directories, so they do not appear in the published repository.
- **No relay send record** exists for this B01.

## Interpretation

This directory contains operational history, not scored results:

- one valid B01 execution, consistent with R2's B01;
- one harmless recorder start in the wrong terminal;
- a state misclassification and reset that made a clean restart necessary.

None of it bears on the MP003 compromise property, because no compromised-key case ran here.

## Related evidence

Scored campaign:

`../scored/`

Provider state captured before the reset:

`../pre_run_state/`

Operator notes, including the original misclassification and its correction:

`../../operator/MP003_OPERATOR_NOTES.txt`

Narrative of the full campaign:

`../../PROVENANCE.md`
