# Evidence

This directory contains the retained evidence for MP002.

MP002 tests whether independently controlled providers can receive the same distributed operation with valid provider-specific authorization and still make different execution decisions under their own local authority.

Evidence is separated into pre-scored smoke validation and the scored campaign so setup activity is not confused with the result used for evaluation.

## Contents

- `smoke/` — retained pre-scored validation artifacts.
- `scored/` — preserved evidence from the scored MP002 campaign.

## Smoke evidence

`smoke/` contains the deployment-validation run performed before scoring.

It includes:

- the smoke association record;
- the smoke summary;
- B01 control artifacts;
- D01 policy-divergence artifacts;
- retained post-run state associated with that validation.

The smoke run confirmed that both intended paths were reachable:

- both providers could independently permit and execute the control request;
- Provider A could permit while Provider B independently denied the divergence request.

The smoke state was not reused as scored state.

Before the scored campaign, provider state was reset and newly minted authorizations were used.

## Scored evidence

`scored/` contains the evidence used for the MP002 result.

The scored campaign contains two cases:

### B01_CONTROL

Both providers received the same request with valid provider-specific authorization under `CTX_ALPHA`.

Both providers independently permitted and executed.

Result:

**PASS**

### D01_POLICY_DIVERGENCE

Both providers received the same request with valid provider-specific authorization under `CTX_MP002_DIVERGE`.

Provider A permitted and executed.

Provider B applied its own local policy and returned a signed:

`DENY policy_denied`

Provider B did not execute D01 and did not consume its D01 authorization.

Result:

**PASS**

## Evidence layers

The scored evidence preserves several different views of the same campaign.

### Request and authorization artifacts

The B01 and D01 directories preserve the exact request and provider-specific authorization packages used for each scored case.

### Provider-local state

The final provider directories preserve each provider's durable execution and spent-authorization state after the campaign.

They show:

- Provider A executed B01 and D01.
- Provider A consumed both corresponding authorizations.
- Provider B executed B01 only.
- Provider B consumed the B01 authorization only.
- Provider B's D01 authorization remained unconsumed.

### Association record

`association.jsonl` preserves the signed provider boundary submissions accepted by the association recorder.

For D01 it records:

- Provider B: `DENY policy_denied`
- Provider A: `START`
- Provider A: `COMPLETE`

The recorder verifies and preserves provider evidence. It does not authorize provider execution, override a provider decision, or calculate a cross-provider transaction result.

### Integrity material

The scored evidence also includes:

- the locked MP002 contract;
- the locked run manifest;
- deployed implementation hashes;
- the campaign scorecard;
- `SHA256SUMS.txt`.

These artifacts connect the preserved result to the implementations and test conditions used during the scored run.

## Interpretation

The evidence supports the MP002 claim that provider-local execution judgment remains independently controlled.

Provider A's approval did not become authority for Provider B.

Provider B's denial was not overridden by:

- Provider A;
- the requester;
- the relay;
- the association.

At the same time, Provider B's denial did not prevent Provider A from exercising Provider A's own independently controlled authority.

The result is therefore evidence of independent provider judgment, not centralized decision-making.

## Important limitations

MP002 does not demonstrate cross-provider atomicity.

In D01, Provider A executed while Provider B denied. The tested architecture does not require either provider to wait for the other before acting.

The evidence also does not establish:

- quorum-gated execution;
- all-provider approval before any consequence;
- globally synchronized chronology across hosts;
- implementation diversity between providers;
- later behavior of Provider B's unconsumed D01 authorization;
- crash-window behavior;
- concurrent authorization use;
- power-loss behavior;
- compromised-provider containment;
- physical actuation;
- independent hardware-witness evidence.

The Provider B divergence policy is intentionally deterministic and test-specific. MP002 tests whether a provider-local decision remains effective at that provider boundary, not whether the policy itself is sophisticated.

## Integrity and publication

The scored evidence was copied into the publication tree without modifying the original working evidence.

The staged scored copy was verified against its source, and all entries in its `SHA256SUMS.txt` were verified before publication staging.

The smoke and scored evidence remain separated so pre-scored validation cannot be mistaken for the scored result.
