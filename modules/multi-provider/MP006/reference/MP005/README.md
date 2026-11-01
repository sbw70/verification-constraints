# MP005 — Frozen Reference Dependencies for MP006

## Purpose

This directory preserves the MP005 implementation and supporting dependencies reused by MP006.

MP006 extends the earlier process-restart durability experiment to physical power-loss recovery.

Rather than introducing a new provider authorization or persistence mechanism, MP006 reuses the frozen MP005 implementation.

The reference directory is retained to establish source identity, implementation continuity, and dependency integrity.

It is not a separate MP006 experiment.

## Source Provenance

**Reference source commit:**

`73713f6e9ed9c95251cc69ec88ef816cab771ac0`

The original MP006 build inventory records 48 unchanged MP005 reference files.

The original source identities are preserved in:

[MP006 Original Build Manifest](../../manifests/original/SHA256SUMS.txt)

The copied implementation includes the final MP005 R3 provider hardening.

Its historical source manifests also retain earlier baseline and implementation identities.

Those historical versions must not be confused with the frozen R3 implementation.

## Directory Structure

| Directory | Contents |
|---|---|
| [provider_a/](provider_a/) | Provider A authorization, consumption, persistence, and execution |
| [provider_b/](provider_b/) | Independent Provider B authorization and policy enforcement |
| [intermediary/](intermediary/) | Stateless multi-provider request forwarding |
| [association/](association/) | Signed provider boundary verification and recording |
| [harness/](harness/) | Shared source verification, evidence collection, and scoring functions |
| [configs/](configs/) | Frozen configuration, implementation manifests, and historical locks |
| [simulation/](simulation/) | MP005 R3 simulation and independent-review source |

Each component has its own documentation.

## Frozen Implementation Identities

| Component | SHA-256 |
|---|---|
| Provider A | `79e4994c955ca842af04a8fd650a33d49de040bab95b821ded9e63e16866f2b6` |
| Provider B | `618ec76ef5dd3bfa3ba7b1ad3941ed0516a7511b72957d7efb82ec565905b605` |
| NUVL intermediary | `09d458cc8e3e13706b5463deffea0e14fcd784011a629623a09b9bd5ee04d6f4` |
| Association recorder | `fad60dfc8df53337d2e41288c2c4973442258cae4240945ebbd0aa8920550bfc` |

The complete identities of supporting files are recorded in the source and implementation manifests.

## MP006 Dependency Usage

The MP006 orchestration adapter is located outside this directory:

[mp006.py](../../mp006.py)

It imports the frozen MP005 harness functions:

- `harness/common.py`
- `harness/ledger_evidence.py`

These functions support:

- Source and harness integrity verification.
- Provider authorization preparation.
- Preserved request submission.
- Consumption-ledger inspection.
- Persistent-state validation.
- Signed boundary-event verification.
- Process identity capture.
- Replay and fresh-execution checks.
- Evidence correlation.

MP006 uses the unchanged Provider A runtime:

`provider_a/provider_a.py`

The adapter supplies experiment-specific network and persistent-state paths.

It does not replace Provider A's authorization, signing, consumption, persistence, or execution methods.

## Historical MP005 Scored Authorization

The directory also contains:

[MP005_SCORED_20261026_R3.scored.json](MP005_SCORED_20261026_R3.scored.json)

This is the original MP005 R3 scored-session authorization record.

It identifies:

**Session:** `MP005_SCORED_20261026_R3`

**Approval scope:** `R01_R02_SCORED_FULL`

**Scope enforcement:** `OPERATOR_ONLY_NOT_ENFORCED_BY_HARNESS`

The record is preserved for historical provenance.

It does not authorize new MP005 or MP006 execution.

MP006 uses separate configuration and operator authorization records.

## Authority Boundaries

The frozen implementation retains independent responsibilities.

### Providers

Each provider controls its own:

- Authorization validation.
- Cryptographic trust material.
- Local policy.
- Authorization consumption.
- Persistent spent state.
- Execution.
- Signed boundary signaling.

### NUVL Intermediary

The intermediary forwards provider-specific artifacts.

It does not issue authorization, maintain provider consumption state, or decide whether execution is permitted.

### Association Recorder

The recorder receives and verifies provider-signed boundary events.

It records observations without obtaining authority over provider execution.

### Test Harness

The harness evaluates evidence without replacing the provider's security decisions.

A successful HTTP response is not proof of authorized execution.

## Cryptographic Material

The provider directories contain Ed25519 laboratory signing and verification keys.

Authorization-issuance keys and boundary-signing keys perform separate functions.

The association component uses registered public keys to verify signed boundary observations.

The included private keys are laboratory fixtures, not production credentials.

They must not be treated as suitable for production deployment.

## Relationship to MP005 Results

The original MP005 experiment tested consumption persistence across idle forced process restart.

Its final scored campaign was:

`MP005_SCORED_20261026_R3`

Recorded results:

- Provider A: PASS.
- Provider B: PASS.

The original MP005 project contains the complete historical documentation:

- [MP005 Provenance](../../../MP005/PROVENANCE.md)
- [MP005 Results](../../../MP005/RESULTS.md)
- [MP005 Evidence](../../../MP005/evidence/)

These documents remain in the original MP005 directory.

They are not duplicated or rewritten inside this reference copy.

## Relationship to MP006

MP006 reuses Provider A's frozen authorization and persistence implementation to test a different interruption condition.

The experiment evaluates:

1. Initial consumption of valid authority.
2. Physical power interruption.
3. Preservation of raw persistent state before provider restart.
4. Recovery under a changed operating-system boot identity.
5. Rejection of previously consumed authority.
6. Successful execution using separate fresh authority.

The MP006-R01 scorer recorded PASS.

That result is established by MP006's own evidence, not by the previous MP005 outcome.

See:

[MP006-R01 Evidence](../../evidence/MP006_R01_RUN001/)

## Preservation Requirements

The reference directory must remain an identifiable copy of the validated MP005 dependencies.

Do not:

- Modify frozen provider implementations.
- Replace provider signing keys.
- Change authorization or ledger algorithms.
- Disable source-integrity verification.
- Modify historical configuration locks.
- Execute archived simulation scripts inside this reference tree.
- Reuse MP005 operator authorization for MP006.
- Write MP006 execution evidence into historical MP005 paths.
- Repair failed verification by modifying reference dependencies.

New documentation must remain distinguishable from files in the original source inventory.

## Scope of Verification

Source hashes establish the identities of the referenced files.

They do not independently establish runtime correctness or experimental success.

The frozen reference preserves the implementation used by MP006.

The MP006 experiment supplies the evidence of observed power-loss recovery, replay rejection, and fresh execution.

The two records serve different purposes and must remain separate.

## Related Documentation

- [MP006 Main README](../../README.md)
- [MP006 Configuration](../../configs/)
- [MP006 Operator Authorization](../../authorizations/)
- [MP006 Original Build Manifests](../../manifests/)
- [MP006 Experiment Evidence](../../evidence/)
