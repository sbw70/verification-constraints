
# AE001 MP003 Source Snapshot

This directory contains the MP003 implementation components reused by AE001.

AE001 did not invent a new provider protocol.

It composed the existing MP003 provider, relay, authorization, boundary-signaling, and association-recording behavior into the artifact-exchange campaign defined by AE001.

## Structure

```text
MP003/
├── association/
│   ├── association_recorder.py
│   ├── provider_registry.json
│   └── trust/
├── intermediary/
│   └── nuvl_multi_relay.py
├── provider_a/
│   ├── mint_authorization_a.py
│   ├── provider_a.py
│   └── provider/key material
└── provider_b/
    ├── mint_authorization_b.py
    ├── provider_b.py
    └── provider/key material
```

## Why MP003 Is Reused

The AE001 property required a working implementation in which:

- authorization artifacts are provider-specific;
- artifacts are bound to requests;
- the intermediary transports but does not decide provider admission;
- providers independently validate authorization material;
- providers control execution;
- providers generate authenticated boundary events; and
- downstream evidence can be recorded without transferring provider authority.

MP003 already supplied those mechanisms.

AE001 therefore reused the existing implementation rather than creating a second protocol for the same authority boundary.

## Provider A

`provider_a/` contains:

- Provider A runtime;
- Provider A authorization mint utility;
- Provider A issuance keypair; and
- Provider A boundary-signing keypair.

In AE001, Provider A was not the target provider for the four defined cases.

No Provider A authorization header was supplied during those requests, so Provider A generated authenticated `DENY auth_missing` background events.

A legitimate Provider A authorization was also created for N02 and deliberately presented to Provider B.

Provider B rejected it as wrong-provider authority.

## Provider B

`provider_b/` contains:

- Provider B runtime;
- Provider B authorization mint utility;
- Provider B issuance keypair; and
- Provider B boundary-signing keypair.

Provider B was the target provider for all four scored AE001 cases.

It:

- accepted valid Provider B material in B01;
- rejected altered Provider B material in N01;
- rejected Provider A material in N02; and
- accepted a fresh valid Provider B authorization again in B02.

Only the two accepted cases produced Provider B software execution.

## Intermediary

`intermediary/nuvl_multi_relay.py` is the MP003 relay used by AE001.

It handled request transport, request derivation, and provider-specific forwarding.

It did not become the provider authorization evaluator.

The relay did not:

- issue provider authorization;
- determine whether Provider B should execute;
- consume provider authorization state;
- sign provider boundary packages; or
- convert Provider A authority into Provider B authority.

## Association Recorder

`association/` contains the MP003 evidentiary recorder, provider registry, and provider public boundary keys.

The recorder received provider-generated boundary packages and preserved them as evidence.

It did not authorize execution.

AE001 also independently verified the raw provider boundary signatures rather than treating the recorder's verification fields as the final signature oracle.

## Existing Binding Model

AE001 reused the existing MP003 binding model.

The relay derives the request representation from the exact request bytes and then derives the binding from the request representation plus context.

The provider independently derives the corresponding operation identity and evaluates the presented authorization against its own provider-scoped rules.

AE001 did not introduce a new binding transform.

## Provider-Specific Authority

Provider A and Provider B remain separate authority domains.

A valid Provider A artifact is not valid Provider B authority merely because:

- the relay carries it;
- the requester possesses it;
- it is placed into a Provider B transport field; or
- the association recorder can observe it.

N02 directly exercised that boundary.

Provider B rejected valid Provider A-issued material with:

```text
DENY auth_provider_mismatch
```

and did not execute.

## Source Identity

The files in this directory are byte-identified in:

`../../configs/AE001_SOURCE_MANIFEST.json`

The source manifest records both SHA-256 values and, where available, the corresponding published Git blob identities from the MP003 source lineage.

The scored campaign also pins the source identities in:

`../../configs/AE001_RUN_MANIFEST.json`

## Laboratory Keys

The provider key material in this directory is intentionally published with the test implementation for reproduction and evidence inspection.

These keys are laboratory artifacts.

They are not production credentials.

Publication of the private laboratory keys means AE001 does not claim post-publication historical authenticity against a party holding those same keys.

## Relationship to AEBS

AE001 also preserves the architectural reference implementation separately under:

`../reference/AEBS.py`

That reference illustrates the provider-controlled artifact-exchange pattern, but the scored campaign did not treat AEBS alone as the tested implementation.

The scored implementation used the MP003 provider-specific authorization and authenticated boundary mechanisms preserved here.

## Scope

This source snapshot identifies the implementation used by AE001.

It does not expand the scored claim beyond the four-case campaign.

AE001 does not establish:

- resistance to arbitrary provider compromise;
- resistance to arbitrary intermediary compromise;
- key-compromise resistance;
- crash or reboot behavior;
- concurrency behavior;
- physical execution;
- offline delivery;
- quorum behavior;
- implementation diversity; or
- global chronology.

The bounded result is that the reused MP003 implementation supported provider-controlled artifact exchange without transferring provider authorization authority to the intermediary.
