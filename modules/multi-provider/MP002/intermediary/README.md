# Intermediary

This directory contains the NUVL relay used in the MP002 scored campaign.

The relay transports the request and provider-specific authorization material toward the independent providers.

It does not originate provider authority, enlarge provider authority, interpret provider policy, or decide whether either provider may execute.

## Contents

- `nuvl_multi_relay.py` — multi-provider relay used for the MP002 scored campaign.

## Role in MP002

The relay receives the requester submission and forwards the request path to both providers.

For each provider, it carries:

- the request representation;
- the verification context;
- the request/context binding;
- that provider's authorization package.

The relay is shared transport.

It is not a shared authorization authority.

Provider A independently decides whether Provider A executes.

Provider B independently decides whether Provider B executes.

The relay does not make either decision.

## Unchanged implementation

The relay used in MP002 is unchanged from the MP001 scored implementation.

Its SHA-256 is:

`09d458cc8e3e13706b5463deffea0e14fcd784011a629623a09b9bd5ee04d6f4`

Because the implementation was reused unchanged, its startup banner still contains the MP001 implementation name.

That is a cosmetic artifact of reuse.

The implementation hash, MP002 contract, MP002 manifest, scored session identifier, and preserved evidence identify the relay used in the MP002 campaign.

The deployed implementation hashes are preserved in:

`../evidence/scored/deployed_implementation_hashes.txt`

## Authority model

The relay is not trusted to create valid provider authorization.

It does not possess the provider issuance role required to create provider-valid authority.

A provider authorization remains bound to the provider and request information signed by that provider's issuance key.

Transporting authorization does not make the relay equivalent to the provider that issued it.

The relay therefore may carry authority without becoming the source of that authority.

## B01 control behavior

For `B01_CONTROL`, the relay received the request with valid Provider A and Provider B authorization material.

It forwarded the corresponding material to both providers.

Both providers independently accepted and executed.

The relay returned HTTP:

`204`

That response establishes relay receipt/handling of the requester submission.

It does not itself prove provider execution.

Provider execution is evidenced separately by provider-local state and signed provider boundary events.

## D01 divergence behavior

For `D01_POLICY_DIVERGENCE`, the relay again transported the same request path to both providers with valid provider-specific authorization.

The providers reached different decisions:

- Provider A permitted and executed.
- Provider B denied under its own local policy.

The relay did not alter that disagreement.

It did not convert Provider B's denial into approval.

It did not prevent Provider A from exercising Provider A's separately controlled authority.

The divergent outcome therefore occurred behind the provider boundaries rather than inside the relay.

## No provider-policy role

The relay does not need to understand why Provider B denied D01.

In the tested implementation, Provider B returned:

`policy_denied`

The policy itself remains Provider B-local.

The relay does not evaluate that policy and does not need access to Provider B's internal decision logic in order to transport the operation.

## No association-authority role

The relay also does not determine the association result.

Provider boundary events are generated and signed by the providers.

The association independently verifies and records those events.

The relay does not create the provider boundary evidence used by the association.

## What this component demonstrates

Within MP002, the unchanged relay demonstrates that shared transport can carry requests toward multiple independent providers without becoming the component that decides their execution outcomes.

The same relay path supported both:

- B01, where both providers permitted;
- D01, where the providers disagreed.

That difference arose from provider-local judgment, not a change in relay behavior.

## What this component does not establish

The MP002 relay evidence does not establish:

- cross-provider atomicity;
- quorum-gated execution;
- all-provider approval before execution;
- globally synchronized chronology;
- implementation diversity;
- compromised-provider containment;
- crash-window behavior;
- concurrent authorization use;
- power-loss behavior;
- physical actuation;
- independent hardware-witness evidence.

It also does not make an HTTP `204` response proof that either provider executed.

Provider execution must be established from the provider and association evidence.

## Related evidence

The scored campaign is preserved under:

`../evidence/scored/`

Provider A is documented under:

`../provider_a/`

Provider B is documented under:

`../provider_b/`

The association component is documented under:

`../association/`

The MP002 contract and run manifest are published under:

`../configs/`
