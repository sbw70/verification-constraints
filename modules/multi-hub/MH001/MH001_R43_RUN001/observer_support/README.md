
# MH001 — Independent Observer Support Code

## Purpose

This directory contains the evidence-recording and verification helpers used by the independent observer in MH001 R4.3.

The observer receives provider-signed boundary events through a separate communication path from the forwarding hubs.

Its responsibilities are to preserve the original signed envelopes, verify their signatures, maintain a hash-linked record, and support independent correlation with provider-local state.

**Session:** `MH001_R43_RUN001`

The code in this directory does not originate provider authorization or decide whether an operation may execute.

## 1. Directory Contents

```text
observer_support/
├── association_recorder.py
└── common.py
```

| File | Responsibility |
|---|---|
| `association_recorder.py` | HTTP event receiver, Ed25519 verification, and append-only observer record |
| `common.py` | Preserved MP005 evidence helpers for hashing, snapshots, signature verification, and outcome correlation |

The MH001-specific integration is located one level above this directory:

- `observer.py`
- `observer_launcher.py`

These are separate scored-run files, not additional contents of `observer_support/`.

## 2. association_recorder.py

This is the independent event-recording implementation.

It accepts provider-signed event envelopes at:

`POST /boundary`

It also exposes:

`GET /health`

The MH001 launcher supplies the actual listener address from `configs/observer.json`.

For the historical scored run, the observer endpoint was:

`192.168.1.102:9191`

### Event Processing

For each received submission, the recorder:

1. Preserves the original request body.
2. Records the receive timestamp and source address.
3. Extracts the claimed provider and signing-key identity.
4. Looks up the provider in the approved public-key registry.
5. Verifies the Ed25519 signature.
6. Records the verification result.
7. Appends a new hash-linked JSONL record.
8. Flushes and synchronizes the record to disk.

The original signed body is stored as `raw_body_b64`.

The recorder retains the claimed fields even when verification fails, allowing invalid submissions to be examined without treating them as authenticated provider events.

### Signature Verification

The signature covers:

```text
NUVL-MP-BOUNDARY-v1| + canonical(event)
```

Canonical JSON uses sorted object keys, compact separators, and UTF-8 encoding.

The signing public key must match the registered provider identity.

Relevant recorded fields include:

- `claimed_provider_id`
- `claimed_key_id`
- `claimed_stage`
- `claimed_authorization_id`
- `claimed_reason_code`
- `registry_match`
- `sig_valid`
- `verification_code`

The recorder also detects duplicate signed-event envelopes within its session and records the earlier receive sequence when applicable.

## 3. Hash-Linked Observer Records

The recorder uses SHA-256 to link its output records.

The initial previous-record hash is 64 zero characters.

For each new record:

```text
record_hash = SHA256(canonical(record_without_record_hash))
```

The resulting hash becomes the next record's `prev_record_hash`.

Each record also receives a sequential `record_seq`.

The recorder writes one JSON object per line.

Its session contains:

- `SESSION_START`
- `SUBMISSION` records
- `SESSION_END`

The session-start record binds the observer evidence to the original registry, recorder source, configuration, and review-contract hashes.

The recorder refuses to overwrite an existing evidence log.

A normal controlled shutdown appends `SESSION_END`, including the submission count.

This construction provides a checkable record sequence. SHA-256 chaining alone does not establish that an untrusted recorder was honest or that a historical log was never replaced; preservation of the original manifest and independent evidence remains necessary.

## 4. common.py

This file preserves MP005 evidence helper functions reused by MH001.

Its responsibilities include:

- SHA-256 hashing and canonical JSON.
- Exclusive evidence-file creation.
- Provider state snapshot collection.
- Saved snapshot integrity checks.
- Independent verification of provider-signed boundary events.
- Evidence correlation using preserved identity and observer records.
- Replay and state-transition assertions.
- Provider process and filesystem evidence helpers.

The source also contains broader historical MP005 harness functions. Not every function is used by the MH001 scored run.

**Do not execute the entire historical MP005 workflow simply because this file is present.**

The MH001 integration selects the relevant functions through `observer.py`.

### Replay Assertions

The reusable helpers support checking that a rejected replay:

- Leaves the spent-state contents unchanged.
- Leaves the execution log unchanged.
- Retains the authorization as spent.
- Produces one matching signed `DENY / auth_spent`.
- Produces no START or COMPLETE event for that replay.

These assertions must be evaluated against the actual before/after provider evidence.

A signed denial without persistent-state correlation is not the entire replay proof.

## 5. MH001 Integration

The parent-level `observer.py` connects these helpers to the scored experiment.

