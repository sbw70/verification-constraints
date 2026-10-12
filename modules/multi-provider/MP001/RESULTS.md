# MP001 Results

MP001 tested whether the multi-provider reference architecture retained provider-scoped authority separation after the principal roles were decomposed from a single Python process onto separate networked hosts.

The scored campaign was executed on 2026-10-09/10.

The tested deployment used:

- a Raspberry Pi 3B+ as the NUVL intermediary
- a Dell Latitude E5450 as Provider A
- an HP Laptop 14-dk1xxx as Provider B
- an HP OmniBook as the association recorder and evidence-collection host
- a separate requester / attacker role

The scored campaign passed all scored baseline and negative-test criteria.

One initial N05 attempt failed to establish its required Provider-B-unavailable precondition. That attempt was retained as a misfire, Provider B was then verified unavailable, and the test was repeated with fresh provider authorizations.

The retry passed.

## Claim under test

MP001 asks:

Does the multi-provider reference architecture retain its intended authority separation when the intermediary, providers, and association are deployed as independent networked roles rather than running inside one process?

The property under test is not merely whether multiple machines can exchange messages.

The relevant separation is whether:

- Provider A retains control over Provider A authorization and execution
- Provider B retains control over Provider B authorization and execution
- Provider A authorization cannot authorize Provider B
- Provider B authorization cannot authorize Provider A
- the intermediary can transport provider authorization without originating or enlarging it
- one provider can deny or be unavailable without transferring authority to another component
- the association can verify provider statements without becoming authoritative for execution

## Result

MP001 passed the scored campaign.

The retained scorecard records:

- B01-B10 — PASS
- N01 — PASS
- N02 — PASS
- N03 — PASS
- N04 — PASS
- N05 initial attempt — RETAINED_MISFIRE
- N05 retry — PASS
- N06 — PASS
- SCORECARD_ASSERTIONS — PASS

The result supports the narrower claim that the single-process reference architecture retained its intended provider-scoped authority separation when its major roles were deployed on physically separate hosts.

## Baseline: B01-B10

Ten baseline requests were executed through the distributed path.

Each baseline request used:

- a unique request body
- verification context `CTX_ALPHA`
- a Provider A authorization issued by Provider A
- a separate Provider B authorization issued by Provider B

For every baseline request:

- the intermediary returned HTTP 204
- Provider A independently validated its own authorization
- Provider B independently validated its own authorization
- Provider A durably consumed its own authorization before `START`
- Provider B durably consumed its own authorization before `START`
- Provider A recorded local execution
- Provider B recorded local execution
- Provider A emitted signed `START` and `COMPLETE` statements
- Provider B emitted signed `START` and `COMPLETE` statements
- the association verified both provider lifecycles

Across B01-B10, the campaign therefore observed:

- 10 Provider A executions
- 10 Provider B executions
- 20 valid provider `START` statements
- 20 valid provider `COMPLETE` statements

The two providers shared correlation material for the same request but did not share authorization IDs, authorization nonces, issuance keys, spent state, execution state, or boundary-signing keys.

## N01 — corrupted Provider A authorization

N01 tested whether invalid Provider A authority could affect Provider B's independent execution authority.

The Provider A authorization signature was deliberately corrupted.

Provider B's authorization remained intact.

Observed result:

- Provider A denied the request with `auth_bad_sig`
- Provider A did not execute under the invalid authorization
- Provider B independently accepted its own valid authorization
- Provider B emitted `START`
- Provider B recorded local execution
- Provider B emitted `COMPLETE`

N01 passed.

This result supports the separation between Provider A authority and Provider B authority.

Failure of Provider A authorization did not revoke, replace, or become a prerequisite for Provider B's independently valid authorization.

## N02 — hostile relay mutation

N02 tested whether a hostile intermediary could alter request material and create valid replacement provider authority by recomputing non-secret relay-side values.

The request representation was changed.

The mechanical binding was recomputed for the altered request.

The original Provider A and Provider B authorizations were then forwarded with the altered request representation.

Observed result:

