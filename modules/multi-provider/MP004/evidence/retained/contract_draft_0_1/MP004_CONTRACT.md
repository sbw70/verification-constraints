# MP004 — Independent Offline Re-verification Contract

Version: 0.1, prepared 2026-10-18. Status: DRAFT; no verifier implementation or scoring has occurred. Freeze a numbered revision and its SHA-256 before implementation/scoring. Changes after freeze require a new revision; retain earlier artifacts.

## Claim
An independent offline verifier can authenticate preserved provider boundary events and evaluate the specified evidence assertions from raw signed packages and pinned provider trust material, without using recorder classifications as verification inputs.

Authentication establishes that the holder of the corresponding boundary key signed the event. It does not establish physical truth, policy correctness, or completeness of the delivered evidence. Provider-produced signatures, recorder storage, and later interpretation are separate evidence layers.

## Workspace and source
Working root: C:\Users\holiw\esp32-main\MULTI_PROVIDER_004.
Canonical module target: modules/multi-provider/MP004/.
Source inspected: C:\Users\holiw\esp32-main\MULTI_PROVIDER_003\github\modules\multi-provider\MP003.
Publication intended: https://github.com/sbw70/verification-constraints/tree/main/modules/multi-provider/MP003.
Live publication fetch failed during preparation; equivalence with current remote HEAD is NOT established. Before freeze, record the published commit and compare selected source bytes to that revision. Local hashes below match the supplied handoff.

Pin these source hashes:
- evidence/scored/association.jsonl: 50af864099a7eb91970866a664005caa24042224d2b69525e0e9610c53eb642a
- configs/MP003_CONTRACT.md: ac368500126f3314faa7f5193a07bbb78061c10e1931606778b6414702b9579b
- configs/MP003_RUN_MANIFEST.json: 85ac48ff64f7b94d078ceb0638240980d30013a78cf3d850964abbd895eb7368

Copy, never move, the source documentation, configs, public registry/trust material, and complete scored tree into source/MP003/. Record each file's relative path, byte length and SHA-256 in configs/MP004_SOURCE_MANIFEST.json. Validate every existing scored SHA256SUMS entry before freezing. Preserve README additions outside that manifest's coverage explicitly. No writes to MP003.

Workspace directories: configs/, source/MP003/, verifier/, fixtures/, evidence/preflight/, evidence/scored/, evidence/retained/, notes/. Mutations belong only in fixtures/; every fixture records source file/hash/record sequence, transformation and output hash. Reserve verifier/ without writing code during this assignment.

## Fixed source selection
Use all 17 SUBMISSION packages (record_seq 2–18) from the pinned 19-record R2 log. Records 1 and 19 are recorder session records, not provider evidence. Records 2–3 are retained auth_malformed harness misfires: include in cryptographic coverage, exclude from MP003 scored success claims. Campaign mappings: B01 4–7; C01 8–10; C02 11–13; C03 14–15; B02 16–18.

The individual record selector is a source locator only. Derive provider, stage and all facts from decoded event bytes, never claimed_* recorder fields.

## Trust and independent computations
Use only public Ed25519 boundary keys. Independently pin provider-to-key mappings; do not select keys from event-supplied paths or recorder classifications. Compute key_id as sha256: plus SHA256 of the raw 32-byte public key.
- PROVIDER_A: sha256:e4664ee3b7bb0012fb7d8f763c9df74594d8a6bec8488d97532a5846cc04b6ff
- PROVIDER_B: sha256:db764408aa319642363057d804f0c2a3d2c7dd22de86ae4a6d6549cb97f60225

Decode raw_body_b64 as strict standard base64; parse UTF-8 JSON. Reject duplicate keys, nonfinite numbers, malformed types, missing/extra package or event fields and unsupported versions/algorithms. Package: alg, event, signature; alg exactly Ed25519. Event fields exactly version, operation_id, binding, provider_id, key_id, stage, boundary_value, authorization_id, authorization_nonce, reason_code. Version is integer 1, excluding boolean. Stage is START, COMPLETE or DENY. Provider/key must match pinned mapping. Hash fields operation_id, binding, boundary_value are 64 lowercase hex characters. Authorization ID is null or 64 lowercase hex; nonce is null or string. START/COMPLETE require nonempty authorization ID/nonce and null reason; DENY requires a nonempty reason string, with nullable authorization ID/nonce. Freeze the allowed denial reason vocabulary from inspected provider code before implementation.

