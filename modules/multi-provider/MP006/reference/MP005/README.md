# MP005 — Frozen Reference Dependencies

## Purpose

This directory contains the frozen MP005 implementation and supporting files reused by MP006.

MP006 extends the earlier process-restart experiment to physical power-loss recovery.

It reuses the MP005 provider authorization, durable consumption ledger, signature verification, boundary signaling, and evidence-validation functions.

MP006 does not introduce a replacement authorization or persistence algorithm.

The reference files must remain distinguishable from MP006-specific code and experimental evidence.

## Directory Structure

| Directory | Purpose |
|---|---|
| [provider_a/](provider_a/) | Provider A authorization, consumption, execution, and signed boundary signaling |
| [provider_b/](provider_b/) | Independent Provider B implementation and policy enforcement |
| [intermediary/](intermediary/) | Stateless NUVL multi-provider forwarding |
| [association/](association/) | Signed boundary-event verification and recording |
| [harness/](harness/) | Shared verification, evidence, and scoring functions |
| [configs/](configs/) | Frozen source identities, contracts, manifests, and historical locks |
| [simulation/](simulation/) | Historical R3 simulation and independent-review implementation |

Each component has its own documentation.

## Frozen Source Identity

The original MP006 build records identify 48 unchanged reference files copied from MP005.

**Reference commit:**

`73713f6e9ed9c95251cc69ec88ef816cab771ac0`

### Primary Implementation Hashes

| Component | SHA-256 |
|---|---|
| Provider A | `79e4994c955ca842af04a8fd650a33d49de040bab95b821ded9e63e16866f2b6` |
| Provider B | `618ec76ef5dd3bfa3ba7b1ad3941ed0516a7511b72957d7efb82ec565905b605` |
| NUVL relay | `09d458cc8e3e13706b5463deffea0e14fcd784011a629623a09b9bd5ee04d6f4` |
| Association recorder | `fad60dfc8df53337d2e41288c2c4973442258cae4240945ebbd0aa8920550bfc` |

Complete identities are retained in the frozen manifests.

[Original MP006 build inventory](../../manifests/original/SHA256SUMS.txt)

Documentation added after the original inventory is not part of that historical manifest.

## MP006 Dependency Use

The MP006 adapter is located at:

[mp006.py](../../mp006.py)

It imports the frozen MP005 harness functions from:

- `harness/common.py`
- `harness/ledger_evidence.py`

The adapter invokes the frozen source and harness verification functions before normal operations.

For Provider A execution, it imports:

`provider_a/provider_a.py`

The adapter changes only the deployment-specific runtime values:

- Listening host.
- Listening port.
- Association endpoint.
- Consumption-ledger path.
- Spent-state path.
- Execution-log path.

It does not replace Provider A's authorization, signature, consumption, or execution methods.

## Historical R3 Authorization Record

The root also contains:

[MP005_SCORED_20261026_R3.scored.json](MP005_SCORED_20261026_R3.scored.json)

This file preserves a historical MP005 scored-session authorization record.

It identifies:

**Session:** `MP005_SCORED_20261026_R3`

**Scope:** `R01_R02_SCORED_FULL`

**Scope enforcement:** `OPERATOR_ONLY_NOT_ENFORCED_BY_HARNESS`

The record is historical.

It is not authorization to launch MP006, reuse MP005 state, or repeat scored experiments.

MP006 has its own configuration and operator authorization.

## Authority Boundaries

The frozen implementation preserves separate responsibilities.

**Providers**

Validate their own authorization artifacts, enforce consumption constraints, and control execution.

**NUVL intermediary**

Forwards provider-specific material without acquiring execution authority.

**Association recorder**

Verifies and records signed boundary events without authorizing execution.

**Test harness**

Collects and evaluates evidence without overriding provider decisions.

The intermediary must not receive provider signing keys.

A successful HTTP response must not be interpreted as proof of provider execution.

## Laboratory Cryptographic Material

The provider directories include Ed25519 laboratory key pairs.

These are published testing fixtures.

They are not production credentials.

The association directory contains the corresponding boundary-verification public keys.

Authorization-issuance keys and boundary-signing keys serve different purposes and must not be interchanged.

## MP005 and MP006 Scope

### MP005

The final scored R3 experiment tested whether consumed authority remained spent across an idle forced provider-process restart.

Its recorded result was PASS for Provider A and Provider B within the defined scope.

### MP006

MP006 separately tested whether Provider A retained consumed authority after physical power interruption and host recovery.

The R01 experiment recorded:

- Original authorization consumed.
- Persistent state preserved across the observed interruption.
- Original authorization replay denied.
- No additional execution caused by replay.
- Separate fresh authorization executed successfully.

**MP006-R01 status:** `PASS`

The MP006 result is established by its own evidence, not by the historical MP005 result.

## Preservation Rules

- Do not modify frozen provider or harness implementation files.
- Do not replace laboratory keys to make verification pass.
- Do not repair historical persistent state.
- Do not execute historical simulation scripts inside this reference tree.
- Do not reuse historical MP005 authorization records.
- Do not redirect MP006 writes into MP005 evidence directories.
- Do not update historical source hashes after documentation changes.
- Preserve mismatches and verification failures for review.

This directory is a dependency reference, not an independent MP006 execution environment.

## Related Documentation

- [MP006 source adapter](../../mp006.py)
- [MP006 configuration](../../configs/)
- [MP006 operator authorization](../../authorizations/)
- [MP006 original build manifests](../../manifests/original/)
- [MP006-R01 scored evidence](../../evidence/MP006_R01_RUN001/)
