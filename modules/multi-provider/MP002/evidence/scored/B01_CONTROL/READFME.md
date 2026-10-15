# B01 Control

This directory contains the request and provider-specific authorization artifacts for the MP002 scored control case.

B01 establishes the expected behavior when both independent providers permit the same operation.

## Test condition

Both providers received the same request representation under:

`CTX_ALPHA`

Each provider was given its own valid provider-issued authorization for that request.

No provider-local deny condition was triggered.

## Contents

- `request.json` — exact request bytes used for the scored B01 submission.
- `SCORED_B01_provider_a_auth.json` — Provider A authorization package.
- `SCORED_B01_provider_a_auth.json.b64` — encoded Provider A authorization transmitted through the relay.
- `SCORED_B01_provider_b_auth.json` — Provider B authorization package.
- `SCORED_B01_provider_b_auth.json.b64` — encoded Provider B authorization transmitted through the relay.

## Scored authorization identifiers

Provider A:

`6a7394b62385b6ea2ff9f72a0271c27e75b1c4081d1aa4ff3eb509468587354a`

Provider B:

`84064da5fac9cb562ac1f85c96db3fe334725f595e7ed6967babd9ec6df195ea`

The request representation was:

`7bf65d11928d3e32ae1245ce5a6a2f8aeb12ba53644b868630b9e814adc7e35f`

## Result

**PASS**

The relay accepted the request and returned HTTP `204`.

The association recorded valid signed boundary events for both providers:

- Provider A: `START`
- Provider A: `COMPLETE`
- Provider B: `START`
- Provider B: `COMPLETE`

All four recorded submissions passed association signature verification.

The final provider-local state also shows one B01 execution and one consumed B01 authorization at each provider.

## What B01 establishes

B01 is the control for MP002.

It demonstrates that, with the MP002 deployment and evidence path in place, both providers can independently validate their own authorization and execute the same operation when their local policy permits it.

This provides the baseline against which D01 is compared.

The important difference between B01 and D01 is Provider B's local policy decision. The relay, association recorder, Provider A runtime, authorization format, and surrounding multi-provider path were not changed to create the divergent result.

## What B01 does not establish

B01 does not by itself demonstrate:

- provider-local policy divergence;
- cross-provider atomicity;
- globally synchronized event ordering;
- implementation diversity;
- crash-window behavior;
- concurrent authorization use;
- power-loss behavior;
- compromised-provider containment;
- physical actuation or independent hardware-witness evidence.

Those claims are outside the scope of this control case.

## Related evidence

The scored association log is preserved in:

`../association.jsonl`

Final Provider A state:

`../final_provider_a/`

Final Provider B state:

`../final_provider_b/`

The corresponding divergent case is:

`../D01_POLICY_DIVERGENCE/`

The scored campaign summary is:

`../SCORECARD.txt`

Integrity information for the scored evidence set is:

`../SHA256SUMS.txt`