Its main functions include:

| Function | Purpose |
|---|---|
| `load_registry()` | Verify approved provider trust and observer public-key identities |
| `session_records()` | Validate observer session sequence and hash-chain continuity |
| `checked_history()` | Confirm the observer session's frozen source and configuration identities |
| `checkpoint()` | Establish an evidence cursor and provider-state baseline before a request |
| `verify_outcome()` | Correlate newly observed signed events with provider before/after state |

The parent-level `observer_launcher.py` provides these actions:

- `inspect`
- `run`
- `checkpoint`
- `verify`

The `run` action requires reviewed startup approval.

The `checkpoint` and `verify` actions operate on explicitly supplied identity, snapshot, and evidence paths.

Successful independent outcome verification does **not**, by itself, assert a complete scored-case PASS. Provider-ingress and operator evidence must also be evaluated.

## 6. Original Source Integrity

Both files are included in the original scored-run SHA-256 manifest.

### association_recorder.py

SHA-256:

`fad60dfc8df53337d2e41288c2c4973442258cae4240945ebbd0aa8920550bfc`

### common.py

SHA-256:

`6dd965501e8266bf7315570b9101b1da0b68e9cd6c7a65072170eaba01bd164c`

The original manifest is:

`evidence/MH001_FINAL_SHA256SUMS.txt`

### Verify on Linux

From `observer_support/`:

```bash
sha256sum association_recorder.py
sha256sum common.py
```

### Verify on Windows PowerShell

From `observer_support/`:

```powershell
Get-FileHash .\association_recorder.py -Algorithm SHA256
Get-FileHash .\common.py -Algorithm SHA256
```

Expected: both hashes match the original manifest.

Do not reformat these Python files or modify their original bytes.

## 7. Original Scored Observer Evidence

The completed historical log is:

`evidence/observer.jsonl`

It contains 16 records:

| Record type | Count |
|---|---:|
| SESSION_START | 1 |
| Provider submissions | 14 |
| SESSION_END | 1 |

All 14 provider submissions recorded:

- `registry_match: true`
- `sig_valid: true`
- `verification_code: ok`

The original provider-signature verification can be repeated offline using the published event envelopes and public keys.

The original observer log is documented in:

`evidence/README.md`

The corresponding public keys and registry are documented under:

`association/`

## 8. Critical T03 Verification

The decisive MH001 replay results appear in observer record sequences 10 and 11.

| Record | Provider | Signed outcome |
|---|---|---|
| 10 | PROVIDER_A | DENY / auth_spent |
| 11 | PROVIDER_B | DENY / auth_spent |

Both denials refer to the original T01 authorizations.

The observer evidence must be correlated with:

- The exact original T01 request bytes.
- The T03 requester receipts.
- The provider-ingress packet captures.
- The provider consumption ledgers.
- The provider execution records.

Two procedural checks from the frozen scoring protocol were not separately documented in the final run: an immediate pre-T03 observer cursor checkpoint and an immediate pre-T04 reconfirmation of Hub A termination.

Those missing records must not be represented as completed merely because the helper implementation supports checkpointing.

## 9. Independent Reproduction

For a new, separately authorized experiment:

1. Preserve the original observer-support source files for reference.
2. Establish a separate run workspace and evidence directory.
3. Configure independently approved provider public signing keys.
4. Verify the recorder's source identity.
5. Use the reviewed launcher and required operator approval.
6. Start the observer with a new exclusive log.
7. Confirm `SESSION_START` and source/configuration bindings.
8. Establish before-request provider-state snapshots and observer checkpoints.
9. Submit authorized requests through the separately reviewed requester/hub workflow.
10. Collect and verify the provider-signed events.
11. Capture after-request provider state.
12. Apply the corresponding fresh-authority or replay assertions.
13. Preserve the completed observer session and calculate its hashes.
14. Correlate all outcomes with provider-ingress evidence.

For T03, the expected signed decision is specifically:

`DENY / auth_spent`

A different denial reason does not satisfy the frozen replay condition.

Do not infer successful or unsuccessful provider execution from a hub response alone.

## 10. Preservation Boundary

Both original Python files belong to the 132-file scored evidence inventory.

This README is supplemental documentation.

Do not modify the original source files, rewrite historical observer records, or regenerate the original hashes.

Do not run the recorder against the historical completed evidence-log path.

Do not reuse a completed session as the output destination for a new experiment.

## Conclusion

The observer-support implementation provides the independently checkable evidence path for provider-signed decisions.

The observer verifies what the providers reported; it does not obtain authority to make those decisions on their behalf.
