# Provider B

This directory contains the MP002 Provider B runtime, authorization-minting utility, laboratory signing keys, and the recorded source diff from the MP001 Provider B runtime.

Provider B is an independent authority domain.

It validates Provider B authorization, applies Provider B's own execution policy, maintains Provider B's own spent state, records Provider B's own execution, and signs Provider B boundary events.

No other MP002 component is permitted to make Provider B's execution decision for it.

## Contents

- `provider_b.py` — Provider B runtime used in the MP002 scored campaign.
- `mint_authorization_b.py` — utility used to mint Provider B authorization packages for the laboratory tests.
- `provider_b_private.pem` — laboratory private key used to sign Provider B boundary events.
- `provider_b_public.pem` — corresponding public boundary-verification key.
- `provider_b_issuance_private.pem` — laboratory private key used to issue Provider B authorization.
- `provider_b_issuance_public.pem` — corresponding public issuance-verification key.
- `MP001_TO_MP002_PROVIDER_B.diff` — source diff between the Provider B runtime actually scored in MP001 and the Provider B runtime used in MP002.

The private keys in this directory are laboratory test keys intentionally published with the test package.

They are not production credentials.

## Provider B role

Provider B receives:

- the request representation;
- the verification context;
- the request/context binding;
- a Provider B authorization package.

Provider B independently validates the information presented to it.

The relay does not perform Provider B's authorization decision.

Provider A does not perform Provider B's authorization decision.

The association does not perform Provider B's authorization decision.

Provider B retains control over whether Provider B executes.

## Authorization validation

The Provider B runtime validates the Provider B-specific authorization before execution.

The tested path includes checks for:

- expected provider identity;
- authorization identifier;
- authorization signature;
- request representation;
- verification context;
- request/context binding;
- authorization spent state.

Authorization is provider-scoped.

Possession of authorization issued for another provider does not make it Provider B authority.

## MP002 policy gate

MP002 adds one deliberate provider-local policy condition to Provider B:

`CTX_MP002_DIVERGE`

When the verified request carries this context, Provider B returns:

`DENY policy_denied`

The policy check occurs after the relevant authorization validation steps but before durable authorization consumption.

The tested ordering is therefore:

valid Provider B authorization  
→ Provider B local policy  
→ `DENY policy_denied`  
→ no authorization consumption  
→ no `START`  
→ no Provider B execution  
→ no `COMPLETE`

This ordering is central to the D01 scored case.

## Policy scope

The MP002 policy is intentionally simple and deterministic.

It is not intended to demonstrate a sophisticated policy engine.

The test asks a narrower architectural question:

**Can Provider B make its own execution decision and have that decision remain effective even when another provider independently approves the same operation?**

For D01, the answer observed in the scored campaign was yes.

Provider A executed under Provider A's authority.

Provider B denied under Provider B's authority.

Neither decision replaced the other.

## Difference from MP001

MP002 intentionally minimizes the change from the MP001 Provider B implementation.

The published:

`MP001_TO_MP002_PROVIDER_B.diff`

shows the source-level difference between the Provider B runtime scored in MP001 and the runtime used in MP002.

The functional MP002 change is the addition of:

- `POLICY_DENY_CONTEXT = "CTX_MP002_DIVERGE"`
- a provider-local `policy_denied` branch before authorization consumption.

The startup banner was also changed from the MP001 name to the MP002 name.

The diff contains no redesign of the authorization format, signing model, spent-state mechanism, boundary-event format, or association path.

This allows the MP002 result to be evaluated as a policy-divergence extension of the already tested multi-provider baseline rather than as an unrelated implementation.

## Implementation integrity

The SHA-256 of the MP002 Provider B runtime used in the scored campaign is:

`5e0ab4b79df4c97bc7bc324d63da85711728d625b82306cdce6c92592e2ee13e`

The Provider B authorization mint utility was unchanged from MP001.

Its SHA-256 is:

`1b3ba1314761a5489817c660cdc4d62e65ba77deae2bfce2fdce48c228f98deb`

The deployed implementation hashes are preserved in:

`../evidence/scored/deployed_implementation_hashes.txt`

## B01 control behavior

In `B01_CONTROL`, Provider B received a valid Provider B authorization under:

`CTX_ALPHA`

The policy-deny condition was not triggered.

Provider B:

- validated its authorization;
- durably consumed it;
- emitted signed `START`;
- recorded local execution;
- emitted signed `COMPLETE`.

The final Provider B state contains the corresponding execution and spent authorization.

## D01 divergence behavior

In `D01_POLICY_DIVERGENCE`, Provider B received its own valid Provider B authorization under:

`CTX_MP002_DIVERGE`

Provider B:

- validated the authorization;
- applied its local policy;
- emitted signed `DENY policy_denied`;
- did not consume the D01 authorization;
- did not emit `START`;
- did not execute;
- did not emit `COMPLETE`.

The association independently verified the signed Provider B denial.

The final Provider B state contains no D01 execution and no D01 spent entry.

## Unconsumed D01 authorization

Because the policy denial occurred before durable authorization consumption, the valid D01 Provider B authorization remained unspent at the end of MP002.

That is a property of the tested ordering, not evidence that the authorization was revoked or destroyed.

MP002 does not test what would happen if the same authorization were later presented after a policy change or under another later condition.

No claim about subsequent acceptance, expiration, revocation, or reuse is made from this test.

## Durable state

Provider B maintains its own local execution and spent-authorization state.

The final scored copies are preserved under:

`../evidence/scored/final_provider_b/`

Those files show:

- 1 execution record;
- 1 consumed authorization;
- no D01 execution;
- no D01 authorization consumption.

The working runtime-state files themselves are not duplicated in this source directory because the preserved scored copies are published with the evidence set.

## Boundary evidence

Provider B signs its own boundary events.

For MP002 these can include:

- `START`
- `COMPLETE`
- `DENY`

The association verifies those signatures using Provider B's configured public boundary key.

The association does not originate Provider B events and cannot convert a Provider B denial into execution.

## Authority boundary

Provider B's issuance key authorizes Provider B operations.

Provider B's boundary-signing key attests to Provider B boundary events.

Those roles do not give:

- Provider A authority over Provider B;
- the relay authority over Provider B;
- the association authority over Provider B;
- the requester authority to mint Provider B authorization.

Provider B remains the execution authority for Provider B.

## What this implementation demonstrates

Within MP002, Provider B demonstrates that a provider can:

- validate its own provider-specific authorization;
- apply its own local policy;
- deny independently of another provider's decision;
- preserve its authorization unconsumed when the denial occurs before consumption;
- produce signed evidence of that denial;
- avoid execution despite another provider approving the same distributed operation.

## What this implementation does not establish

MP002 Provider B does not establish:

- policy sophistication;
- cross-provider atomicity;
- quorum-gated execution;
- all-provider approval before execution;
- later behavior of the unconsumed D01 authorization;
- implementation diversity between Providers A and B;
- compromised-provider containment;
- crash-window behavior;
- concurrent authorization use;
- power-loss behavior;
- physical actuation;
- independent hardware-witness evidence.

Those properties are either outside MP002's scope or require separate tests.

## Related evidence

The D01 scored artifacts are published under:

`../evidence/scored/D01_POLICY_DIVERGENCE/`

The final Provider B durable state is under:

`../evidence/scored/final_provider_b/`

The scored association record is:

`../evidence/scored/association.jsonl`

The MP002 contract and run manifest are published under:

`../configs/`
