# Scored Evidence

This directory contains the preserved evidence from the MP002 scored campaign.

The scored run tested whether independently controlled providers could receive the same operation with valid provider-specific authorization and still make different execution decisions without another component overriding either provider.

The campaign contained one control case and one policy-divergence case.

## Session

Scored session:

`MP002_SCORED_20261013`

The association recorder, provider registry, contract, run manifest, provider runtimes, mint utilities, and relay implementation were fixed for the scored campaign.

The contract and manifest copies preserved in this directory are byte-identical to the corresponding publication copies under `configs/`.

## Contents

- `MP002_CONTRACT.md` — contract governing the scored campaign.
- `MP002_RUN_MANIFEST.json` — locked run manifest and expected scored cases.
- `SCORECARD.txt` — concise scored-result record captured after execution.
- `association.jsonl` — append-only hash-chained association record containing the signed provider boundary submissions received during the scored session.
- `deployed_implementation_hashes.txt` — hashes of the implementations used for the scored deployment.
- `SHA256SUMS.txt` — integrity manifest for the scored evidence set.
- `B01_CONTROL/` — exact request and provider-specific authorization artifacts for the control case.
- `D01_POLICY_DIVERGENCE/` — exact request and provider-specific authorization artifacts for the divergent-policy case.
- `final_provider_a/` — Provider A's final durable execution and spent-authorization state.
- `final_provider_b/` — Provider B's final durable execution and spent-authorization state.

## Scored cases

### B01_CONTROL

Both providers received the same request with valid provider-specific authorization under:

`CTX_ALPHA`

Both independently permitted and executed the operation.

Observed signed boundary lifecycle:

- Provider A: `START`, `COMPLETE`
- Provider B: `START`, `COMPLETE`

Final local state shows one B01 execution and one consumed B01 authorization at each provider.

Result:

**PASS**

### D01_POLICY_DIVERGENCE

Both providers received the same request with valid provider-specific authorization under:

`CTX_MP002_DIVERGE`

Provider A permitted the request.

Provider B applied its own local policy and denied the request before authorization consumption.

Observed signed boundary result:

- Provider A: `START`, `COMPLETE`
- Provider B: `DENY policy_denied`

Final local state shows:

- Provider A executed D01 and consumed its D01 authorization.
- Provider B did not execute D01.
- Provider B did not consume its D01 authorization.

Result:

**PASS**

## Final provider state

At the end of the scored campaign:

Provider A:

- executions: `2`
- spent authorizations: `2`

Provider B:

- executions: `1`
- spent authorizations: `1`

For D01:

`D01_PROVIDER_A_AUTHORIZATION_CONSUMED=True`

`D01_PROVIDER_B_AUTHORIZATION_CONSUMED=False`

These counts reconcile with the two scored cases:

- A executed B01 and D01.
- B executed B01 only.

## Association evidence

The association recorder verified individual signed provider submissions and preserved them in the hash-chained `association.jsonl`.

For D01, the association record contains:

- Provider B signed `DENY` with reason `policy_denied`.
- Provider A signed `START`.
- Provider A signed `COMPLETE`.

All corresponding submissions passed signature verification.

The association recorder does not decide whether an operation is authorized, does not cause provider execution, and does not convert a provider denial into approval.

It also does not calculate a cross-provider success result such as quorum, `1/2`, `2/2`, or transaction completion. Any such interpretation would be post-run analysis of the preserved provider evidence, not a decision made by the recorder during execution.

## Integrity

The final association record hash recorded for the scored campaign is:

`7002cd90fcf586dd145c6156ca3ed5da18f267138796099f536c4df53798013a`

The SHA-256 of `association.jsonl` is:

`d3025b6b55331dfe4505f0a1ddc82fdb1776f5dcc30449b77f683b7ed258d9e8`

`SHA256SUMS.txt` covers the preserved scored evidence files in this directory tree.

The staged publication copy was verified against the source scored-evidence directory before publication.

## What MP002 demonstrates

The scored evidence supports the narrower MP002 claim:

**providers participating in the same distributed operation can retain independent provider-local execution judgment even when both possess valid provider-specific authorization for the same request.**

Provider A's approval did not override Provider B's denial.

Provider B's denial did not prevent Provider A from exercising Provider A's own independently controlled authority.

The relay transported the request and authorization material without becoming provider authority.

The association verified and preserved signed provider evidence without becoming execution authority.

## Important limitations

MP002 does not demonstrate cross-provider atomicity.

In D01, Provider A executed while Provider B denied. The architecture tested here does not require one provider to wait for another before acting.

MP002 therefore does not establish:

- all-or-nothing distributed execution;
- quorum-gated execution;
- all-provider approval before any consequence;
- globally synchronized chronology across hosts;
- implementation diversity between providers;
- behavior after later reuse of Provider B's unconsumed D01 authorization;
- crash-window behavior;
- concurrent authorization use;
- power-loss behavior;
- compromised-provider containment;
- physical actuation;
- independent hardware-witness evidence.

The Provider B policy used for D01 was deliberately deterministic and test-specific. MP002 tests whether a provider-local denial remains effective at that provider boundary, not whether the policy itself is sophisticated.

## Smoke versus scored evidence

Setup and pre-scored validation artifacts are preserved separately under:

`../smoke/`

Those artifacts are retained for provenance and troubleshooting but are not substituted for the scored campaign documented here.
