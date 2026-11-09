
# MH001 — Provider B Final State Evidence

## Purpose

This directory preserves the final provider-controlled consumption and execution records from Provider B during the MH001 R4.3 scored experiment.

Provider B ran on an HP laptop and independently maintained its own authorization-consumption history, execution records, and spent-authority state.

**Session:** `MH001_R43_RUN001`

**Provider:** `PROVIDER_B`

**Recorded endpoint:** `192.168.1.107:18091`

**Functional result:** PASS

These files were copied from the provider host after T04. They are historical evidence, not files for initializing a new experiment.

## 1. Directory Contents

| File | Purpose |
|---|---|
| `provider_b_consume_ledger.jsonl` | Hash-linked authorization-consumption history |
| `provider_b_execution.jsonl` | Provider-local software execution records |
| `provider_b_spent_state.json` | Final persistent spent-authority snapshot |

The three records originate from Provider B.

Neither Hub A nor Hub B maintained these execution-authority records.

## 2. Consumption Ledger

The final consumption ledger contains three entries.

| Ledger sequence | Test phase | Result |
|---|---|---|
| 1 | Rehearsal | Consumed |
| 2 | T01 | Consumed |
| 3 | T04 | Consumed |

T03 produced no additional consumption entry.

### Rehearsal

Authorization ID:

`60d0f8f5192def2595b611225371815c088fc024d27c26e4103dd89e226e99e4`

Ledger entry hash:

`5d88dc3acddf479ce61c3c655930dd15c5ba3bf0e0854772db74ae7c7aca82f4`

### T01 — Original Authorization

Authorization ID:

`041315d147341d225acd07d925abcae408864bb52def806709b6b9def5e52b4a`

Ledger sequence: `2`

Ledger entry hash:

`a99e671a0ec866028ab6def190807fddd1bb4354524a55f3aae6e1cff6cab7b3`

T01 reached Provider B through:

```text
Requester → Hub A → Hub B → Provider B
```

Provider B accepted the issued authorization, recorded consumption, and executed the operation once.

### T03 — Original Authorization Replay

The original T01 request was submitted again, directly through Hub B.

```text
Requester → Hub B → Provider B
```

Provider B returned a signed denial with reason:

`auth_spent`

The denial referred to the original T01 authorization.

The ledger contains no new consumption entry for this replay.

The corresponding independent signed denial is preserved in the scored observer evidence, outside this directory.

### T04 — Fresh Authorization

Authorization ID:

`1d5777cc2f3dedba9a88d435b4d764ac749c77d6aea9f76e177d32e0fcea8226`

Ledger sequence: `3`

Ledger entry hash:

`1ed8542ff8885e1a7764b18b625626187efc6de2feea0ea69088d51308d73c41`

This entry references the T01 ledger hash as its previous entry.

The original consumed authorization remained part of the ledger history.

## 3. Final Spent-State Snapshot

The file:

`provider_b_spent_state.json`

records the final persistent state.

Expected values:

- `version`: 1
- `ledger_seq`: 3
- Three spent authorization identities
- Recorded nonces for all three authorizations

Final ledger head:

`1ed8542ff8885e1a7764b18b625626187efc6de2feea0ea69088d51308d73c41`

The snapshot ledger head matches the final entry in the consumption ledger.

Both the original T01 authorization and fresh T04 authorization are recorded as spent.

The snapshot must be checked against the ledger, not treated as an independent replacement for ledger validation.

## 4. Execution Evidence

The file:

`provider_b_execution.jsonl`

contains three recorded software executions.

| Execution sequence | Test phase | Result |
|---|---|---|
| 1 | Rehearsal | executed |
| 2 | T01 | executed |
| 3 | T04 | executed |

No T03 execution entry appears.

The authorization and operation identifiers in the execution records correspond to the three consumption-ledger entries.

The execution log records provider software behavior. It does not independently establish physical actuator activity.

## 5. SHA-256 Verification

The three original files are included in the final 132-file evidence manifest.

The following SHA-256 values were verified during MH001 publication.

