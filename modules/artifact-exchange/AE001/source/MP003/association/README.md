# AE001 Association Recorder Source

This directory contains the copied MP003 association-recorder implementation used by AE001.

It is preserved as tested source, not as a new AE001 authorization component.

## Contents

```text
association/
├── association_recorder.py
├── provider_registry.json
└── trust/
    ├── provider_a_public.pem
    └── provider_b_public.pem
```

## Role

The association recorder receives provider-generated boundary packages and preserves them as evidence.

It does not:

- issue authorization;
- evaluate provider authorization artifacts for execution;
- decide whether an operation should run;
- initiate provider execution; or
- enlarge provider authority.

Provider authority remains provider-controlled.

The recorder's role is evidentiary.

## `association_recorder.py`

This is the MP003 association-recorder implementation used by AE001.

During the campaign it received signed provider boundary packages directly from the providers and recorded the resulting association data.

The recorder verifies provider signatures using the configured provider registry and public boundary-signing keys.

That verification supports evidence handling only.

It is not the execution decision.

## `provider_registry.json`

The provider registry maps provider identity information to the corresponding trusted public boundary-signing material used by the recorder.

Provider A and Provider B remain distinct provider identities.

The registry does not make either provider interchangeable with the other and does not confer authorization authority on the recorder.

## `trust/`

The `trust/` directory contains the public provider boundary-signing keys used by the recorder.

Those keys verify provider-generated boundary packages.

They are separate from the provider authorization-issuance keys used to create request-bound authorization artifacts.

## AE001 Use

AE001 used the association recorder as a separate process from the relay.

The relay transported request and authorization material.

The providers independently evaluated their authorization material and generated signed boundary events.

The association recorder received those provider-generated events separately and preserved them.

For the scored run, the session contained:

- four Provider A authenticated denials; and
- six Provider B boundary events across the four defined cases.

Those records were correlated with request identity, provider state, execution evidence, and raw signed packages.

## Independent Verification

The AE001 scored harness independently verified the raw provider boundary signatures.

The recorder's own verification fields were not treated as the independent signature-verification oracle.

This distinction matters because recording evidence and independently checking that evidence are separate functions.

## Source Identity

The files in this directory are copied MP003 source used by AE001.

Their exact identities are recorded in:

`../../../configs/AE001_SOURCE_MANIFEST.json`

and:

`../../../configs/AE001_RUN_MANIFEST.json`

The campaign provenance is documented in:

`../../../PROVENANCE.md`

## Scope

This source supports provider-specific signed evidence collection.

It does not establish:

- authorization authority in the recorder;
- global event chronology;
- trusted external timestamping;
- association-chain integrity as a scored AE001 property;
- resistance to recorder-host compromise; or
- independence of the recorder host from the relay host.

In AE001, the association recorder and relay ran as separate processes on the same Raspberry Pi host.

No stronger process- or host-isolation claim is made.