Canonical event bytes: json.dumps(event, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8"). Canonicalize the parsed event; do not require original package whitespace/key ordering to be canonical. Decode signature as unpadded base64url, require canonical encoding and exactly 64 decoded bytes. Verify Ed25519 over b"NUVL-MP-BOUNDARY-v1|" + canonical_event_bytes using the independently selected key.

Recompute raw SHA256 from decoded package bytes and signed_event_sha256 as SHA256(canonical_json({"event": event, "signature": signature_text})). Recorder hash/classification comparisons occur only after the independent result is fixed; they cannot change it.

For scored campaign records, derive request_repr from exact preserved request.json bytes and contexts from fixed manifest/send artifacts. Recompute binding = SHA256(UTF8("NUVL_BIND_V1|" + request_repr + "|" + context)); operation_id = SHA256(UTF8("NUVL-MP-OP-v1|" + binding)). Compare event identities, authorization IDs/nonces and expected stages/reasons against independently extracted source artifacts. Freeze exact per-record assertion values and artifact hashes in the run manifest before scoring. Records 2–3 require only package/schema/authentication coverage unless their request/context source is independently identified.

Report separate dimensions: input/schema status, cryptographic status, trust mapping status, contextual assertion status and interpretation status. A valid signature is not automatically an accepted interpretation. Fail closed on parse/key errors; do not label a pre-signature mapping failure as a cryptographic failure.

Do not import or invoke the association recorder or its verification helpers. A standard independent cryptography library is permitted. Compare recorder sig_valid, registry_match, verification_code, claimed_* and derived hash fields only in a post-verification comparison report. Recorder fields must not populate expected provider facts.

## Scored matrix and falsification
| Case | Exact transformation/source | Required result |
|---|---|---|
| B01 valid control | All 17 original packages, pinned public keys | All authenticate; 15 scored events satisfy frozen campaign assertions; 2 misfire events remain separately labeled |
| N01 signed-field tamper | Record 4: replace boundary_value with 64 zeroes (use 64 ones if already zero); retain signature | Structurally valid fixture reaches cryptographic check and signature fails |
| N02 signature tamper | Record 4: flip low bit of first decoded signature byte; re-encode base64url without padding; preserve event | Signature fails |
| N03 wrong anchor | Verify unchanged record 4 with B public key in an explicitly labeled cryptographic negative harness | Direct Ed25519 check fails; production path must also refuse mismatched key mapping |
| N04 false summary | Unsigned JSON claim: PROVIDER_B EXECUTED C02, identified by frozen C02 operation_id; compare against authenticated record 11 | Claim classified contradicted by signed DENY auth_provider_mismatch; no authority attributed to summary |
| N05a false invalid metadata | Copy record 4; set sig_valid=false, registry_match=false, verification_code="laboratory_false_invalid"; raw_body_b64 unchanged | Underlying package still authenticates; metadata disagreement reported |
| N05b false valid metadata | Wrap N01 tampered package in copied record 4; set sig_valid=true, registry_match=true, verification_code="ok" | Underlying signature rejected despite metadata; disagreement reported |

N04 authenticates the provider's reported denial. Provider B's per-case spent/execution snapshots and final snapshots may corroborate the software record, with provenance and hashes, but are not provider-signed facts unless separately demonstrated. Neither a DENY nor absence from this finite log proves universal absence of execution. Do not infer real-world non-execution solely from a signature.

Every case is mandatory in this proposed revision. Expected cryptographic rejection is a case PASS, not acceptance of the artifact. Overall PASS requires all expected results, complete coverage, source-hash consistency and independence from recorder metadata. Any accepted tamper, accepted wrong key, dependence on classification, accepted false summary, missing fixture, or missing output falsifies/prevents PASS. Infrastructure errors produce INCOMPLETE, never silent exclusion. Retain all misfires and corrections.

## Freeze and output requirements
Before verifier code: resolve live-publication comparison; validate full source manifest; pin record-level raw package hashes, expected assertions, denial vocabulary, fixture recipes, filenames and outputs; freeze contract and run manifest with SHA-256. This draft is not a locked contract.

Scoring records contract/manifest/verifier/dependency hashes and versions, invocation, per-record results, per-case expected/actual outcomes, counts, fixture hashes, post-verification recorder comparisons and explicit overall status. Copy full scored evidence into staging; never move or overwrite originals. No execution-authority test or live topology changes are required.

Association chain verification is deferred from the mandatory MP004 claim. If later added, score it separately; internal chain consistency does not authenticate provider signatures or prove immutable storage/global chronology. Supplied MP003 terminal record hash: 4c3282924708f504323bbd2cb1188bd0f2071e54a66b5bdb928e344abaa0a906.

## Claim boundaries
NUVL transports authority; each provider alone controls its execution authority. The association and offline verifier are evidentiary only. Verification cannot originate/enlarge authority or change historical provider decisions.

No claim of physical witness, global chronology, synchronized clocks, crash/power-loss behavior, restart durability, concurrency, cross-provider atomicity, implementation diversity, compromised-host resistance, boundary-key compromise resistance, completeness of undelivered evidence, immutable storage, or physical consequences from software records. Published laboratory keys support reproducibility, not post-publication historical authenticity against an adversary able to re-sign artifacts.
