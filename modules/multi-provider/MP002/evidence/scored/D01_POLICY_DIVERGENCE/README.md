# D01 Policy Divergence

This directory contains the request and provider-specific authorization artifacts for the MP002 scored policy-divergence case.

D01 tests whether two independent providers can receive the same operation with valid provider-specific authorization and still reach different execution decisions under their own local authority.

## Test condition

Both providers received the same request representation under:

`CTX_MP002_DIVERGE`

Each provider was given its own valid provider-issued authorization for that request.

Provider A permitted the operation.

Provider B's local policy explicitly denied the test context `CTX_MP002_DIVERGE`.

The Provider B policy check occurs after authorization validation but before durable authorization consumption.

## Contents

- `request.json` — exact request bytes used for the scored D01 submission.
- `SCORED_D01_provider_a_auth.json` — Provider A authorization package.
- `SCORED_D01_provider_a_auth.json.b64` — encoded Provider A authorization transmitted through the relay.
- `SCORED_D01_provider_b_auth.json` — Provider B authorization package.
- `SCORED_D01_provider_b_auth.json.b64` — encoded Provider B authorization transmitted through the relay.

## Scored authorization identifiers

Provider A:

`07f8f83fc040d9f88d2b1f98dabb5ed73ad1788dd96de58ed1da41fb32a30e98`

Provider B:

`017ea9125ded9e79bf52b10be8471744848417f37c5e8d121828aa470757bfab`

The request representation was:

`7c954784d82d0d80509f70e8eca810f2dbbf1c6ae74b6fe72672903d73c30505`

## Result

**PASS**

Provider A:

- validated its provider-specific authorization;
- permitted the request;
- durably consumed the authorization;
- emitted signed `START`;
- recorded local execution;
- emitted signed `COMPLETE`.

Provider B:

- validated its provider-specific authorization;
- applied its local policy;
- emitted signed `DENY`;
- reported reason `policy_denied`;
- did not consume the D01 authorization;
- did not emit `START`;
- did not emit `COMPLETE`;
- did not create a D01 execution record.

The association accepted the corresponding signed boundary submissions as cryptographically valid.

For D01, the recorded events were:

- Provider B: `DENY policy_denied`
- Provider A: `START`
- Provider A: `COMPLETE`

No global timing or causal-order claim is made from the order in which those independently generated events reached the association.

## What D01 establishes

D01 demonstrates provider-local decision independence in the tested multi-provider path.

Provider A's approval did not cause Provider B to execute.

The relay did not convert Provider B's denial into execution.

The association did not convert Provider B's denial into execution.

Provider B retained control over whether Provider B executed.

The providers therefore participated in the same operation without requiring one provider's judgment to become authoritative over the other.

## Scope of the policy test

The Provider B policy used here is intentionally simple and deterministic.

It denies when the verification context is:

`CTX_MP002_DIVERGE`

MP002 does not claim that this policy is sophisticated, adaptive, or representative of a production policy engine.

The property under test is narrower:

**a provider-local deny remains authoritative for that provider and is not overridden elsewhere in the path.**

## Authorization consumption

Provider B denied D01 before durable authorization consumption.

As a result, Provider B's valid D01 authorization remained unspent at the end of the scored campaign.

This behavior is visible in the final Provider B spent-state evidence.

MP002 does not test subsequent presentation of that unconsumed authorization after a policy change, expiration, revocation, restart, or other later condition.

No claim about such later behavior is made here.

## Cross-provider atomicity

D01 does not provide cross-provider atomic execution.

Provider A executed even though Provider B denied.

This is consistent with the MP002 architecture: Provider A does not wait for Provider B, and Provider B does not wait for Provider A.

MP002 therefore demonstrates independent provider judgment, not an all-or-nothing distributed transaction.

A system requiring every provider to approve before any provider performs a consequence would require a separate composition or quorum mechanism that gates execution before provider side effects occur. That behavior is not tested here.

## What D01 does not establish

D01 does not establish:

- cross-provider atomicity;
- quorum or all-provider approval before execution;
- globally synchronized chronology;
- implementation diversity;
- later behavior of Provider B's unconsumed authorization;
- crash-window behavior;
- concurrent authorization use;
- power-loss behavior;
- compromised-provider containment;
- physical actuation or independent hardware-witness evidence.

These claims remain outside the scope of MP002.

## Related evidence

The scored association log is preserved in:

`../association.jsonl`

Final Provider A state:

`../final_provider_a/`

Final Provider B state:

`../final_provider_b/`

The control case is:

`../B01_CONTROL/`

The scored campaign summary is:

`../SCORECARD.txt`

Integrity information for the scored evidence set is:

`../SHA256SUMS.txt`
