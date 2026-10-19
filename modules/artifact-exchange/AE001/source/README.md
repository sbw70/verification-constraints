# AE001 Source

This directory preserves the source material used to define and execute AE001 — Provider-Controlled Artifact Exchange.

It contains two distinct source sets:

```text
source/
├── MP003/
└── reference/
```

They serve different purposes and should not be conflated.

## `MP003/`

`MP003/` contains the actual provider, relay, authorization-minting, association-recording, registry, and laboratory key material used by the AE001 campaign.

Those components supplied the tested behavior for:

- provider-specific authorization issuance;
- request-bound authorization;
- Provider A / Provider B separation;
- provider-side authorization evaluation;
- provider-controlled spent state;
- provider-controlled software execution;
- authenticated provider `START`, `COMPLETE`, and `DENY` packages; and
- downstream evidence recording without transferring provider authority.

AE001 reused the existing MP003 protocol and implementation rather than creating a new provider protocol.

The scored campaign depended on this source set.

## `reference/`

`reference/` contains:

```text
AEBS.py
```

`AEBS.py` is the compact architectural reference for the Provider-Controlled Artifact Exchange and Boundary Signaling model.

It illustrates the intended separation between:

- requester;
- intermediary conveyance;
- provider evaluation;
- provider execution initiation; and
- provider-generated boundary signaling.

It is not the sole implementation used by the scored campaign.

The provider-specific cryptographic and lifecycle controls exercised by AE001 came from the MP003 source set.

## Tested Composition

The AE001 campaign combined the existing MP003 components in the following roles:

```text
Requester
    |
    v
Intermediary / Relay
    |
    +----> Provider A
    |
    +----> Provider B
              |
              v
        Provider-controlled
        evaluation/execution

Provider-generated boundary packages
              |
              v
      Association recorder
```

Provider B was the target provider for the four defined cases.

Provider A remained a separate provider authority and supplied both background denial evidence and the valid Provider A authorization used in the wrong-provider N02 case.

## Authority Boundary

The source layout reflects the authority boundary being tested.

The relay can:

- receive request material;
- derive the existing request representation and binding;
- transport provider-specific authorization material; and
- forward requests to providers.

The relay does not thereby gain authority to:

- issue provider authorization;
- decide provider admission;
- consume provider authorization state;
- initiate provider execution; or
- generate provider boundary statements.

Those functions remain provider-controlled.

The association recorder likewise records and verifies provider-generated evidence without gaining provider execution authority.

## Source Identity

Exact source identities are recorded in:

`../configs/AE001_SOURCE_MANIFEST.json`

The source manifest records SHA-256 values for the preserved source files and, where applicable, the published Git identities from the MP003 lineage.

The scored run additionally pins the campaign source and script identities through:

`../configs/AE001_RUN_MANIFEST.json`

## Laboratory Keys

The MP003 source snapshot includes provider issuance and boundary-signing laboratory keys.

They are intentionally published as part of the reproducible test package.

They are not production credentials.

Because the private laboratory keys are public, AE001 does not claim post-publication historical authenticity against a party possessing those keys.

## Modification Boundary

AE001 did not replace the core MP003 provider authorization logic.

Campaign-specific orchestration is kept separately under:

`../scripts/`

The launcher adjusts deployment-specific configuration such as host addresses, ports, fresh run-state paths, and observational relay auditing.

The provider decision logic, provider authorization model, request-binding model, and provider boundary-signing behavior remain the copied MP003 implementation.

## Related Material

Campaign configuration and locked identities:

`../configs/`

Execution and scored evidence:

`../evidence/`

Campaign result:

`../RESULTS.md`

Campaign provenance:

`../PROVENANCE.md`

## Scope

This directory identifies the implementation material used by AE001.

It does not by itself establish the scored result.

The AE001 claim depends on the combination of:

- preserved source;
- locked campaign definition;
- scored execution;
- raw provider-signed boundary evidence;
- provider state;
- execution records; and
- retained provenance.

The tested result remains limited to the defined four-case software campaign.
