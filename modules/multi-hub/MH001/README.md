# MH001 — Multi-Hub Authority Persistence Experiment

## Overview

MH001 is a reproducible, two-provider, two-hub experiment examining whether a change in network forwarding path can restore execution authority that a provider has already consumed.

The experiment uses mechanical forwarding hubs, independently controlled provider authorization, durable consumption records, and an independent signed-event observer.

**Implementation:** MH001 R4.3  
**Scored session:** `MH001_R43_RUN001`  
**Live execution:** November 7–8, 2026 UTC  
**Functional result:** PASS  
**Procedural status:** Two required checkpoints were not separately documented.

The tested question was straightforward:

**Can the same consumed authorization execute again if the requester changes hubs?**

In the recorded experiment, it did not.

## 1. Directory Structure

```text
MH001/
├── README.md
├── MH001_R43_RUN001/
│   ├── README.md
│   ├── frozen_R43/
│   ├── configs/
│   ├── trust/
│   ├── association/
│   ├── authorizations/
│   ├── rehearsal_inputs/
│   ├── rehearsal_requests/
│   ├── t01_inputs/
│   ├── t01_requests/
│   ├── t04_inputs/
│   ├── t04_requests/
│   ├── validation/
│   ├── observer_support/
│   └── evidence/
└── original_host_test_keys/
    ├── README.md
    ├── provider_a/
    └── provider_b/
```

The two major branches serve different purposes.

### `MH001_R43_RUN001/`

Contains the frozen implementation, original configurations, authorizations, validation records, and scored execution evidence.

Start with:

[Scored-run documentation](MH001_R43_RUN001/README.md)

### `original_host_test_keys/`

Contains the eight original disposable Ed25519 private/public key files collected from the provider hosts.

These were intentionally published after testing for exact historical reproducibility.

They are not members of the original 132-file scored-run manifest.

See:

[Original test-key documentation](original_host_test_keys/README.md)

## 2. Architecture

The experiment used two independent forwarding hubs and two independent providers.

### Initial Route — T01

```text
Requester
   |
   v
 Hub A
  |   \
  |    v
  |   Hub B
  v     |
Provider A
        |
        v
    Provider B
```

### Alternate Route — T03 and T04

```text
Requester
   |
   v
 Hub B
  |   \
  v    v
Provider A   Provider B
```

Each provider independently evaluated its own authorization.

The forwarding hubs did not hold provider signing keys, interpret provider authorization semantics, or decide whether execution was allowed.

Provider-signed events traveled to an independent observer through a separate evidence path.

## 3. Results

The scored experiment followed four tests after the initial rehearsal.

| Test | Action | Recorded outcome |
|---|---|---|
| T01 | Execute valid, single-use authorizations through Hub A | Both providers accepted |
| T02 | Terminate designated Hub A | Requests subsequently used Hub B |
| T03 | Replay the exact T01 requests through Hub B | Both providers denied |
| T04 | Submit newly issued authorizations through Hub B | Both providers accepted |

### T03 — Replay Denial

The original T01 requests were preserved and replayed without issuing new authority.

Both providers returned independently signed:

`DENY / auth_spent`

The recorded provider histories showed no additional consumption or execution for the replayed authorizations.

### T04 — Fresh Authorization

Each provider subsequently accepted a different, newly issued authorization.

Both providers recorded one new consumption and software execution.

Their final consumption ledgers contained three entries each:

1. Rehearsal.
2. T01.
3. T04.

T03 produced no additional consumption entry.

### Independent Observer Results

The completed observer record contains:

- 1 session-start record.
- 14 provider-signed event submissions.
- 1 session-end record.

All 14 submissions recorded valid Ed25519 signatures and matching registered provider identities.

The decisive T03 denials are observer records 10 and 11.

### Procedural Limitations

Two frozen scoring requirements were not separately documented:

- An immediate pre-T03 observer cursor checkpoint establishing that the matching denial was not already present.
- An immediate pre-T04 reconfirmation that Hub A remained terminated.

The published evidence supports the functional result, but those missing checkpoints prevent claiming complete documentation of every frozen procedural requirement.

For detailed findings and independent verification:

[Scored evidence](MH001_R43_RUN001/evidence/)

## 4. Provenance

MH001 preserves the lineage of the implementation and the identity of the evidence used to evaluate it.

### Provider Implementation

The provider implementations originate from the earlier MP005 multi-provider work.

The frozen provider source is associated with Git commit:

`73713f6e9ed9c95251cc69ec88ef816cab771ac0`

The original published source text and supporting-source records are preserved under:

