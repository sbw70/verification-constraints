# AE001 Provider B Source

This directory contains the copied MP003 Provider B runtime, authorization mint utility, and laboratory keys used by AE001.

Provider B was the target provider for all four defined AE001 cases.

The campaign tested whether provider-issued authorization material could traverse the intermediary while Provider B retained exclusive control over artifact evaluation, authorization consumption, software execution, and authenticated boundary signaling.

## Contents

| File | Role | SHA-256 |
|---|---|---|
| `provider_b.py` | Provider B runtime | `5e0ab4b79df4c97bc7bc324d63da85711728d625b82306cdce6c92592e2ee13e` |
| `mint_authorization_b.py` | Provider B authorization mint | `1b3ba1314761a5489817c660cdc4d62e65ba77deae2bfce2fdce48c228f98deb` |
| `provider_b_issuance_private.pem` | Provider B issuance signing key | `fb450986458ee062e1747471cfef731a743b6d3915b1d86bbf0f4c2e7e1e3433` |
| `provider_b_issuance_public.pem` | Provider B issuance verification key | `07ba26931a6112826f39fdc9a286562f608f394b4f8de4d26f48751855d8fe64` |
| `provider_b_private.pem` | Provider B boundary-signing key | `02e145e18080e3a2dc230d70c6de71f33fa4ff7ec7fed829f313292a845b95d7` |
| `provider_b_public.pem` | Provider B boundary verification key | `bcb4441a3ad143b5a3d646189d15ba806340c52530ba9b5ef4e19f30e0c59e47` |

These are laboratory keys published intentionally with the test source for reproduction.

They are not production credentials.

## Deployment in AE001

Provider B ran on:

```text
Host: Xer0trust2
Address: 192.168.1.107
Endpoint: 192.168.1.107:19090/ingest
```

The runtime was deployed into a fresh AE001-specific run directory under:

```text
/home/seth/ARTIFACT_EXHANGE/RUN_ID
```

Canonical MP003 source and state were not used as writable campaign state.

The scored deployment identity is preserved in:

`../../../evidence/scored/AE001_SCORED_20261018_R1/provider_b_deployment.json`

## Two Provider-Controlled Key Roles

Provider B uses separate Ed25519 keypairs for authorization issuance and boundary signaling.

### Authorization issuance

`provider_b_issuance_private.pem` is used by `mint_authorization_b.py` to sign Provider B authorization artifacts.

`provider_b_issuance_public.pem` is loaded by Provider B to verify those artifacts.

The relay does not hold or exercise Provider B issuance authority merely because it transports the resulting artifact.

### Boundary signaling

`provider_b_private.pem` is used by the Provider B runtime to sign provider-generated boundary events.

`provider_b_public.pem` is used to verify those events.

Boundary signaling is distinct from authorization issuance.

The provider evaluates the incoming authorization first and then generates its own authenticated statement about the resulting execution boundary.

## Provider B Decision Path

`provider_b.py` is the copied MP003 Provider B runtime used by AE001.

For incoming authorization material, Provider B independently checks the properties required by the existing protocol, including:

- provider identity;
- authorization identity;
- issuance signature;
- request representation;
- request binding and context;
- provider-local policy;
- spent state; and
- local authorization lifecycle.

The relay does not make these checks on Provider B's behalf.

If Provider B accepts the authorization, Provider B controls state consumption and software execution.

If Provider B rejects the authorization, it emits a signed `DENY` and does not consume that authorization as valid authority.

## AE001 Case Results

Provider B was exercised by all four scored cases.

| Case | Material presented to Provider B | Provider B result |
|---|---|---|
| B01 | Valid fresh Provider B authorization bound to the request | `START` → one software execution → `COMPLETE` |
| N01 | Valid Provider B authorization with one signature byte altered | `DENY auth_bad_sig` |
| N02 | Valid fresh Provider A authorization presented in the Provider B header | `DENY auth_provider_mismatch` |
| B02 | Fresh valid Provider B authorization after both negative cases | `START` → one software execution → `COMPLETE` |

