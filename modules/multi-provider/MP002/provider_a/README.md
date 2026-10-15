# Provider A

This directory contains the MP002 Provider A runtime, authorization-minting utility, and laboratory signing keys.

Provider A is an independent authority domain.

It validates Provider A authorization, maintains Provider A's own spent state, records Provider A's own execution, and signs Provider A boundary events.

No other MP002 component is permitted to make Provider A's execution decision for it.

## Contents

- `provider_a.py` — Provider A runtime used in the MP002 scored campaign.
- `mint_authorization_a.py` — utility used to mint Provider A authorization packages for the laboratory tests.
- `provider_a_private.pem` — laboratory private key used to sign Provider A boundary events.
- `provider_a_public.pem` — corresponding public boundary-verification key.
- `provider_a_issuance_private.pem` — laboratory private key used to issue Provider A authorization.
- `provider_a_issuance_public.pem` — corresponding public issuance-verification key.

The private keys in this directory are laboratory test keys intentionally published with the test package.

They are not production credentials.

## Provider A role

Provider A receives:

- the request representation;
- the verification context;
- the request/context binding;
- a Provider A authorization package.

Provider A independently validates the information presented to it.

The relay does not perform Provider A's authorization decision.

Provider B does not perform Provider A's authorization decision.

The association does not perform Provider A's authorization decision.

Provider A retains control over whether Provider A executes.

## Authorization validation

The Provider A runtime validates Provider A-specific authorization before execution.

The tested path includes checks for:

- expected provider identity;
- authorization identifier;
- authorization signature;
- request representation;
- verification context;
- request/context binding;
- authorization spent state.

Authorization is provider-scoped.

Authorization issued for another provider does not become Provider A authority merely because it reaches Provider A.

## MP002 implementation

The Provider A runtime used in MP002 is unchanged from the MP001 scored implementation.

Its SHA-256 is:

`c875582b275f270b8e68af69ed4ee84896e83815cdf33b7d7c5ccc813fe2e606`

The Provider A authorization mint utility is also unchanged from MP001.

Its SHA-256 is:

`1a485e8a5d3de854cb31303b8d3bf1339ef72cb9b42f308490bd02519e76d7ec`

Because the runtime was reused unchanged, its startup banner may still contain the MP001 implementation name.

That does not indicate that an MP001 scored session was running. The implementation hash, MP002 contract, MP002 manifest, session identifier, and preserved evidence identify the deployment used for MP002.

The deployed implementation hashes are preserved in:

`../evidence/scored/deployed_implementation_hashes.txt`

## B01 control behavior

In `B01_CONTROL`, Provider A received a valid Provider A authorization under:

`CTX_ALPHA`

Provider A:

- validated its authorization;
- durably consumed it;
- emitted signed `START`;
- recorded local execution;
- emitted signed `COMPLETE`.

The final Provider A state contains the corresponding execution and spent authorization.

## D01 divergence behavior

In `D01_POLICY_DIVERGENCE`, Provider A received its own valid Provider A authorization under:

`CTX_MP002_DIVERGE`

Provider A had no local policy rule denying that context.

Provider A therefore:

- validated its authorization;
- durably consumed it;
- emitted signed `START`;
- recorded local execution;
- emitted signed `COMPLETE`.

Provider B independently denied the same distributed operation under Provider B's own local policy.

Provider B's denial did not alter Provider A's decision or state.

## Independent judgment

D01 is important because Provider A did not depend on Provider B's approval.

Provider A did not wait for Provider B before exercising Provider A's own authority.

Likewise, Provider A's approval did not cause Provider B to execute.

The resulting divergent outcome is intentional evidence of independent provider judgment:

- Provider A: execute.
- Provider B: deny.

Neither provider became authoritative over the other.

## Durable state

Provider A maintains its own local execution and spent-authorization state.

The final scored copies are preserved under:

`../evidence/scored/final_provider_a/`

Those files show:

- 2 execution records;
- 2 consumed authorizations;
- B01 execution and consumption;
- D01 execution and consumption.

The working runtime-state files themselves are not duplicated in this source directory because the preserved scored copies are published with the evidence set.

## Boundary evidence

Provider A signs its own boundary events.

For successful MP002 execution, the relevant boundary stages are:

- `START`
- `COMPLETE`

The association verifies those signatures using Provider A's configured public boundary key.

The association does not originate Provider A events and does not authorize Provider A execution.

## Authority boundary

Provider A's issuance key authorizes Provider A operations.

Provider A's boundary-signing key attests to Provider A boundary events.

Those roles do not give:

- Provider B authority over Provider A;
- the relay authority over Provider A;
- the association authority over Provider A;
- the requester authority to mint Provider A authorization.

Provider A remains the execution authority for Provider A.

## Cross-provider atomicity

MP002 does not require Provider A to wait for Provider B before executing.

In D01, Provider A executed while Provider B denied.

That result demonstrates independent authority domains, but it also means MP002 does not provide all-or-nothing cross-provider execution.

A composition or quorum design that requires every required provider to approve before any consequence occurs would be a separate mechanism and is not tested here.

## What this implementation demonstrates

Within MP002, Provider A demonstrates that a provider can:

- validate its own provider-specific authorization;
- consume that authorization locally before execution;
- execute under its own authority;
- produce signed boundary evidence;
- proceed independently of another provider's decision.

Combined with Provider B's divergent result, this supports the MP002 claim that provider-local execution judgment remains independently controlled.

## What this implementation does not establish

MP002 Provider A does not establish:

- cross-provider atomicity;
- quorum-gated execution;
- all-provider approval before execution;
- globally synchronized chronology;
- implementation diversity between Providers A and B;
- compromised-provider containment;
- crash-window behavior;
- concurrent authorization use;
- power-loss behavior;
- physical actuation;
- independent hardware-witness evidence.

Those properties are outside the scope of MP002 or require separate tests.

## Related evidence

The B01 scored artifacts are published under:

`../evidence/scored/B01_CONTROL/`

The D01 scored artifacts are published under:

`../evidence/scored/D01_POLICY_DIVERGENCE/`

The final Provider A durable state is under:

`../evidence/scored/final_provider_a/`

The scored association record is:

`../evidence/scored/association.jsonl`

The MP002 contract and run manifest are published under:

`../configs/`
