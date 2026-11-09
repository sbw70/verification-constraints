
# MH001 — Incomplete Observer Startup Evidence

## Purpose

This directory preserves the first incomplete observer startup attempt from the MH001 R4.3 experiment.

The attempt was archived before the successful observer session used for the rehearsal and scored tests.

It is retained to document the original sequence of activity without deleting, replacing, or misrepresenting an incomplete evidence record.

**Session identifier:** `MH001_R43_RUN001`

**Status:** INCOMPLETE STARTUP — NOT SCORED

## 1. Directory Contents

```text
incomplete_startup/
└── observer_attempt_001.jsonl
```

The file contains one JSONL record.

It is an independent historical artifact and is not part of the successful observer's continuous hash-linked record sequence.

## 2. Recorded Startup Event

The file contains:

| Property | Recorded value |
|---|---|
| Record type | `SESSION_START` |
| Record sequence | 1 |
| Session ID | `MH001_R43_RUN001` |
| Observer host | `Xer0trust` |
| Registered providers | `PROVIDER_A`, `PROVIDER_B` |
| Recorded startup time | 2026-11-07 03:29:39.286489 UTC |
| Schema version | 1 |

Record hash:

`f059908bd52f8b59e1a2b29032b6aa5390be33a92c46364745989ba25655ce12`

The file does not contain any provider submission records.

It also does not contain a `SESSION_END` record.

## 3. Why the Attempt Is Incomplete

The observer recorded a session-start event, but the preserved file does not establish a completed observer session.

Specifically, this file provides no evidence of:

- A completed observer shutdown.
- A final `SESSION_END` record.
- Provider-signed `START` events.
- Provider-signed `COMPLETE` events.
- Provider-signed `DENY` events.
- Any scored T01, T03, or T04 decision.

The absence of additional records does not independently establish the precise cause of the interrupted startup.

This attempt must not be interpreted as successful provider-event collection.

It was retained rather than repaired or appended to.

## 4. Successful Observer Session

A separate observer recording attempt was subsequently used for the successful experiment.

That original record is located at:

`evidence/observer.jsonl`

The path is relative to the MH001 scored-run root.

The successful session contains:

| Record type | Count |
|---|---:|
| SESSION_START | 1 |
| Provider submissions | 14 |
| SESSION_END | 1 |
| **Total** | **16** |

The 14 submissions include signed provider events from the rehearsal, T01, T03, and T04.

The successful session began at:

`2026-11-07T04:04:58.843375+00:00`

It completed with a recorded `SESSION_END` at:

`2026-11-08T01:07:19.463886+00:00`

Final record hash:

`df02d012c01efa7c9e12a4b86020c4af34d25474b7b09bc0ad54510309c4f9b4`

The successful observer session has its own record sequence and hash chain.

Although the two attempts share the same experiment session identifier, their independent session-start records distinguish their histories.

Do not join or concatenate their JSONL contents.

## 5. Original File Integrity

The archived startup file has the following SHA-256:

`4e964c5c6cf36ba7f1990b415130724a4ffeb394969be1a32c4851615110a2cc`

The successful observer file has the following SHA-256:

`e4b6e09413081e0d5f932a8485acfd1f27e1c79e43dbfc290c7f01cc3f9ea5dd`

Both files are included in the original 132-file MH001 scored evidence manifest:

`evidence/MH001_FINAL_SHA256SUMS.txt`

The archived attempt remains part of the published evidence inventory even though it is excluded from scored provider-event correlation.

### Verify on Linux

From this directory:

```bash
sha256sum observer_attempt_001.jsonl
wc -l observer_attempt_001.jsonl
```

Expected:

- SHA-256 matches the value above.
- One JSONL record.

### Verify on PowerShell

From this directory:

```powershell
Get-FileHash .\observer_attempt_001.jsonl -Algorithm SHA256
@(Get-Content .\observer_attempt_001.jsonl).Count
```

These commands read the original file without modifying it.

## 6. Independent Examination

To inspect the preserved startup record, read the JSONL file and confirm:

1. The file contains exactly one valid JSON object.
2. Its `record_type` is `SESSION_START`.
3. Its `record_seq` is 1.
4. Its `session_id` is `MH001_R43_RUN001`.
5. Both expected providers appear in `registered_providers`.
6. The record contains its original hash and provenance fields.
7. No provider submission or session-end record exists.

The startup record includes the observer's source, configuration, registry, and contract identities.

Those fields support identification of the attempted observer session.

They do not establish a completed recording lifecycle.

For the successful session, verify the separate 16-record observer file independently.

## 7. Reproduction Requirements

A new MH001 experiment should establish a dedicated observer session before the rehearsal or scored transactions.

The observer must:

1. Load the approved provider public-key registry.
2. Establish a new exclusive output log.
3. Record `SESSION_START`.
4. Independently verify incoming provider-signed events.
5. Preserve complete provider-event records.
6. Maintain the record hash chain.
7. Complete the session with `SESSION_END`.
8. Preserve and hash the resulting log.

If an observer startup attempt becomes incomplete:

- Preserve the incomplete output.
- Do not rewrite its original records.
- Do not fabricate a missing `SESSION_END`.
- Do not silently append a new recording attempt to it.
- Do not use incomplete records to establish a scored provider decision.
- Resolve the startup problem before beginning the scored experiment, using a separately reviewed new recording attempt.

A new observer attempt must maintain its own evidence history.

An incomplete startup is not evidence of provider authorization failure or successful execution.

## 8. Scoring Boundary

The first startup attempt is historical context only.

It does not contribute provider decisions to the scored T01–T04 results.

The scored provider decisions are evaluated using the successful observer recording, provider-ingress evidence, hub forwarding logs, and provider-controlled persistent state.

This distinction prevents an incomplete observer session from being mistaken for a continuous or completed scored recording.

## 9. Preservation

`observer_attempt_001.jsonl` is an original MH001 evidence artifact.

Its SHA-256 identity must remain unchanged.

This README is supplemental documentation and is not part of the original 132-file scored inventory.

Do not delete, repair, replace, merge, or normalize the archived observer attempt.

**Conclusion:** The first observer attempt is preserved as an incomplete startup record. The separate completed observer session supplies the signed provider decisions used for MH001 scoring.
