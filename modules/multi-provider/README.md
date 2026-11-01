# Multi-Provider — Provider-Controlled Authority Boundaries

## Overview

The Multi-Provider module demonstrates how independent systems can receive related requests without sharing or transferring execution authority.

A neutral intermediary forwards provider-specific artifacts.

Each provider independently determines whether an operation is authorized.

Providers retain control over their own authorization, policy, consumption state, and execution.

An association component records provider-originated boundary events without acquiring authority over the providers.

The architecture separates:

- Request transport.
- Provider authorization.
- Execution.
- Boundary observation.
- Evidence verification.

The implementation is provided as a Python reference, with subsequent experiments extending the architecture across physical machines, independent provider policies, compromised credentials, and persistent execution authority.

## Architecture

The general request path is:

```text
                   Requester
                       |
                       v
               NUVL Intermediary
                       |
             +---------+---------+
             |         |         |
             v         v         v
         Provider A Provider B Provider C
             |         |         |
             +---------+---------+
                       |
                       v
                  Association
                (Evidence Only)
```

Each provider independently evaluates the material addressed to its boundary.

A decision by Provider A does not authorize execution by Provider B.

The intermediary does not create or enlarge provider authorization.

The association component records provider-originated events without becoming a decision authority.

The architecture does not require shared signing keys, shared provider policies, or a centralized authorization database.

## Reference Implementation

**File:** [MPBS.py](MPBS.py)

The original reference implements the architectural roles in a single Python program.

It includes:

- A requester.
- A neutral forwarding intermediary.
- Three provider endpoints.
- Provider-specific HMAC verification.
- Provider-controlled execution decisions.
- Boundary-event signaling.
- A non-authoritative association component.

The reference demonstrates the separation of responsibilities.

It is not a production-hardened deployment.

The subsequent MP001–MP006 experiments provide more specific implementations, controls, and evidence.

## Experimental Progression

The numbered experiments test distinct properties of the architecture.

| Experiment | Primary question | Recorded result |
|---|---|---|
| [MP001](MP001/) | Does authority separation survive deployment across independent networked hosts? | PASS |
| [MP002](MP002/) | Can providers make different policy decisions without another component overriding them? | PASS |
| [MP003](MP003/) | Can compromised Provider A authorization credentials create authority at Provider B? | PASS — cross-provider authority not obtained |
| [MP004](MP004/) | Can provider-signed boundary evidence be verified independently of the recorder? | PASS |
| [MP005](MP005/) | Does consumed authority remain spent across provider-process restart? | PASS — Providers A and B |
| [MP006](MP006/) | Does consumed authority remain spent after physical power loss and host recovery? | PASS — Provider A |

Each result applies to the implementation, conditions, and acceptance criteria of its experiment.

A PASS does not establish properties outside the corresponding test scope.

### MP001 — Distributed Authority Separation

[Documentation](MP001/README.md) | [Results](MP001/RESULTS.md)

MP001 separates the requester, intermediary, providers, and association recorder across networked machines.

It evaluates whether the independently controlled provider boundaries remain effective after physical distribution.

The scored baseline and negative cases passed.

An initial Provider-B-unavailable test did not establish its required precondition. That attempt was preserved, and a corrected retry passed.

### MP002 — Independent Provider Policy

[Documentation](MP002/README.md) | [Results](MP002/RESULTS.md)

MP002 demonstrates that independently authorized providers can reach different execution decisions.

Provider A permitted and executed the operation.

Provider B denied the operation under its own local policy.

Neither the intermediary nor the association component overrode those decisions.

### MP003 — Compromised Provider Credentials

[Documentation](MP003/README.md) | [Results](MP003/RESULTS.md)

MP003 tests the consequences of compromising Provider A's authorization-issuance private key.

The compromised key enabled execution at Provider A.

It did not authorize execution at Provider B.

Provider B rejected Provider A authority and incorrectly relabeled authorization material.

Provider B's legitimate authorization continued to function.

The experiment demonstrates a tested cross-provider authority boundary, not immunity to every possible lateral attack.

### MP004 — Independent Evidence Verification

[Documentation](MP004/README.md) | [Results](MP004/RESULTS.md)

MP004 evaluates whether preserved provider-signed boundary evidence can be authenticated without relying on the association recorder's conclusions.

An independent offline verifier evaluates the original signed material against pinned provider trust keys and defined assertions.

The seven required scored cases passed.

This establishes evidence-verification independence within the tested scope.

It does not convert the verifier into an authorization authority.

### MP005 — Durable Authority Across Process Restart

[Documentation](MP005/README.md) | [Results](MP005/RESULTS.md)

MP005 introduces provider-local durable consumption ledgers and persistent spent-authority state.

The experiment evaluates whether consumed authority remains spent after termination and restart of the provider process.

The final R3 scored campaign recorded:

- Provider A: PASS.
- Provider B: PASS.
- Exact replay denied without another consumption or execution.
- Separate fresh authorization accepted and executed.

