# MP001 — Distributed Multi-Provider Authority Separation

MP001 is the first split-host test of the multi-provider execution framework.

It takes the architecture represented by the parent module's single-process reference and deploys the principal roles across separate networked hosts:

- NUVL intermediary
- Provider A
- Provider B
- association recorder
- requester / attacker role

The test asks whether provider-scoped execution authority remains independently controlled after those roles are separated across actual machines.

The result was **PASS** for all scored baseline and negative-test criteria.

One initial N05 attempt failed to establish its required Provider-B-unavailable precondition. That attempt was retained as a misfire, the precondition was corrected, and a fresh retry passed.

## Claim under test

MP001 tests this question:

**Does the multi-provider reference architecture retain its intended authority separation when roles are split across actual independent hosts instead of one Python process?**

The property is authority separation, not merely distributed communication.

In the tested architecture:

- Provider A controls Provider A authorization
- Provider B controls Provider B authorization
- Provider A authorization cannot authorize Provider B
- Provider B authorization cannot authorize Provider A
- the NUVL intermediary can transport provider-specific authorization but cannot originate or enlarge it
- providers do not share spent state
- providers do not share execution state
- one provider does not authorize another
- one provider does not need another provider's approval before exercising its own valid authority
- the association verifies and records provider statements but does not authorize execution

## Architecture

The tested path was:

Requester → NUVL intermediary → Provider A

Requester → NUVL intermediary → Provider B

Provider A → Association

Provider B → Association

The intermediary forwards Provider A and Provider B artifacts independently.

Each provider evaluates only its own provider-specific authorization.

The association receives signed provider boundary statements after provider-side decisions have been made.

The association is observational.

It does not sit in the provider authorization path.

## Tested topology

### Requester / attacker

Hardware:

Chromebook

Role:

request generation and hostile-input generation

### NUVL intermediary

Host:

`nuvl-relay`

Hardware:

Raspberry Pi 3B+

IPv4:

`192.168.1.100`

Role:

stateless multi-provider intermediary

### Provider A

Host:

`Xer0trust-3`

Hardware:

Dell Latitude E5450

IPv4:

`192.168.1.118`

Role:

independent Provider A

### Provider B

Host:

`Xer0trust2`

Hardware:

HP Laptop 14-dk1xxx

IPv4:

`192.168.1.106`

Role:

independent Provider B

### Association / evidence collection

Host:

`Xer0trust`

IPv4:

`192.168.1.102`

Role:

association recorder, operator, and evidence collection

The frozen topology is retained in:

`evidence/MP001_TOPOLOGY_FREEZE.txt`

The earlier environmental baseline is retained in:

`evidence/MP001_PREDEPLOY_BASELINE.txt`

## Authority model

Provider authorization is provider-scoped.

Provider A and Provider B use separate:

- Ed25519 issuance keypairs
- Ed25519 boundary-signing keypairs
- authorization IDs
- authorization nonces
- spent state
- local execution state
- runtime decision instances

An authorization issued by Provider A has no authority at Provider B.

An authorization issued by Provider B has no authority at Provider A.

A common request representation, binding, or operation ID does not change that separation.

Those values provide representation and correlation.

They are not shared execution authority.

## NUVL intermediary

The intermediary implementation is under:

`intermediary/`

Its scored implementation:

- accepts opaque request bytes
- computes the request representation
- carries the verification context
- computes a non-secret mechanical binding
- selects the Provider A authorization header for Provider A
- selects the Provider B authorization header for Provider B
- forwards provider artifacts asynchronously
- returns HTTP 204 without waiting for provider execution

The intermediary does not:

- possess provider issuance private keys
- validate provider authorization
- maintain provider spent state
- maintain provider execution state
- decide whether Provider A executes
- decide whether Provider B executes
- create replacement provider authority

A requester-visible HTTP 204 confirms intermediary receipt and handling.

It does not by itself establish provider execution.

## Providers

Provider implementations are under:

- `provider_a/`
- `provider_b/`

Each provider independently:

1. parses its received artifact
2. recomputes the mechanical binding
3. validates provider-specific authorization
4. verifies its own issuance signature
5. verifies the authorized request representation
6. verifies the authorized context
7. checks its own spent state
8. durably consumes the authorization
9. emits signed `START`
10. performs its provider-local execution step
11. durably records local execution evidence
12. emits signed `COMPLETE`

Validation failures produce signed provider `DENY` statements.

No `START` is generated before durable authorization consumption.

## Association

The association implementation is under:

`association/`

The association:

- receives provider boundary submissions
- preserves the raw received bytes
- hashes submissions
- verifies provider boundary signatures
- verifies provider identity against the registry
- records malformed and forged submissions
- identifies exact duplicate signed events
- maintains a local hash-chained observation record

It does not:

- issue provider authorization
- consume provider authorization
- decide provider policy
- trigger provider execution
- confer authority on Provider A
- confer authority on Provider B
- combine the two providers into a new authority

Association evidence is therefore evidence of provider statements, not a source of provider authority.

## Configuration

The fixed MP001 protocol and scoring definitions are under:

`configs/`

### `MP001_CONTRACT.md`

Defines the normative:

- canonical representation
- request representation
- verification context
- mechanical binding
- operation ID
- authorization structure
- authorization signatures
- validation sequence
- single-use behavior
- boundary-event structure
- boundary signatures
- association semantics

Scored SHA-256:

`7db3a52907af48d2524995e15b947600e534555758338cc38ce2594ff633ff4e`

### `MP001_RUN_MANIFEST.json`

Defines the baseline and negative cases and their expected observations.

Final scored SHA-256:

`37f2cea056bce67c209204467fa574c1d83307ec7e6df59815fb58eae20acf54`

The manifest also fixes the claims MP001 does not make.

## Scored campaign

The scored campaign is retained under:

`evidence/MP001_SCORED_20261009/`

The final scorecard records:

- B01-B10 — PASS
- N01 — PASS
- N02 — PASS
- N03 — PASS
- N04 — PASS
- N05 initial attempt — RETAINED_MISFIRE
- N05 retry — PASS
- N06 — PASS
- SCORECARD_ASSERTIONS — PASS

See:

`RESULTS.md`

for the test-by-test result.

See:

`PROVENANCE.md`

for deployment, artifact, hash, and evidence-history details.

## Baseline series

B01 through B10 tested ordinary valid distributed operation.

For all ten requests:

- Provider A independently accepted and executed under Provider A authorization
- Provider B independently accepted and executed under Provider B authorization
- both providers durably consumed their own authorization
- both providers emitted signed `START`
- both providers recorded local execution
- both providers emitted signed `COMPLETE`
- the association verified both provider lifecycles

The baseline established the ordinary split-host execution path before negative cases were considered.

## Negative cases

### N01 — bad Provider A authorization

Provider A received a corrupted authorization signature.

Provider B received intact Provider B authorization.

Observed:

- Provider A — `DENY auth_bad_sig`
- Provider B — `START`, local execution, `COMPLETE`

This demonstrated that invalid Provider A authority did not invalidate or replace Provider B's independently valid authority.

### N02 — hostile relay mutation

The request representation was changed and the non-secret mechanical binding was recomputed while the original provider authorizations were retained.

Observed:

- Provider A — `DENY auth_request_mismatch`
- Provider B — `DENY auth_request_mismatch`
- no provider execution

Control of relay-side representation material did not create replacement provider authority.

### N03 — forged provider boundary

A boundary package claiming Provider A was submitted with an invalid Provider A boundary signature.

Observed:

- registry provider match
- signature invalid
- verification code `bad_sig`

The association retained the forged submission but did not accept it as an authentic Provider A statement.

### N04 — duplicate boundary

A valid Provider A `COMPLETE` boundary package was submitted to the association a second time without alteration.

Observed:

- signature remained valid
- second submission was retained
- duplicate was identified
- it did not become a new distinct provider lifecycle

### N05 — Provider B unavailable

The first attempt did not actually establish Provider B unavailability and is retained as a misfire.