- Provider A denied with `auth_request_mismatch`
- Provider B denied with `auth_request_mismatch`
- neither provider executed

N02 passed.

The test shows that possession of the request path and the ability to recompute the public mechanical binding were insufficient to authorize the changed request.

The relay could alter transport material.

It could not mint new Provider A or Provider B authorization.

## N03 — forged Provider A boundary statement

N03 tested whether the association would accept a boundary package claiming Provider A when the Provider A boundary signature was invalid.

A Provider A boundary event was retained while its signature was altered.

The forged package was submitted directly to the association.

Observed result:

- the claimed provider matched a registered provider
- the claimed key ID matched the Provider A registry entry
- boundary signature verification failed
- the association recorded `bad_sig`
- the submission was retained as invalid evidence

N03 passed.

The association did not convert a structurally plausible Provider A claim into an authentic Provider A statement.

No provider execution was required for this case.

## N04 — duplicate valid boundary submission

N04 tested whether an exact replay of a previously valid signed provider boundary statement would be preserved as a duplicate rather than counted as a new distinct provider event.

The initial distributed execution completed normally.

An exact previously accepted Provider A `COMPLETE` package was then submitted to the association again.

Observed result:

- the replayed boundary remained signature-valid
- the association retained the second submission
- the association identified it as a duplicate of the earlier Provider A `COMPLETE`
- the duplicate did not become a new distinct provider lifecycle

N04 passed.

Cryptographic validity and observational uniqueness remained separate properties.

## N05 — Provider B unavailable

N05 tested whether Provider A remained independently executable when Provider B was unavailable.

### Initial attempt

The first N05 attempt did not satisfy the test precondition.

Provider B was still running.

During that attempt:

- Provider A executed
- Provider B consumed its authorization
- Provider B emitted `START`
- Provider B did not retain a corresponding execution record

Because Provider B had not actually been made unavailable, this attempt could not score the intended property.

It was retained as:

`N05_INITIAL_ATTEMPT=RETAINED_MISFIRE`

The evidence was not deleted or normalized.

### Retry

Provider B was then forcibly stopped and its unavailability verified.

Fresh Provider A and Provider B authorizations were created.

The request was submitted again as `N05_RETRY_001`.

Observed result:

- Provider A emitted `START`
- Provider A recorded local execution
- Provider A emitted `COMPLETE`
- no Provider B boundary record was produced for the retry

N05 retry passed.

This result supports the property that Provider A did not require Provider B to authorize Provider A's execution and did not wait for Provider B participation before exercising Provider A's own valid authority.

The result does not claim two-provider completion while one provider is unavailable.

It demonstrates the opposite: provider participation remains independent.

## N06 — sequential authorization replay

N06 tested ordinary sequential replay of intact, previously valid provider authorizations.

The same request and the same Provider A and Provider B authorization packages were submitted twice.

First submission:

- Provider A accepted and executed
- Provider B accepted and executed

Second submission:

- Provider A denied with `auth_spent`
- Provider B denied with `auth_spent`
- neither provider produced a second local execution

N06 passed.

Provider spent state remained independent and provider-local.

The replay did not create additional authority merely because the request and authorization packages were intact.

## Association observations

The final scored association log contains:

- 62 total submissions
- 61 signature-valid submissions
- 1 signature-invalid submission
- 28 `START` statements
- 28 `COMPLETE` statements
- 6 `DENY` statements
- 33 Provider A submissions
- 29 Provider B submissions
- 1 detected duplicate

The final association record-chain hash is:

`94f2b4985faf7b32eebb3acc356160f421bbc344848ccf3a139e0002fd6bc9f6`

The SHA-256 of the retained scored `association.jsonl` is:

`2b18fa2f54bc725e2511aca893887a68f44df942258d65e1185ad096e884c348`

The association recorded and verified provider statements.

It did not determine whether either provider was authorized to execute.

## Final Provider A state

Provider A finished the retained campaign state with:

- 14 local execution records
- 14 spent authorizations

Provider A execution-log SHA-256:

