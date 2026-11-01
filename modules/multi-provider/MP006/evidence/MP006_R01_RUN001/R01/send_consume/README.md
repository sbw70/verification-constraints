# MP006-R01 — Initial Authorization Submission

## Purpose

This directory preserves the original authorization submission and the corresponding Provider A boundary events.

The submission occurred before the physical power interruption.

Its purpose was to establish that the original authorization was accepted, consumed, and executed once before testing persistence across power loss.

## Directory Contents

| File | Purpose |
|---|---|
| [send.json](send.json) | Preserved request, authorization header, identity, destination, and submission timestamp |
| [relay_response.json](relay_response.json) | HTTP response returned by the NUVL relay |
| [cursor.json](cursor.json) | Association-recorder position and prefix hash before submission |
| [boundary_records.json](boundary_records.json) | Correlated Provider A signed boundary events |
| [SHA256SUMS.txt](SHA256SUMS.txt) | Original four-file integrity inventory |

## Original Submission

**Submission timestamp:**

`2026-10-31T16:13:48.456474+00:00`

**Relay endpoint:**

`http://192.168.1.100:8080/nuvl`

**Provider:** `PROVIDER_A`

**Authorization ID:**

`0105b3696211a2f1e536e3b9f07d0c8688e6e05640fd50b1462bb864ece97a0c`

The submission contains:

- The original request bytes, Base64-encoded for evidence preservation.
- The original provider authorization in the `X-Provider-A-Authorization` header.
- The original verification context.
- The authorization and operation identity metadata.
- The destination and local submission timestamp.

The authorization header matches the package preserved in [original/](../original/).

The recorded identity matches the original authorization metadata.

## Relay Response

[relay_response.json](relay_response.json) records:

```json
{
  "body_b64": "",
  "status": 204
}
```

HTTP `204` confirms the recorded relay response.

It does not establish that Provider A authorized or executed the request.

Execution evidence must come from Provider A's signed boundary events and persistent records.

## Association Recorder Cursor

[cursor.json](cursor.json) records:

**Byte offset:** `758`

**Prefix SHA-256:**

`b836c32f73c879e4e6ce37cdc27ee637621efea8edb5afa042b679825f4b479c`

The cursor identifies the recorder-log position before submission.

The frozen MP005 harness uses this position and prefix hash to detect replacement or truncation of the existing recorder history.

It then correlates subsequent records using provider identity, authorization identity, operation identity, binding, and nonce.

The recorded cursor follows the initial `SESSION_START` entry.

## Provider A Boundary Events

[boundary_records.json](boundary_records.json) preserves two correlated events.

| Recorder sequence | Provider | Stage | Ledger sequence |
|---|---|---|---:|
| 3 | `PROVIDER_A` | `START` | 1 |
| 4 | `PROVIDER_A` | `COMPLETE` | 1 |

Both events identify the original authorization and operation.

**Ledger head:**

`7191f3b14e0641d7c197b547b61f41b36c9792593cf6b6b067c3980d2f596dba`

Both records contain the original signed event packages.

The recorder marks both signatures as valid.

The MP006 scorer validates the preserved boundary signatures and identities using the frozen MP005 trust material.

The events also appear at sequences 3 and 4 in the original [association recorder](../association_recorder.jsonl).

The recorder contains a separate Provider B `auth_missing` denial at sequence 2. That event is not part of the correlated Provider A execution evidence.

## Persistent-State Correlation

The [pre-consumption state](../pre_consume/) records:

- Zero ledger entries.
- Zero spent authorizations.
- Zero execution records.

The [post-consumption state](../consumed/) records:

- One ledger entry.
- One spent authorization.
- One software execution record.

The new ledger entry identifies the original authorization and the same operation represented by the signed boundary events.

The MP006 scorer confirms the required ledger advancement, execution count, authorization identity, and signed boundary sequence.

## Integrity Verification

The original [SHA256SUMS.txt](SHA256SUMS.txt) inventories four evidence files.

From this directory:

```bash
sha256sum -c SHA256SUMS.txt
```

This README is additional documentation and is not included in the original inventory.

Do not modify the preserved submission, boundary records, recorder cursor, or historical hashes.

## Evidence Boundary

This directory documents the original submission and correlated Provider A boundary events.

Together with the persistent-state captures, it supports the conclusion that the original authorization was consumed and executed once before power interruption.

It does not independently establish power-loss persistence or subsequent replay rejection.

Those properties are evaluated using the recovery and replay evidence.

See the [R01 evidence documentation](../README.md) for the complete experiment.
