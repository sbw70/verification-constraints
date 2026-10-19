# AE001 Provider A Source

This directory contains the copied MP003 Provider A runtime, authorization mint utility, and laboratory keys used by AE001.

Provider A was not the target provider in the four scored AE001 cases.

Its role in AE001 was to remain independently provider-scoped while the relay delivered no Provider A authorization material.

## Contents

| File | Role | SHA-256 |
|---|---|---|
| `provider_a.py` | Provider A runtime | `c875582b275f270b8e68af69ed4ee84896e83815cdf33b7d7c5ccc813fe2e606` |
| `mint_authorization_a.py` | Provider A authorization mint | `1a485e8a5d3de854cb31303b8d3bf1339ef72cb9b42f308490bd02519e76d7ec` |
| `provider_a_issuance_private.pem` | Provider A issuance signing key | `37f808b6901f5020fb7b68924217d76f7923d898e44913a6338008d85ac15fd8` |
| `provider_a_issuance_public.pem` | Provider A issuance verification key | `a52276369981962b878311ec4e33186af25ac10cd359fafbc760e118e607ad71` |
| `provider_a_private.pem` | Provider A boundary-signing key | `f4fb81ff6901b6f9ef8ea4f870430760cf7cdc2eb28dff74125e277fa6465ff9` |
| `provider_a_public.pem` | Provider A boundary verification key | `4f9f01b0296f75a7acf8c3fd11bf7f27d75f0526e7912a02d0a725b1e6fbaa19` |

These are laboratory keys published intentionally with the test source for reproduction.

They are not production credentials.

## Deployment in AE001

Provider A ran on:

```text
Host: Xer0trust-3
Address: 192.168.1.118
Endpoint: 192.168.1.118:19090/ingest
```

The runtime was deployed into a fresh AE001-specific run directory under:

```text
/home/seth/ARTIFACT_EXHANGE/RUN_ID
```

Canonical MP003 source and state were not used as writable campaign state.

The scored deployment identity is preserved in:

`../../../evidence/scored/AE001_SCORED_20261018_R1/provider_a_deployment.json`

## Two Provider-Controlled Key Roles

Provider A uses separate Ed25519 keypairs for two distinct purposes.

### Authorization issuance

`provider_a_issuance_private.pem` is used by the Provider A mint utility to issue Provider A authorization artifacts.

`provider_a_issuance_public.pem` is used by Provider A to verify those artifacts.

Issuance authority is provider-specific.

A Provider A authorization does not become Provider B authority merely because it is transported to Provider B.

### Boundary signaling

`provider_a_private.pem` is used by the Provider A runtime to sign provider-generated boundary events.

`provider_a_public.pem` is used to verify those events.

Boundary-signing authority is separate from authorization issuance.

## Provider A Behavior in AE001

AE001 targeted Provider B through the Provider B authorization header.

No Provider A authorization header was supplied in any of the four defined cases.

Provider A therefore produced an authenticated:

```text
DENY auth_missing
```

for each case.

These Provider A denials are background path evidence.

They are not additional scored cases.

Across the scored run:

- Provider A generated four authenticated denials;
- Provider A executed zero operations; and
- Provider A ended with zero spent authorizations.

## N02 and Provider Separation

N02 used a legitimate fresh Provider A authorization artifact.

That artifact was deliberately placed in the Provider B authorization header and transported to Provider B.

Provider A did not authorize Provider B to execute.

Provider B independently evaluated the presented material and rejected it with:

```text
DENY auth_provider_mismatch
```

This demonstrates the tested provider-scoping property:

a valid authorization issued by Provider A does not become Provider B authority through intermediary conveyance.

## Provider A Mint Utility

`mint_authorization_a.py` creates Provider A authorization artifacts using Provider A's issuance private key.

In AE001, it was used to create the legitimate Provider A artifact used for the N02 wrong-provider case.

The mint utility does not grant authority to the relay.

The resulting artifact remains Provider A-issued material and is evaluated according to the receiving provider's own rules.

## Provider Runtime

`provider_a.py` is the unchanged copied MP003 Provider A implementation used by the campaign.

It independently:

- derives and checks request binding;
- validates provider identity;
- verifies Provider A authorization signatures using Provider A's issuance public key;
- checks request representation and context;
- checks spent state;
- controls consumption;
- controls software execution; and
- generates signed boundary events.

The relay does not perform these provider-side admission functions on Provider A's behalf.

## State and Execution Evidence

AE001 preserves Provider A state and execution snapshots around each case.

For the scored run, Provider A's final state shows:

```text
spent authorizations: 0
executions: 0
```

The final Provider A runtime evidence is under:

`../../../evidence/scored/AE001_SCORED_20261018_R1/final/provider_a/`

## Source Identity

The files in this directory are copied MP003 source.

Their exact SHA-256 identities are recorded in:

`../../../configs/AE001_SOURCE_MANIFEST.json`

The scored campaign configuration and source identities are also pinned by:

`../../../configs/AE001_RUN_MANIFEST.json`

## Scope

Provider A's AE001 role supports provider separation and background path evidence.

AE001 does not test:

- compromise of Provider A's issuance key;
- compromise of Provider A's boundary key;
- compromise of the Provider A host;
- Provider A execution under a positive AE001 case;
- crash or reboot recovery;
- concurrent authorization use; or
- physical execution.

The scored claim remains bounded to the defined AE001 artifact-exchange campaign.
