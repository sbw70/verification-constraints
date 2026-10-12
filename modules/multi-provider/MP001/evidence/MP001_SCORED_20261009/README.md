# MP001 Scored Campaign Evidence

This directory contains the retained artifacts from the MP001 scored campaign executed on 2026-10-09/10.

The campaign tested whether the multi-provider reference architecture retained provider-scoped authority separation when the intermediary, Provider A, Provider B, and the association were deployed as separate networked processes on separate hosts.

The association recorded provider boundary statements but did not authorize execution. Provider A and Provider B independently evaluated and consumed their own provider-issued authorizations.

The normative wire, authorization, validation, and boundary-signing rules are defined in:

`../../configs/MP001_CONTRACT.md`

The preregistered campaign cases are defined in:

`../../configs/MP001_RUN_MANIFEST.json`

## Campaign result

The retained scorecard reports:

- `B01-B10=PASS`
- `N01=PASS`
- `N02=PASS`
- `N03=PASS`
- `N04=PASS`
- `N05_INITIAL_ATTEMPT=RETAINED_MISFIRE`
- `N05_RETRY_001=PASS`
- `N06=PASS`
- `SCORECARD_ASSERTIONS=PASS`

See `MP001_SCORECARD.txt`.

## Baseline series: B01-B10

B01 through B10 exercised the ordinary valid multi-provider path.

Each case used:

- a distinct raw request body
- a Provider A authorization bound to that request
- a separate Provider B authorization bound to the same request
- verification context `CTX_ALPHA`

All ten requester submissions returned HTTP 204 from the intermediary.

Across the ten baseline cases:

- Provider A generated 10 `START` and 10 `COMPLETE` boundary statements
- Provider B generated 10 `START` and 10 `COMPLETE` boundary statements
- Provider A recorded 10 local executions
- Provider B recorded 10 local executions

The providers used separate authorization IDs, nonces, issuance keys, spent state, execution state, and boundary-signing keys.

The matching operation IDs used for correlation did not combine the providers' authority.

Relevant artifacts include:

- `requests/B01.json` through `requests/B10.json`
- `auth_a/B01_auth.json` through `auth_a/B10_auth.json`
- `auth_b/B01_auth.json` through `auth_b/B10_auth.json`
- `requester_baseline.log`
- `baseline_request_hashes.txt`
- `baseline_authorization_index.txt`
- `baseline_requests.tar`
- `B01_B10_auth_a.tar`
- `B01_B10_auth_b.tar`

## N01 — corrupted Provider A authorization signature

N01 supplied Provider A with a deliberately corrupted authorization signature while Provider B received its intact provider-specific authorization.

Observed behavior:

- Provider A denied with `auth_bad_sig`
- Provider B independently proceeded through `START` and `COMPLETE`
- the invalid Provider A authorization did not prevent Provider B from acting under Provider B's own valid authority

The directory retains both the original and corrupted Provider A authorization artifacts under `auth_a/`.

The requester record is:

`requester_N01.log`

## N02 — hostile relay request mutation

N02 tested a relay-side mutation that changed the request representation and recomputed the non-secret mechanical binding while retaining the original provider-issued authorizations.

The altered relay artifacts are:

- `N02_HOSTILE_RELAY_A.json`
- `N02_HOSTILE_RELAY_B.json`

Both providers independently rejected the altered request with:

`auth_request_mismatch`

Recomputing public binding material therefore did not create replacement Provider A or Provider B authority.

The original and tampered request bodies are retained under `requests/`.

## N03 — forged boundary submission

N03 tested association-side verification of a forged provider boundary package.

A Provider A boundary event was retained while its Ed25519 signature was altered.

The resulting artifact is:

`N03_FORGED_BOUNDARY.json`

The association:

- retained the submission
- matched the claimed provider to the registry
- rejected the signature as invalid
- did not convert the forged submission into an authentic Provider A statement

The requester-side association submission result is retained in:

`requester_N03.log`

This case concerns verification of provider boundary evidence by the association. It does not make the association an execution authority.

## N04 — duplicate valid boundary submission

N04 first completed an ordinary valid provider execution.

An exact previously accepted Provider A `COMPLETE` boundary package was then submitted to the association again.

The replayed package is retained as:

`N04_DUPLICATE_A_COMPLETE.json`

The duplicate remained cryptographically valid because its signed bytes were unchanged.

The association retained the second submission as a duplicate rather than treating it as a new distinct provider event.

The campaign recorded one duplicate.

Requester-side results are retained in:

`requester_N04.log`

## N05 — provider unavailability

The initial N05 attempt did not satisfy the intended Provider B unavailable precondition.

That attempt was retained rather than removed from the evidence.

During the initial attempt:

- Provider A produced `START` and `COMPLETE`
- Provider B was still running
- Provider B consumed its authorization and produced `START`
- the intended unavailability condition had therefore not been established

The scorecard records:

`N05_INITIAL_ATTEMPT=RETAINED_MISFIRE`