[Source provenance](MH001_R43_RUN001/frozen_R43/provenance/)

The frozen R4.3 directory contains the routing implementation, provider source, issuance tools, and previous validation records.

### Validation Provenance

The initial R4.3 implementation passed 29 offline tests.

The subsequent deployment package introduced 23 additional tests.

The preserved local validation history contains three attempts:

| Attempt | Result |
|---|---|
| 001 | Failed; original test-suite socket-access errors |
| 002 | 52/52 PASS |
| 003 | 52/52 PASS |

These records are retained separately from the later live experiment.

[Local validation history](MH001_R43_RUN001/validation/)

### Evidence Provenance

Two SHA-256 inventories are preserved:

| Manifest | Scope |
|---|---|
| `MH001_R43_RUN001/SHA256SUMS.txt` | 65 original local deployment-review files |
| `MH001_R43_RUN001/evidence/MH001_FINAL_SHA256SUMS.txt` | 132 original scored-run files |

The final manifest preserves the original source, configuration, request, authorization, and evidence identities.

The eight subsequently published original test keys are separate from that 132-file inventory.

New documentation files are also separate from the original scored inventory.

These distinctions must be maintained during independent audit.

## 5. Independent Verification

A reviewer can reproduce the historical evidence checks without starting a provider or sending network requests.

### Step 1 — Verify the Original Files

From `MH001_R43_RUN001/`:

```bash
sha256sum -c evidence/MH001_FINAL_SHA256SUMS.txt
```

Expected: 132 successful file checks.

### Step 2 — Verify Source Identities

Inspect the frozen R4.3 source, its preserved provenance records, and the provider source hashes.

### Step 3 — Verify Provider Authorizations

Use the original public issuance keys to validate the signed authorization packages.

The packages are preserved in:

`MH001_R43_RUN001/authorizations/`

### Step 4 — Compare Original Requests

Reconstruct the original T01 HTTP requests using the frozen requester and published authorization packages.

Confirm their bytes match the historical files under:

`MH001_R43_RUN001/t01_requests/`

### Step 5 — Examine the Replay

Use requester receipts and provider-ingress captures to confirm that T03 reused the original T01 requests through Hub B.

### Step 6 — Verify Signed Decisions

Use the original boundary-event public keys to verify the observer's signed T03 denial events.

### Step 7 — Verify Persistent State

Compare the final provider consumption ledgers, spent-state records, and execution logs.

Confirm no additional execution occurred during T03 and that fresh T04 authority advanced each provider's ledger once.

Detailed procedures are documented in the respective evidence and artifact directories.

## 6. Reproducing the Experiment

A new live experiment requires its own approved environment.

The published materials provide the original implementation and historical evidence needed to examine or reproduce the tested behavior.

For a new run:

1. Establish isolated provider-controlled state and signing identities.
2. Verify the frozen runtime and approved configurations.
3. Establish an independent observer.
4. Prepare and preserve original provider-bound requests.
5. Execute the initial valid authorizations.
6. Terminate the designated forwarding hub under explicit operator approval.
7. Replay the exact original requests through the alternate hub.
8. Verify signed denials and unchanged consumption state.
9. Issue and submit fresh authority.
10. Verify the fresh operations execute exactly once.
11. Preserve the new evidence and create a separate hash inventory.

See:

[Original operator gates](MH001_R43_RUN001/frozen_R43/OPERATOR_GATES.md)

The historical scored directory and original signing-key materials must remain unchanged.

## 7. Scope of the Findings

MH001 provides evidence for a specific architectural constraint:

**Network forwarding position does not independently confer provider execution authority.**

Within the tested environment, a request could reach the provider through a different hub without restoring its consumed authorization.

The experiment does not demonstrate immunity to arbitrary compromise, all possible network topologies, or compromise of provider-controlled signing keys.

It also does not establish physical actuator execution.

Its measured execution outcomes are provider software events and durable provider-state transitions.

## 8. Preservation

The historical implementation, signatures, request bytes, evidence records, and SHA-256 manifests are preserved for reproducibility.

Do not rewrite original artifacts or regenerate historical hashes.

The original disposable test private keys are published intentionally. They must remain intact for historical reproduction but must not be treated as trusted operational credentials.

A new experiment must use separate state, approvals, and evidence.

## Conclusion

MH001 demonstrated that two independent providers rejected replayed, previously consumed authorization after a change in the forwarding route.

Both providers remained able to accept fresh, separately issued authorization through the alternate hub.

**Forwarding changed. Provider-controlled authority did not.**
