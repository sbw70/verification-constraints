# MP006-R01 — Fresh Authorization Submission

## Purpose

This directory preserves the submission of a separate, previously unused Provider A authorization after physical power-loss recovery and successful replay denial.

The test verifies that the recovered provider can execute newly authorized work without restoring or discarding previously consumed authority.

## Directory Contents

| File | Purpose |
|---|---|
| [send.json](send.json) | Preserved request, authorization header, identity, destination, and submission timestamp |
| [relay_response.json](relay_response.json) | HTTP response returned by the NUVL relay |
| [cursor.json](cursor.json) | Association-recorder position and prefix hash before submission |
| [boundary_records.json](boundary_records.json) | Correlated, signed Provider A execution events |

All four files are included in the parent R01 SHA-256 inventory.

## Fresh Authorization Submission

**Submission timestamp:**

`2026-10-31T17:20:43.571721+00:00`

**Relay endpoint:**

`http://192.168.1.100:8080/nuvl`

**Provider:** `PROVIDER_A`

**Authorization ID:**

`821ca36878ef72241d6bb02815ad5de8ce2e867f49d1807f6bf0cdd99ff24695`

**Verification context:**

`CTX_MP005_MP006_R01_FRESH`

The submission contains the original bytes of the fresh request, its provider authorization header, and the corresponding identity metadata.

The authorization header matches the package preserved in [fresh/](../fresh/).

The authorization identifier, nonce, binding, and operation identity agree with the preserved issuance records.

This authorization is distinct from the one consumed before power loss.

## Relay Response

[relay_response.json](relay_response.json) records:

```json
{
  "body_b64": "",
  "status": 204
}
```

HTTP `204` records the relay response.

It does not independently establish that Provider A accepted or executed the authorization.

Execution must be established through Provider A's signed boundary events and persistent execution records.

## Association Recorder Cursor

[cursor.json](cursor.json) records:

**Byte offset:** `12640`

**Prefix SHA-256:**

`7dc456954bcb10f25d532b8e8408f21d26c9f96cd45554fb3828a6c59d3a6aac`

The cursor identifies the existing association-recorder history before the fresh submission.

The recorded offset follows recorder sequence 6, which contains the original authorization's `auth_spent` denial.

The frozen MP005 harness uses this cursor to detect replacement or truncation of the preceding recorder history.

Subsequent events are correlated using the provider, authorization, operation, binding, and nonce identities.

## Provider A Boundary Events

[boundary_records.json](boundary_records.json) contains two correlated events.

| Recorder sequence | Provider | Stage | Ledger sequence |
|---|---|---|---:|
| 8 | `PROVIDER_A` | `START` | 2 |
| 9 | `PROVIDER_A` | `COMPLETE` | 2 |

Both events identify the fresh authorization.

**Operation ID:**

`980a0f7e80d9d918347d65757666ab7b918306c3e4f4f9ab4a8deeda2db6535f`

**Final ledger head:**

`b744c9c7182d82769e11a4e29394f463a2a0f93e3d80f5f5a2d4d5873a074a6d`

Both records preserve their original signed event packages.

The association recorder marks both signatures as valid.

The MP006 scorer validates the preserved signatures and event identities against the frozen MP005 trust material.

The events also appear at sequences 8 and 9 in the original [association recorder](../association_recorder.jsonl).

A separate Provider B `auth_missing` denial appears at sequence 7.

Provider B was not the scored execution target.

## Persistent-State Correlation

The [before_fresh/](../before_fresh/) capture records:

- One existing ledger entry.
- One spent authorization.
- One existing execution record.
- No consumption or execution of the fresh authorization.

The [after_fresh/](../after_fresh/) capture records:

- Two ledger entries.
- Two spent authorizations.
- Two execution records.
- One matching execution of the fresh authorization.

The second ledger entry references the original ledger head.

The original consumption history remains unchanged.

The new entry identifies the fresh authorization and operation represented by the signed boundary events.

The MP006 scorer confirms the expected state advancement and execution count.

All twelve fresh-execution checks returned `true`.

## Timestamp Interpretation

The submission and provider execution timestamps originate from different machines.

Their clock ordering is not independently established by this directory.

The MP006 scorer explicitly records:

`"timestamp_comparisons_scored": false`

The execution conclusion therefore relies on preserved request identity, signed boundary correlation, and provider-local state changes rather than cross-machine timestamp ordering.

## Integrity Verification

This directory does not contain a separate `SHA256SUMS.txt`.

All four files are included in the original [R01 evidence inventory](../SHA256SUMS.txt).

From the parent R01 directory:

```bash
sha256sum -c SHA256SUMS.txt
```

This README is additional documentation and is not included in the historical inventory.

Do not modify the preserved submission, boundary records, recorder cursor, or original evidence hashes.

## Evidence Boundary

This directory establishes the recorded fresh-authority submission and correlated Provider A execution events.

Together with the provider-local state captures, it supports the conclusion that the recovered provider successfully consumed and executed one separate fresh authorization.

The original authorization remained spent throughout the experiment.

The result does not establish hardware-level execution or protection against arbitrary replacement of the complete persistent history.

See the [R01 evidence documentation](../README.md) for the complete experiment.
