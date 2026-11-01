# MP006-R01 — Authorization Replay

## Purpose

This directory preserves the exact replay of the original Provider A authorization after physical power loss and recovery.

The experiment tests whether previously consumed authority remains unusable after the provider restarts.

The expected outcome is a provider-originated `auth_spent` denial without additional consumption or execution.

## Directory Contents

| File | Purpose |
|---|---|
| [send.json](send.json) | Preserved replay request, authorization header, identity, destination, and submission timestamp |
| [relay_response.json](relay_response.json) | HTTP response returned by the NUVL relay |
| [cursor.json](cursor.json) | Association-recorder position and prefix hash before replay |
| [boundary_records.json](boundary_records.json) | Correlated, signed Provider A denial |

These four files are included in the parent R01 SHA-256 inventory.

## Replay Submission

**Submission timestamp:**

`2026-10-31T17:01:53.335061+00:00`

**Relay endpoint:**

`http://192.168.1.100:8080/nuvl`

**Provider:** `PROVIDER_A`

**Authorization ID:**

`0105b3696211a2f1e536e3b9f07d0c8688e6e05640fd50b1462bb864ece97a0c`

The replay uses the original request and authorization preserved in [original/](../original/).

Comparison with [send_consume/send.json](../send_consume/send.json) confirms that:

- The request bytes are unchanged.
- The authorization header is unchanged.
- The verification context is unchanged.
- The authorization and operation identities are unchanged.

No new authorization was issued for this replay.

## Relay Response

[relay_response.json](relay_response.json) records:

```json
{
  "body_b64": "",
  "status": 204
}
```

The relay's HTTP `204` response does not indicate authorization acceptance or execution.

Provider A's signed boundary event supplies the authorization decision.

## Association Recorder Cursor

[cursor.json](cursor.json) records:

**Byte offset:** `7920`

**Prefix SHA-256:**

`2d6c126933be0cb9d45d7d6a25d82af2d4389419f44764dcbc32f917d97dbeb8`

The cursor identifies the existing recorder history before the replay submission.

The offset follows the first four recorder records, including the original Provider A `START` and `COMPLETE` events.

The MP005 harness uses the preserved prefix hash to detect recorder-history replacement or truncation before correlating subsequent events.

## Provider A Denial

[boundary_records.json](boundary_records.json) contains one correlated event.

| Field | Recorded value |
|---|---|
| Provider | `PROVIDER_A` |
| Stage | `DENY` |
| Reason | `auth_spent` |
| Recorder sequence | 6 |
| Ledger sequence | 1 |
| Recorder signature-valid flag | `true` |

**Ledger head:**

`7191f3b14e0641d7c197b547b61f41b36c9792593cf6b6b067c3980d2f596dba`

The denial identifies the original authorization, nonce, binding, and operation.

Its ledger sequence and head match the persistent state recovered after power loss.

The original [association recorder](../association_recorder.jsonl) contains the same Provider A denial at sequence 6.

A separate Provider B `auth_missing` denial appears at sequence 5. Provider B was not the scored execution target.

No Provider A `START` or `COMPLETE` event was recorded for the replay.

## Persistent-State Verification

The [before_replay/](../before_replay/) and [after_replay/](../after_replay/) captures contain identical:

- Consumption-ledger bytes.
- Spent-state bytes.
- Execution-log bytes.

Both captures record:

| Property | Value |
|---|---:|
| Ledger entries | 1 |
| Ledger sequence | 1 |
| Spent authorizations | 1 |
| Execution records | 1 |

The original authorization remains spent.

No additional ledger entry or execution record was produced.

The MP006 scorer validates these comparisons alongside the signed denial.

## Scored Result

The official [case_results.json](../case_results.json) records:

**Status:** `PASS`

**Safety result:**

`REPLAY_REJECTED_WITHOUT_ADDITIONAL_CONSUMPTION_OR_EXECUTION`

All recorded replay-safety checks returned `true`.

## Integrity Verification

This directory does not contain a separate `SHA256SUMS.txt`.

All four files are included in the original [R01 evidence inventory](../SHA256SUMS.txt).

From the parent R01 directory:

```bash
sha256sum -c SHA256SUMS.txt
```

This README is additional documentation and is not included in the historical inventory.

Do not modify the submission records, signed denial, recorder cursor, or original evidence hashes.

## Evidence Boundary

This directory establishes the recorded replay request and Provider A's signed rejection.

Combined with the unchanged persistent-state captures, it supports the conclusion that the original authorization remained consumed after the observed physical power interruption.

The result applies to this recorded replay attempt and recovered provider implementation.

It does not establish resistance to arbitrary replacement of the complete persistent history.

See the [R01 evidence documentation](../README.md) for the complete experiment.