| File | SHA-256 |
|---|---|
| `provider_b_consume_ledger.jsonl` | `df1511722c3bde02e0ff71220ab0aea30fbd3afed786924ba1f611733e060063` |
| `provider_b_execution.jsonl` | `2b755d23e28edaf3c37b3bf286a9715479187a707e4dd6f1fdce4741312c1a2d` |
| `provider_b_spent_state.json` | `04a861250f36f6205b3977a0e80ad47d1e11278bfa19b088625cc6330b242392` |

### Verify on Linux

From this directory:

```bash
sha256sum provider_b_consume_ledger.jsonl
sha256sum provider_b_execution.jsonl
sha256sum provider_b_spent_state.json
```

Compare the calculated values with the table above.

### Verify on Windows PowerShell

From this directory:

```powershell
Get-FileHash .\provider_b_consume_ledger.jsonl -Algorithm SHA256
Get-FileHash .\provider_b_execution.jsonl -Algorithm SHA256
Get-FileHash .\provider_b_spent_state.json -Algorithm SHA256
```

These are read-only operations.

Do not modify or normalize the original file contents before hashing.

## 6. Ledger and Snapshot Verification

After confirming file integrity:

1. Read the consumption ledger as three JSONL records.
2. Confirm every record identifies `PROVIDER_B`.
3. Confirm sequences 1, 2, and 3.
4. Confirm entry 1 has a null `previous_entry_hash`.
5. Confirm entry 2 references entry 1's hash.
6. Confirm entry 3 references entry 2's hash.
7. Recalculate and validate the entry hashes using the frozen provider ledger implementation.
8. Confirm the final snapshot references ledger sequence 3 and its matching head.
9. Confirm the snapshot contains all three consumed authorization IDs and their corresponding nonces.
10. Match the execution-log authorization and operation identifiers to the ledger.

The frozen ledger helper is located at:

`frozen_R43/provider_support/ledger_evidence.py`

That path is relative to the MH001 scored-run root.

Do not bootstrap, truncate, repair, or overwrite these historical state files.

## 7. Independent Signed-Event Correlation

Provider-local files alone do not establish independent signature verification.

The corresponding independent observer record is:

`evidence/observer.jsonl`

Relative to the MH001 scored-run root.

Verification should establish that:

- T01 produced a signed `START` and `COMPLETE` for the original authorization.
- T03 produced a newly observed signed `DENY / auth_spent`.
- The T03 denial identifies Provider B and the original T01 authority.
- The denial matches the original nonce, binding, operation, signing-key identity, and ledger state.
- T04 produced signed `START` and `COMPLETE` events for a distinct fresh authorization.

The final provider ledger and execution records must agree with these independently verified observations.

A hub receipt alone must not be treated as evidence that an operation executed.

## 8. Evidence Limitations

These files represent Provider B's final persistent state.

They do not provide separate before-and-after T03 state snapshots.

The absence of an additional T03 consumption or execution is evaluated using the final state history together with preserved provider-ingress requests, hub logs, requester receipts, and independent signed observer records.

This directory alone does not prove that Hub A was terminated or that the replay reached Provider B.

Those observations belong to other MH001 evidence directories.

## 9. Independent Reproduction

For historical verification, preserve the published files exactly and compare their hashes with the final scored manifest.

For a fresh execution experiment:

1. Use the frozen Provider B source and reviewed dependencies.
2. Establish new provider-controlled signing identities.
3. Initialize a separate persistent ledger and spent-state snapshot.
4. Issue and execute a valid single-use authorization.
5. Preserve the original request bytes.
6. Change the forwarding path and submit those same request bytes.
7. Verify a signed `DENY / auth_spent` without an additional consumption or execution.
8. Issue new authority and confirm that fresh execution remains possible.

A new reproduction will have different authorization IDs, nonces, signatures, and ledger hashes if it uses newly generated signing keys and inputs.

The behavioral requirements must match; the generated identities need not.

Never use the historical spent-state files as fresh initial state.

## 10. Preservation Boundary

These three files belong to the original MH001 scored evidence inventory.

This README is supplemental documentation added after publication of the scored run.

It must not alter the original evidence hashes or be represented as part of the original 132-file manifest.

**Provider B result:** The routing path changed, but previously consumed provider authority remained spent.