`9cd2b26247196d867f5b1fd8cca81aacff780a53f7f0885c352a14ed4f1edbf4`

Provider A spent-state SHA-256:

`88d2a5a6047a3748227ae71ade63a4531af81e2d2f291c8623ac928b8ea4c550`

The counts match.

## Final Provider B state

Provider B finished the retained campaign state with:

- 13 local execution records
- 14 spent authorizations

Provider B execution-log SHA-256:

`da1eba172b0194c71d1ff81960e56be073c7c1c9b170a8bd5a85303c12c4769a`

Provider B spent-state SHA-256:

`84c79f21b91861c377645b85a411158b00bbb8809a097977228e6253ae1c4aab`

The one-record difference is preserved from the retained initial N05 misfire.

It was not corrected after the campaign to make the final state appear cleaner.

## Deployed implementation hashes

The scored deployment used the following implementations.

NUVL intermediary:

`09d458cc8e3e13706b5463deffea0e14fcd784011a629623a09b9bd5ee04d6f4`

Provider A runtime:

`c875582b275f270b8e68af69ed4ee84896e83815cdf33b7d7c5ccc813fe2e606`

Provider A authorization mint:

`1a485e8a5d3de854cb31303b8d3bf1339ef72cb9b42f308490bd02519e76d7ec`

Provider B runtime:

`7759ae8604515ef711ea8cde7b867c3b8faf19e26aedbd48c29d6099fd804fa1`

Provider B authorization mint:

`1b3ba1314761a5489817c660cdc4d62e65ba77deae2bfce2fdce48c228f98deb`

The association recorder SHA-256 was:

`fad60dfc8df53337d2e41288c2c4973442258cae4240945ebbd0aa8920550bfc`

## Evidence integrity

The scored campaign evidence is retained under:

`evidence/MP001_SCORED_20261009/`

Its original scored artifacts are covered by:

`evidence/MP001_SCORED_20261009/SHA256SUMS.txt`

The frozen scored evidence archive is:

`evidence/MP001_SCORED_20261009_FINAL.tar`

Archive SHA-256:

`029cd08f6363ee694cb93f5ecfb83c37d447a1dec8d20b86bd1a09f752c562ca`

The archive hash is retained in:

`evidence/MP001_SCORED_20261009_FINAL.tar.sha256`

Publication READMEs added after the evidence freeze are explanatory documents and are not original scored artifacts.

## What MP001 demonstrates

Within the tested configuration, MP001 observed that:

- Provider A and Provider B retained independent authorization authority
- each provider verified only its own provider-issued authorization
- one provider's authorization did not authorize the other
- invalid Provider A authorization did not prevent Provider B from independently using its own valid authority
- hostile relay mutation did not create replacement provider authority
- the intermediary could recompute public mechanical binding without gaining provider issuance authority
- Provider A could execute under its own valid authority while Provider B was unavailable
- sequential replay of consumed provider authorization was denied independently by both providers
- forged provider boundary evidence was rejected by the association
- exact replay of valid boundary evidence was retained and identified as a duplicate
- the association could verify and correlate provider participation without authorizing provider execution

## What MP001 does not demonstrate

MP001 does not establish:

- physical actuation
- independent physical witness confirmation
- implementation diversity between providers
- correctness of arbitrary provider policy
- global cross-host event chronology
- crash-window replay persistence
- concurrent double-spend resistance
- power-loss replay persistence
- Byzantine consensus
- distributed transaction atomicity
- two-provider execution when one provider is unavailable
- security of every possible multi-provider deployment

Provider `EXECUTED` and `COMPLETE` are software-local execution evidence in MP001.

Physical consequence requires separate testing.

## Conclusion

MP001 moved the multi-provider architecture from a single-process reference into a physically distributed deployment without moving provider execution authority into the intermediary or association.

Provider A remained authoritative for Provider A.

Provider B remained authoritative for Provider B.

The intermediary transported provider-specific authority but could not originate or enlarge it.

The association verified provider statements but did not confer, combine, or replace provider authority.

The scored evidence supports that separation across the tested distributed deployment.