The implementation also includes offline reconciliation and fail-closed startup characterization.

Process restart does not establish physical power-loss durability.

### MP006 — Durable Authority Across Physical Power Loss

[Documentation](MP006/README.md) | [Scored evidence](MP006/evidence/MP006_R01_RUN001/)

MP006 extends the persistence experiment to a documented physical power interruption.

Provider A consumed an authorization and recorded execution before the interruption.

Following host recovery:

- The operating-system boot identifier had changed.
- Raw persistent state was preserved before provider restart.
- The original authorization remained spent.
- Exact replay produced a signed `auth_spent` denial.
- Replay caused no additional consumption or execution.
- Separate fresh authority executed successfully.

**Scored result:** `PASS`

The independent witness observed network unavailability and recovery.

Physical disconnection was operator-attested rather than measured using a dedicated electrical instrument.

The result does not establish resistance to complete-history rollback or every possible interrupted-write condition.

## Authority Model

### Intermediary

The intermediary may:

- Receive requests.
- Calculate mechanical request bindings.
- Forward provider-specific artifacts.
- Route requests to independent providers.

It must not:

- Originate provider authorization.
- Hold provider signing secrets.
- Override provider rejection.
- Convert one provider's authorization into another's.
- Maintain provider execution authority.
- Treat transport completion as authorization.

A successful HTTP forwarding response is not proof that a provider executed an operation.

### Providers

Each provider independently controls:

- Authorization issuance and validation.
- Provider-specific trust material.
- Local policy.
- Authorization consumption.
- Replay enforcement.
- Execution.
- Provider-originated boundary signaling.

Provider decisions are not inherited across boundaries.

### Association

The association component may receive, verify, correlate, and preserve provider-originated boundary events.

It does not:

- Issue authorization.
- Approve execution.
- Override provider decisions.
- Create transitive provider trust.
- Convert completion counts into authority.

A signed event is evidence of a statement verified against the registered provider key.

It is not independent hardware execution attestation.

## Persistence and Recovery

The later experiments introduce provider-local durable authorization consumption.

The provider records consumption before reporting successful execution initiation.

The persistent history supports enforcement of single-use constraints across tested restart and recovery conditions.

The intermediary does not maintain this consumption ledger.

The architecture distinguishes persistent provider authority state from the evidence collected by the test harness.

The MP005 and MP006 evidence must be evaluated separately because they test different failure conditions.

## Evidence and Verification

Each experiment maintains its own evidence, configuration, and integrity records.

Depending on the experiment, these include:

- Authorization artifacts.
- Signed provider boundary events.
- Persistent consumption ledgers.
- Spent-authority snapshots.
- Execution logs.
- Provider process identities.
- Configuration and source manifests.
- SHA-256 inventories.
- Scored case results.

The recorded PASS classifications are supported by the corresponding experiment directories.

Evidence verification must not rely exclusively on HTTP acknowledgments or recorded PASS labels.

Raw evidence and defined acceptance criteria remain the basis for assessing the supported claims.

Historical files must not be modified to make later results appear consistent with earlier configurations.

## AI-Assisted Integration Constraints

[AI_ASSIST.md](AI_ASSIST.md) defines architectural restrictions for AI-assisted development.

The principal constraint is that independent provider boundaries must remain independent.

AI agents and development tools must not introduce shared authority, shared provider secrets, intermediary-side authorization, or transitive provider trust to simplify implementation.

A passing software test does not justify violating the architecture.

## Repository Navigation

| Path | Contents |
|---|---|
| [MPBS.py](MPBS.py) | Original executable architectural reference |
| [AI_ASSIST.md](AI_ASSIST.md) | AI-assisted development constraints |
| [MP001/](MP001/) | Split-host authority separation |
| [MP002/](MP002/) | Independent provider policy |
| [MP003/](MP003/) | Compromised provider credentials |
| [MP004/](MP004/) | Independent offline evidence verification |
| [MP005/](MP005/) | Process-restart authority persistence |
| [MP006/](MP006/) | Physical power-loss authority persistence |

Each numbered experiment should be reviewed within its own directory.

## Architectural Limitations

The framework does not claim to eliminate every security risk arising from compromised components or providers.

In particular:

- Compromising a provider's legitimate signing authority can compromise that provider.
- A compromised intermediary can disrupt, suppress, duplicate, or alter forwarded traffic.
- Provider availability is not guaranteed.
- Provider policy correctness remains provider-controlled.
- Signed software evidence is not independent physical execution attestation.
- Hash-linked local records do not inherently prevent replacement of an entire consistent history.
- Successful results from one provider do not automatically establish equivalent behavior at another.

These limitations are not exceptions to the authority model.

They define its tested and untested boundaries.

## Licensing

Copyright 2026 Seth Brian Wells. All rights reserved.

This module is not released under the Apache 2.0 license applied to the repository root.

Commercial licensing terms apply.

Non-commercial research evaluation may be available upon request.

See the repository licensing documentation for applicable terms.
