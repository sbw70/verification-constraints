# Association

This directory contains the MP002 association recorder, provider registry, and trusted provider boundary-verification keys.

The association receives signed provider boundary events, verifies them against the configured provider registry, rejects invalid or duplicate submissions, and preserves accepted submissions in an append-only hash-chained record.

It does not authorize provider execution and does not become authority over either provider.

## Contents

- `association_recorder.py` — receives, verifies, and records signed provider boundary events.
- `provider_registry.json` — maps provider identities to the boundary-verification keys trusted by the recorder.
- `trust/` — public trust-anchor material used to verify provider boundary signatures.

## Role in MP002

The association exists to verify and preserve evidence from independently controlled providers.

For each submitted boundary event, the recorder checks the claimed provider against the registry, verifies the provider signature, detects duplicate submissions, and appends the result to the association log.

The resulting record can show what each provider independently reported without requiring either provider to trust the other.

The association does not:

- issue provider authorization;
- validate provider issuance authority on behalf of a provider;
- decide whether a provider should execute;
- consume provider authorization;
- cause Provider A or Provider B to execute;
- override a provider denial;
- convert a denial into an approval;
- enlarge authority received from either provider.

Provider execution authority remains provider-scoped.

## MP002 implementation

The association recorder used in MP002 is unchanged from the MP001 scored implementation.

Its SHA-256 is:

`fad60dfc8df53337d2e41288c2c4973442258cae4240945ebbd0aa8920550bfc`

The provider registry is also unchanged from MP001.

Its SHA-256 is:

`59d739588427d87313e3434982d943a9c82bad26c3fe3deb7d5488efadb6088d`

Because the recorder implementation was reused unchanged, its startup banner still identifies itself as:

`MP001_ASSOCIATION_RECORDER`

That banner reflects the reused implementation name and does not indicate that the MP001 scored session was running. The MP002 scored session was separately identified as:

`MP002_SCORED_20261013`

The implementation hash, registry hash, session record, contract, manifest, and preserved evidence identify the actual MP002 deployment.

## What the recorder verifies

The recorder verifies individual provider boundary submissions.

A boundary event includes information such as:

- provider identity;
- operation identifier;
- binding;
- boundary stage;
- authorization identifier where applicable;
- authorization nonce where applicable;
- denial reason where applicable.

The recorder verifies the provider's signature using the corresponding public boundary key from the registry and records the verification result.

For accepted MP002 scored submissions, the verification result was:

`sig_valid=True`

with:

`verification_code=ok`

## D01 association evidence

For the scored D01 policy-divergence operation, the association recorded three valid signed provider events:

- Provider B: `DENY`, reason `policy_denied`
- Provider A: `START`
- Provider A: `COMPLETE`

All three passed signature verification.

This records that Provider B independently denied while Provider A independently proceeded through its own execution lifecycle.

Nothing in the association path converted Provider B's signed denial into a Provider B execution.

## Event ordering

The association log records the order in which submissions were received by the recorder.

That order is not treated as a globally synchronized chronology across the independent hosts.

For D01, Provider B's denial was recorded before Provider A's `START` and `COMPLETE`, but MP002 does not use that receipt order to make a cross-host timing or causal-order claim.

## No cross-provider decision engine

The MP002 association recorder does not group provider events into an authoritative distributed transaction result.

It does not calculate:

- `1/2` or `2/2` completion;
- quorum satisfaction;
- all-provider approval;
- distributed commit;
- overall operation authorization;
- cross-provider success or failure.

Those conclusions, if desired, can be derived later by analyzing the preserved signed evidence.

Such post-run interpretation would remain separate from the recorder and would not retroactively become execution authority.

## Hash-chained record

Accepted association records are linked through the recorder's hash chain.

For the MP002 scored campaign, the final record hash was:

`7002cd90fcf586dd145c6156ca3ed5da18f267138796099f536c4df53798013a`

The SHA-256 of the preserved scored `association.jsonl` is:

`d3025b6b55331dfe4505f0a1ddc82fdb1776f5dcc30449b77f683b7ed258d9e8`

The preserved association log is published under:

`../evidence/scored/association.jsonl`

## Trust model

The association holds public verification material for provider boundary events.

It does not hold the providers' execution authority merely by possessing those public keys.

The test provider private keys are published elsewhere in this laboratory package for reproducibility, but the tested architectural role of the association uses the corresponding public trust anchors to verify provider-produced evidence.

Provider A and Provider B remain independently controlled authority domains.

## What this component demonstrates

Within MP002, the association demonstrates that independently signed provider outcomes can be verified and correlated without making the association the source of provider authority.

For the divergence case, it preserves both sides of the disagreement:

- A executed under A's authority.
- B denied under B's authority.

The association records those facts rather than resolving the disagreement by taking control away from either provider.

## Limitations

The association evidence does not establish:

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

The recorder is an evidence-verification component, not a distributed transaction coordinator or provider authorization service.

## Related evidence

The scored association record is preserved in:

`../evidence/scored/association.jsonl`

The scored campaign summary is:

`../evidence/scored/SCORECARD.txt`

The locked contract and run manifest are published under:

`../configs/`

Provider-specific implementation details are documented under:

`../provider_a/`

and:

`../provider_b/`