After Provider B was stopped and verified unavailable, the test was repeated with fresh authorizations.

Observed on the valid retry:

- Provider A `START`
- Provider A local execution
- Provider A `COMPLETE`
- no Provider B lifecycle

Provider A therefore did not require Provider B participation to exercise Provider A's own valid authority.

### N06 — sequential authorization replay

The same intact Provider A and Provider B authorizations were submitted twice.

First submission:

- Provider A executed
- Provider B executed

Second submission:

- Provider A — `DENY auth_spent`
- Provider B — `DENY auth_spent`
- no second execution

## Association totals

The scored association log contains:

- 62 submissions
- 61 signature-valid submissions
- 1 signature-invalid submission
- 28 `START`
- 28 `COMPLETE`
- 6 `DENY`
- 33 Provider A submissions
- 29 Provider B submissions
- 1 duplicate

Final record-chain hash:

`94f2b4985faf7b32eebb3acc356160f421bbc344848ccf3a139e0002fd6bc9f6`

Scored `association.jsonl` SHA-256:

`2b18fa2f54bc725e2511aca893887a68f44df942258d65e1185ad096e884c348`

## Final provider state

Provider A finished with:

- 14 local execution records
- 14 spent authorizations

Provider B finished with:

- 13 local execution records
- 14 spent authorizations

The Provider B difference is preserved from the retained initial N05 misfire.

It was not removed or normalized after the campaign.

## Evidence integrity

The scored evidence directory contains:

`SHA256SUMS.txt`

The original scored artifacts were also frozen as:

`evidence/MP001_SCORED_20261009_FINAL.tar`

Archive SHA-256:

`029cd08f6363ee694cb93f5ecfb83c37d447a1dec8d20b86bd1a09f752c562ca`

Publication documentation added after the evidence freeze is not part of the original scored artifact set.

## Directory guide

### `association/`

Association recorder, provider registry, and provider boundary trust anchors.

### `configs/`

Normative MP001 contract and scored-run manifest.

### `intermediary/`

NUVL multi-provider relay used in the campaign.

### `provider_a/`

Provider A runtime, authorization mint, and MP001 laboratory key material.

### `provider_b/`

Provider B runtime, authorization mint, and MP001 laboratory key material.

### `evidence/`

Pre-deployment baseline, topology freeze, pre-run smoke evidence, scored campaign artifacts, integrity files, and frozen scored archive.

### `RESULTS.md`

Scored results and supported claims.

### `PROVENANCE.md`

Deployment history, implementation hashes, key provenance, preparation history, retained misfire, and evidence integrity.

## Relationship to the parent reference

The parent multi-provider module contains `MPBS.py`, a compact single-process architectural reference.

MP001 is not a claim that the parent reference and MP001 are identical implementations.

MP001 takes the same central authority-separation model and subjects a two-provider form of it to a real split-host deployment with:

- provider-issued Ed25519 authorization
- provider-local durable spent state
- provider-local execution evidence
- signed provider boundary statements
- association-side signature verification
- retained negative-test evidence

The MP001 result therefore concerns the tested split-host implementation in this directory.

## Supported conclusion

Within the tested MP001 configuration:

**Provider A remained authoritative for Provider A.**

**Provider B remained authoritative for Provider B.**

The NUVL intermediary transported provider-specific authority without becoming equivalent authority.

The association verified provider statements without becoming execution authority.

The split-host deployment therefore preserved the provider-scoped authority separation under test.

## Limits

MP001 does not claim:

- physical actuation
- independent physical witness confirmation
- provider implementation diversity
- global cross-host clock authority
- crash-window replay persistence
- concurrent double-spend resistance
- power-loss replay persistence
- Byzantine consensus
- distributed transaction atomicity
- correctness of arbitrary provider policy
- security of every possible deployment

Provider `EXECUTED` and `COMPLETE` in MP001 are software-local execution evidence.

Physical consequence requires separate testing.

## Licensing

Licensing for MP001 follows the licensing terms of the parent multi-provider module.

See the parent `README.md` and applicable module licensing material for current terms.
