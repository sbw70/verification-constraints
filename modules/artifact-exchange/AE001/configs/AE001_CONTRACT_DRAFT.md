# AE001 — Provider-Controlled Artifact Exchange

Draft 0.1. Not frozen; actual machine access, live source hashes, ports and runtime configuration remain to be established. No preflight or scored run has occurred.

Property: a request-bound provider-issued artifact traverses the relay; the target provider alone evaluates it, initiates its software execution, and signs its boundary signals. Recording those signals confers no execution authority on the association.

Proposed topology: Windows requester/association, existing Raspberry Pi relay, existing Linux Provider A and Provider B. Reuse the inspected MP003 implementations and existing wire binding, issuance and boundary-signature formats unchanged. AEBS.py is the architectural reference; its fixed token and printed unsigned boundary hashes are not presented as the implementation of the stronger AE001 controls. Patent draft sections 7.2–7.6 inform the technical direction; this campaign makes no legal or whole-document validation claim.

The unmodified relay fans out to A and B. Target B for the four scored cases using its authorization header; leave A's header absent. A's normal signed auth_missing denial is expected background evidence, not an added case. Configuration-only launch files may select isolated AE001 paths/ports after live inspection; they must not change authorization or relay semantics. No canonical MP state is reset or reused as an empty AE001 state.

| Case | Input | Expected Provider B result |
|---|---|---|
| B01 | Fresh request and matching legitimate B authorization | START, software execution, COMPLETE; authorization consumed |
| N01 | Fresh matching B authorization; flip one decoded signature bit and retain all authorization fields | DENY auth_bad_sig; no consumption/execution/START/COMPLETE |
| N02 | Fresh legitimate A authorization placed in B header | DENY auth_provider_mismatch; no consumption/execution/START/COMPLETE |
| B02 | Fresh request and legitimate B authorization after negatives | START, software execution, COMPLETE; authorization consumed |

Use unique request/context/nonces and preserve original/mutated packages separately. Verify request SHA256, existing NUVL_BIND_V1 binding and operation ID, provider/key identity, authorization identity, raw signed events and signatures. Compare per-case provider state and execution logs; denial alone is not proof of non-execution. Relay source/configuration inspection plus delivery evidence must support exclusion of authorization logic/signing material. Association holds public boundary keys, not provider private signing keys. Never infer authorization from relay HTTP 204.

PASS requires all four locked cases, target-specific authenticated boundary events, matching provider state/execution evidence, and consistent source/configuration/input/output hashes. Unexpected admission or intermediary-produced provider boundary evidence is FAIL. Missing delivery, evidence, or preconditions is INCOMPLETE. Preserve misfires; revise/freeze before scoring if implementation or expected reason changes.

Evidence: exact requests/headers, original and modified authorization packages, relay delivery evidence, per-case provider state/execution snapshots, raw boundary packages and association records, source/configuration hashes. Only four cases; no concurrency, crash/restart, DDIL, physical witness, chronology, chain research or quorum claim. Published laboratory keys remain for reproducibility. No README files, deletes, moves, commits or remote writes. Hiccups remain outside future github staging in CHECK_ME.