The initial requester record is:

`requester_N05.log`

A fresh authorization set was then created for `N05_RETRY_001` after Provider B unavailability was verified.

During the retry:

- Provider A independently produced `START`
- Provider A independently completed its local execution
- Provider A produced `COMPLETE`
- no Provider B boundary record was produced for the retry

The scorecard records:

`N05_RETRY_001=PASS`

The retry requester record is:

`requester_N05_RETRY_001.log`

The retained misfire explains the final Provider B difference between spent and execution counts.

## N06 — sequential authorization replay

N06 submitted the same intact Provider A and Provider B authorization pair twice.

On the first submission:

- Provider A accepted and executed
- Provider B accepted and executed

On the second submission:

- Provider A denied with `auth_spent`
- Provider B denied with `auth_spent`

The second submission therefore did not produce a second provider-local execution from either provider.

The requester record is:

`requester_N06.log`

MP001 tests ordinary sequential replay only. It does not claim to re-test crash-window, concurrent-contention, or power-loss persistence properties.

## Association record

The complete retained association observation log is:

`association.jsonl`

Final association counts are recorded in:

`association_final_counts.txt`

The retained counts are:

- submissions: 62
- signature valid: 61
- signature invalid: 1
- `START`: 28
- `COMPLETE`: 28
- `DENY`: 6
- Provider A submissions: 33
- Provider B submissions: 29
- duplicates: 1

Association ordering is local observation order.

Association timestamps or provider-local timestamps do not establish a globally synchronized chronology and are not authority inputs.

The final association record-chain value is:

`94f2b4985faf7b32eebb3acc356160f421bbc344848ccf3a139e0002fd6bc9f6`

It is retained in:

`association_final_record_hash.txt`

The SHA-256 of `association.jsonl` is:

`2b18fa2f54bc725e2511aca893887a68f44df942258d65e1185ad096e884c348`

It is retained in:

`association_log_hash.txt`

## Final provider state

Final Provider A state is retained under:

`final_provider_a/`

Provider A finished with:

- 14 local execution records
- 14 spent authorizations

Final Provider B state is retained under:

`final_provider_b/`

Provider B finished with:

- 13 local execution records
- 14 spent authorizations

The Provider B difference is preserved from the retained N05 initial misfire.

Hashes of the final provider state files are recorded in:

`final_provider_hashes.txt`

## Deployed implementation

`deployed_implementation_hashes.txt` records the SHA-256 values of the implementations deployed for the scored campaign:

- NUVL multi-provider intermediary
- Provider A runtime
- Provider A authorization mint
- Provider B runtime
- Provider B authorization mint

These hashes identify the code deployed for the campaign.

They do not by themselves establish execution behavior; the behavioral evidence is retained separately in this directory.

## Directory contents

`requests/` contains the retained raw request inputs.

`auth_a/` contains Provider A authorization packages and authorization-generation evidence.

`auth_b/` contains Provider B authorization packages and authorization-generation evidence.

`final_provider_a/` contains Provider A's final local execution and spent state.

`final_provider_b/` contains Provider B's final local execution and spent state.

The campaign root also contains:

- requester logs
- association evidence
- negative-test artifacts
- baseline indexes and archives
- deployed implementation hashes
- final provider hashes
- campaign scorecard
- integrity manifest

## Integrity manifest

`SHA256SUMS.txt` contains the retained SHA-256 manifest for the original scored campaign artifacts.

The scored evidence package was also preserved outside this directory as:

`../MP001_SCORED_20261009_FINAL.tar`

with its archive hash retained as:

`../MP001_SCORED_20261009_FINAL.tar.sha256`

The publication READMEs added to this directory and its child directories were created after the scored evidence package was frozen. They are explanatory documentation and are not original scored artifacts.

They should therefore not be interpreted as members of the original scored manifest or archived campaign evidence.

## What this campaign supports

MP001 supports the narrower claim that the single-process multi-provider reference architecture retained its intended authority separation when its major roles were split across physically separate hosts.

The observed implementation showed that:

- Provider A and Provider B used independent provider-issued authority
- one provider's authorization did not authorize the other provider
- the intermediary transported provider authorization without minting replacement provider authority
- altering request material at the intermediary did not create valid replacement provider authority
- one provider could deny while the other independently proceeded under its own valid authority
- Provider A could proceed while Provider B was unavailable
- previously consumed provider authorizations were denied on sequential replay
- the association could verify, reject, retain, and classify provider boundary submissions without becoming the authority for provider execution

## Limits

MP001 does not establish:

- physical actuation
- independent hardware witness confirmation
- globally synchronized event chronology
- provider implementation diversity
- crash-window replay behavior
- concurrent double-spend behavior
- power-loss persistence behavior
- correctness of arbitrary provider policy
- security of every possible multi-provider deployment

Provider `COMPLETE` and the provider execution logs represent software-local execution evidence in this campaign.

Physical consequence and independently witnessed actuation require separate testing.
