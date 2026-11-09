
# MH001 — Provider A Final State Evidence

## Purpose

This directory contains the final persistent consumption and execution records copied from Provider A (Dell Latitude) after the MH001 R4.3 scored experiment.

These files document the provider's local authorization-consumption history and recorded software executions.

The records were preserved after T04 and copied byte-for-byte from the provider host. They are historical evidence, not a fresh state initialization package.

**Session:** `MH001_R43_RUN001`

**Provider identity:** `PROVIDER_A`

**Recorded endpoint:** `192.168.1.118:18090`

## Files

| File | Purpose |
|---|---|
| `provider_a_consume_ledger.jsonl` | Hash-linked history of consumed authorizations |
| `provider_a_execution.jsonl` | Local record of software operations executed |
| `provider_a_spent_state.json` | Persistent snapshot identifying consumed authorization IDs and the current ledger head |

All three records are provider-controlled state artifacts.

They are not routing-hub authorization decisions.

## Consumption Ledger

The final ledger contains three entries.

| Sequence | Phase | Result |
|---|---|---|
| 1 | Rehearsal | Consumed |
| 2 | T01 | Consumed |
| 3 | T04 | Consumed |

T03 does not have a consumption entry because the previously consumed T01 authorization was denied.

### T01 Authorization

Authorization ID:

`a92b2daf4e88cbb066ef5ce47431b8ca09144055d3b8e60c3a1c185303f1c3ea`

Ledger sequence: `2`

Ledger entry hash:

`2c780e5c2a32ab1c5985568d22b3cce29a357663d5b4e1654b204c4dfc6c54cc`

### T04 Authorization

Authorization ID:

`295e8d3288b7923daf7c5beaf0cb6433e8dff8eb9b47c6c56bc3822bcb1276ea`

Ledger sequence: `3`

Final ledger head:

`c4a600ca733c67a95652c3fb3add5764a1d0fbff44111493ea0967d9d7338876`

The T04 ledger entry links to the previous T01 entry.

## Final Spent-State Snapshot

The final snapshot records:

- Ledger sequence: `3`
- Three spent authorization identities
- Their corresponding nonces
- The final ledger head

The snapshot's `ledger_head` matches the final consumption-ledger entry hash.

The snapshot is not a substitute for validating the ledger's structure and hash chain.

## Execution Evidence

The execution log contains three recorded executions.

| Execution sequence | Phase | Result |
|---|---|---|
| 1 | Rehearsal | executed |
| 2 | T01 | executed |
| 3 | T04 | executed |

There is no fourth execution entry associated with T03.

This is consistent with the independently observed T03 `DENY / auth_spent` decision.

The execution file records software execution reported by the provider. It does not independently establish physical actuator activity.

## Verification Procedure

### 1. Verify File Integrity

From the `MH001_R43_RUN001` directory, verify these three files against:

`evidence/MH001_FINAL_SHA256SUMS.txt`

Expected SHA-256 values:

| File | SHA-256 |
|---|---|
| `provider_a_consume_ledger.jsonl` | `71b582a74b0de5c9e14636a952a901918fcf2b2d1d7a699122f9af69f3252840` |
| `provider_a_execution.jsonl` | `03c914c43bc1cf47d82dd2fd91bd7b0c506b985fdaaa03f026af14d00f719551` |
| `provider_a_spent_state.json` | `b2367c325d81c482354d3e8c23ae4ead352a698fba9a132c8f7632ceaa4da6a9` |

Do not modify the files before verification.

### 2. Verify Ledger Structure

Inspect the three ledger entries.

Confirm:

- Sequences are 1, 2, and 3.
- Each entry identifies `PROVIDER_A`.
- Sequence 1 has a null previous-entry hash.
- Sequence 2 references sequence 1's entry hash.
- Sequence 3 references sequence 2's entry hash.
- Entry hashes validate under the frozen provider ledger implementation.

The applicable implementation is in:

`../../../frozen_R43/provider_support/ledger_evidence.py`

The relative path above is resolved from the scored-run root, not from this README's directory.

### 3. Verify Snapshot Consistency

Confirm that:

- `ledger_seq` equals 3.
- `ledger_head` matches ledger entry 3.
- All three consumed authorization IDs are represented in `spent`.
- Each recorded nonce matches the corresponding ledger entry.

### 4. Correlate Execution Records

Match each execution-log authorization ID and operation ID to the corresponding consumption-ledger entry.

Confirm three executions and no additional entry for the T03 replay.

### 5. Correlate Independent Provider Decisions

Use the independent signed-event record:

`../../observer.jsonl`

The paths in this section are relative to the `provider_a/` directory.

For T01, identify the signed `START` and `COMPLETE` events.

For T03, identify the independently verified signed `DENY` event with reason `auth_spent`.

For T04, identify the new signed `START` and `COMPLETE` events.

Match the authorization identity, operation, nonce, provider identity, signing key, and recorded ledger state.

A provider's local execution log alone is not sufficient to establish independent signature verification.

## Evidence Limitations

These three files represent final provider state.

They do not contain separate before-and-after T03 state snapshots.

The conclusion that T03 produced no additional consumption or execution relies on correlation with the preserved request, independent signed observer record, final state history, and other scored evidence.

Do not infer a new execution from a transport receipt or HTTP response alone.

## Reproduction Boundary

These files may be used to independently examine the recorded provider history.

They must not be used as the initial state for a fresh replication.

For a new MH001 experiment:

1. Use the verified frozen provider implementation.
2. Establish an isolated provider-controlled signing identity.
3. Initialize new persistent state through the reviewed bootstrap procedure.
4. Execute rehearsal, T01, T03, and T04 under the recorded test constraints.
5. Preserve the resulting independent evidence.
6. Compare the new results against the historical behavioral requirements, not against identical newly generated authorization IDs or signatures.

Never erase or repair historical consumed state to make replay succeed.

## Preservation

These three original files are members of the published 132-file evidence manifest.

This README is supplemental documentation added after the scored experiment.

It must not be treated as an original scored artifact.

Do not modify the historical ledger, execution log, spent-state snapshot, or final manifest.
