# MP004 Scored Evidence

This directory contains the authoritative scored MP004 offline re-verification run.

Scored session:

`MP004_SCORED_20261018_R1`

Overall result:

**PASS**

MP004 tested whether preserved provider boundary evidence could be authenticated and evaluated independently from the association recorder's own classifications.

The verifier operated on preserved MP003 evidence and pinned provider public keys. It did not import or invoke the association recorder.

## Scored run

The scored output is under:

`MP004_SCORED_20261018_R1/`

It contains:

- `SUMMARY.md` — overall and per-case result.
- `case_results.json` — machine-readable results for the seven scored cases.
- `record_results.jsonl` — independent per-record verification results.
- `recorder_comparison.jsonl` — comparison between independently derived results and recorder-supplied metadata after verification.
- `fixture_manifest.json` — exact negative-fixture construction, source record identities, hashes, and expected outcomes.
- `run_metadata.json` — verifier, manifest, dependency, platform, source-count, and invocation metadata.
- `SHA256SUMS.txt` — integrity inventory for the scored output.

## Result

All seven required cases passed.

| Case | Property tested | Result |
|---|---|---|
| B01 | Original preserved provider boundary packages independently authenticate | PASS |
| N01 | Changing a signed event field invalidates the signature | PASS |
| N02 | Changing the signature invalidates the package | PASS |
| N03 | A valid Provider A event does not verify under Provider B's trust anchor | PASS |
| N04 | An unsigned false summary cannot override authenticated provider evidence | PASS |
| N05a | Valid provider evidence remains valid when copied recorder metadata falsely marks it invalid | PASS |
| N05b | Tampered provider evidence remains invalid when copied recorder metadata falsely marks it valid | PASS |

For negative cases, PASS means the expected rejection, mismatch, or contradiction occurred. It does not mean the altered artifact was accepted.

## B01 — preserved provider evidence

The verifier processed all 17 provider `SUBMISSION` packages preserved in the MP003 association log.

All 17 independently authenticated under the pinned provider boundary keys.

Fifteen records belonged to the scored MP003 campaign cases and were also checked against the fixed contextual expectations in the MP004 run manifest.

The remaining two records were signed `DENY auth_malformed` events from the retained MP003 B01 harness misfire. They were included in cryptographic coverage but were not treated as scored MP003 campaign outcomes.

This distinction preserves the original MP003 record rather than silently excluding the misfire.

## N01 — signed-field tamper

A copy of MP003 record 4 had its signed `boundary_value` changed while retaining the original provider signature.

The fixture remained structurally parseable and reached signature verification.

Independent result:

`signature_invalid`

**PASS**

The recorder metadata copied with the record still described the original valid event. The independent result was derived from the modified signed package, not from those recorder fields.

## N02 — signature tamper

A copy of record 4 retained the original event while one bit of the decoded signature was changed.

Independent result:

`signature_invalid`

**PASS**

This confirms that the verifier was validating the preserved provider signature rather than accepting the package because its surrounding recorder record had previously been classified as valid.

## N03 — wrong provider trust anchor

The unchanged Provider A event from record 4 was checked against Provider B's boundary public key.

The direct Ed25519 verification failed.

The verifier's normal provider-to-key mapping also rejected the wrong trust-anchor selection.

**PASS**

This preserves provider-specific trust during later evidence verification. Provider identity does not allow one provider's public key to substitute for another's.

## N04 — false external summary

The test introduced an unsigned summary claiming that Provider B had `EXECUTED` the MP003 C02 operation.

The independently authenticated Provider B evidence for that operation was a signed:

`DENY auth_provider_mismatch`

The false summary was classified:

`contradicted_by_authenticated_denial`

**PASS**

The result is deliberately narrow. It establishes that the supplied summary conflicts with the authenticated provider statement.

It does not convert the provider's signed denial into universal proof that no physical or unobserved execution occurred.

## N05a — false-negative recorder metadata

A copy of valid record 4 retained the original raw provider package but changed recorder-added fields to claim:

- `sig_valid = false`
- `registry_match = false`
- `verification_code = laboratory_false_invalid`

The independent verifier still authenticated the provider package as valid.

**PASS**

Recorder classification did not determine the cryptographic result.

## N05b — false-positive recorder metadata

The N01 signed-field tamper was wrapped in copied recorder metadata claiming:

- `sig_valid = true`
- `registry_match = true`
- `verification_code = ok`

The independent verifier rejected the altered provider package.

**PASS**

A recorder assertion of validity could not make invalid provider evidence authentic.

## Independence from recorder interpretation

The scored verifier derived its result before comparing against recorder-added fields.

The following recorder fields were not verification authorities:

- `sig_valid`
- `registry_match`
- `verification_code`
- `claimed_provider_id`
- `claimed_stage`
- `claimed_binding`
- other `claimed_*` values

For original unmodified records, independently derived values could then be compared with the preserved recorder values.

For intentionally altered fixtures, disagreement was expected where the fixture changed signed bytes or recorder metadata.

The association recorder remained an evidence-recording component, not an authority source for the verifier.

## Source and implementation identity

The scored run checked:

- 111 selected MP003 source files;
- all 67 entries in the MP003 scored `SHA256SUMS.txt`.

Recorded verifier SHA-256:

`452111ef7b7f96e2f42d14a416605ba53ee5b878b3dc05ce2729f6dc9db096c7`

Recorded run-manifest SHA-256:

`2add8dfdf3203685e21dff7b7c9a0fb356496f6c7e43e8affa80f024568f77f2`

The scored run used `cryptography` version `50.0.2` under Python `3.12.14`.

## Evidence meaning

MP004 supports the following narrow result:

**Preserved provider boundary evidence from MP003 could be independently authenticated and evaluated from the raw signed packages and pinned provider trust material without relying on the association recorder's verification classifications.**

The scored negative cases further showed that:

- signed-field modification was detected;
- signature modification was detected;
- a provider's trust anchor could not be substituted with another provider's;
- a later unsigned summary could be contradicted by authenticated provider evidence;
- false recorder classifications could not change the independent cryptographic result.

This is evidence verification.

It is not execution authorization.

The verifier does not create, enlarge, transfer, or substitute provider authority.

## Limits

The scored result does not establish:

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

A valid provider boundary signature establishes that the holder of the corresponding boundary private key signed the event.

It does not, by itself, establish every real-world fact described by that event.