All four cases passed their defined criteria.

## B01 — Valid Provider B Authority

B01 presented a legitimate fresh Provider B authorization matching the request.

Provider B accepted it and generated authenticated:

```text
START
COMPLETE
```

One software execution was recorded and one authorization entered Provider B's spent state.

This is the first positive bookend.

## N01 — Altered Signature

N01 began with a legitimate fresh Provider B authorization.

The original authorization was preserved separately.

The transmitted copy had the first decoded signature byte altered while the authorization fields remained otherwise unchanged.

Provider B independently rejected it with authenticated:

```text
DENY auth_bad_sig
```

Provider B's execution and spent-authority state remained unchanged.

The relay transported the artifact but did not decide that the signature was invalid.

## N02 — Wrong Provider Authority

N02 presented a legitimate fresh Provider A authorization in the Provider B authorization header.

Provider B rejected it with authenticated:

```text
DENY auth_provider_mismatch
```

No Provider B execution occurred and no Provider B authorization state was consumed.

The result demonstrates the tested provider-scoping property:

valid Provider A authority does not become Provider B authority through transport or presentation to Provider B.

## B02 — Post-Negative Positive Bookend

B02 presented a new legitimate Provider B authorization after N01 and N02.

Provider B again generated authenticated:

```text
START
COMPLETE
```

and performed one software execution.

This demonstrated that the two negative cases had not damaged or consumed the provider state needed for a later legitimate operation.

## Final Provider B State

Across the scored campaign, Provider B:

```text
executions: 2
spent authorizations: 2
```

Those executions correspond only to B01 and B02.

Neither N01 nor N02 changed Provider B's execution or spent-authority state.

Final Provider B evidence is under:

`../../../evidence/scored/AE001_SCORED_20261018_R1/final/provider_b/`

## Boundary Evidence

Provider B generated its own signed boundary packages.

For the scored run, those were:

- B01: `START`, `COMPLETE`
- N01: `DENY auth_bad_sig`
- N02: `DENY auth_provider_mismatch`
- B02: `START`, `COMPLETE`

The association recorder preserved those packages.

The scored harness also independently verified the raw Provider B signatures rather than relying on the recorder's classification fields as the signature-verification oracle.

## Provider State

AE001 used fresh, isolated runtime state for the campaign.

The provider's existing persistence behavior was not replaced by the relay or scoring harness.

Provider B controlled its own spent-authority and execution records.

The negative cases were required to leave those records byte-unchanged.

The positive cases were required to add exactly one execution and one spent authorization each.

## Provider Authority

Provider B's authority does not arise from:

- relay delivery;
- the requester's possession of an artifact;
- the association recorder;
- HTTP `204`;
- correlation records; or
- a valid authorization belonging to another provider.

Provider B itself evaluates whether the presented material constitutes Provider B authority.

Only after successful provider-side evaluation does Provider B initiate its software execution and generate authenticated execution-boundary signals.

## Source Identity

The files in this directory are copied MP003 source used by AE001.

Their exact SHA-256 identities are recorded in:

`../../../configs/AE001_SOURCE_MANIFEST.json`

The scored campaign source and configuration identities are pinned by:

`../../../configs/AE001_RUN_MANIFEST.json`

Campaign provenance is documented in:

`../../../PROVENANCE.md`

## Scope

AE001 establishes Provider B behavior only for the defined four-case software campaign.

It does not test:

- compromise of Provider B's issuance key;
- compromise of Provider B's boundary-signing key;
- arbitrary compromise of the Provider B host;
- crash or reboot recovery;
- power-loss behavior;
- concurrent authorization use;
- delayed or offline delivery;
- physical actuation; or
- every possible malformed authorization.

The bounded result is that, in the tested configuration, Provider B retained control over whether transported verification material could produce Provider B software execution.
