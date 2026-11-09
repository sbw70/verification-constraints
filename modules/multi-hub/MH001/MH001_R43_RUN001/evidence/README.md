
# MH001 — Scored Experiment Evidence

## Purpose

This directory contains the independently collected evidence for the MH001 R4.3 multi-hub experiment.

The evidence supports examination of whether changing a request's forwarding path restored provider execution authority that had already been consumed.

**Session:** `MH001_R43_RUN001`

**Experiment date:** November 7, 2026 (continuing into November 8 UTC)

**Functional result:** PASS

This directory is an evidence archive, not an executable test harness.

The original evidence files must remain byte-identical.

## 1. Directory Contents

```text
evidence/
├── README.md
├── MH001_FINAL_SHA256SUMS.txt
├── observer.jsonl
├── observer.pid
├── observer_startup.stdout.log
├── observer_startup.stderr.log
├── final_remote/
│   ├── hub_a.jsonl
│   ├── hub_b.jsonl
│   ├── provider_a/
│   └── provider_b/
├── incomplete_startup/
│   └── observer_attempt_001.jsonl
├── ingress/
│   ├── provider_a_18090.pcap
│   └── provider_b_18091.pcap
└── requester/
    ├── MH001_requester1.etl
    └── eight transmission receipts
```

Each evidence subdirectory documents a distinct observation source.

| Directory | Evidence responsibility |
|---|---|
| `requester/` | Original request hashes, first-hop destinations, and transport receipts |
| `ingress/` | Independently captured HTTP requests received by each provider |
| `final_remote/` | Hub forwarding logs and provider persistent consumption/execution records |
| `incomplete_startup/` | Preserved earlier observer startup attempt, excluded from scoring |

The provider-specific and transport-specific READMEs explain the detailed verification procedures.

## 2. Evidence Integrity Manifest

File:

`MH001_FINAL_SHA256SUMS.txt`

This manifest identifies 132 original scored-run files.

The manifest includes evidence, implementation source, configurations, authorizations, validation history, and other preserved session artifacts.

**The 132 entries cover the scored-run directory, not only this evidence directory.**

The paths in the manifest are relative to:

`MH001_R43_RUN001/`

The manifest itself is an additional file and is not one of its own 132 entries.

### Manifest Identity

SHA-256:

`B86996AE2B7A50754DDCCF41A688130814689F907E57BBBB6F7E4B516A4CF005`

The original final verification reported:

**132/132 files matched their recorded SHA-256 values.**

### Verify on Linux

Change into the `MH001_R43_RUN001` directory.

Run:

```bash
sha256sum -c evidence/MH001_FINAL_SHA256SUMS.txt
```

Expected result: 132 successful file checks and no mismatches.

### Verify on Windows PowerShell

Change into the `MH001_R43_RUN001` directory.

Run:

```powershell
$entries = Get-Content .\evidence\MH001_FINAL_SHA256SUMS.txt
$verified = 0

foreach ($line in $entries) {
    if ($line -notmatch '^([0-9a-fA-F]{64})  (.+)$') {
        throw "Malformed manifest entry: $line"
    }

    $expected = $Matches[1]
    $relativePath = $Matches[2]

    $actual = (Get-FileHash -LiteralPath $relativePath -Algorithm SHA256).Hash

    if ($actual -ne $expected) {
        throw "SHA-256 mismatch: $relativePath"
    }

    $verified++
}

"PASS: $verified/$($entries.Count) original files verified"
```

This checks the original files without modifying them.

New documentation added after the experiment is not covered by this original manifest.

Do not regenerate the historical manifest to include new READMEs.

## 3. Independent Observer

File:

`observer.jsonl`

This is the completed independent observer record for the scored experiment.

The observer ran separately from the provider and hub processes.

**Recorded endpoint:** `192.168.1.102:9191`

It received provider-signed event submissions independently of the hub forwarding path.

The observer verified provider identity, signing-key identity, and Ed25519 signatures using its registered provider public keys.

The hubs did not make those authorization decisions.

### Original File Integrity

SHA-256:

`e4b6e09413081e0d5f932a8485acfd1f27e1c79e43dbfc290c7f01cc3f9ea5dd`

The file is included in the final 132-entry manifest.

## 4. Observer Record Structure

The completed observer log contains 16 JSONL records.

| Record type | Count |
|---|---:|
| SESSION_START | 1 |
| Provider START submissions | 6 |
| Provider COMPLETE submissions | 6 |
| Provider DENY submissions | 2 |
| SESSION_END | 1 |
| **Total** | **16** |

The records have consecutive sequence numbers from 1 through 16.

### Session Start

Record sequence: `1`

Timestamp:

`2026-11-07T04:04:58.843375+00:00`

Registered providers:

- `PROVIDER_A`
- `PROVIDER_B`

### Session End

Record sequence: `16`

Timestamp:

`2026-11-08T01:07:19.463886+00:00`

Recorded provider submission count: `14`

Final record hash:

`df02d012c01efa7c9e12a4b86020c4af34d25474b7b09bc0ad54510309c4f9b4`

The original observer was stopped cleanly.

The first incomplete startup attempt is archived separately and must not be merged into this record sequence.

## 5. Recorded Provider Events

The observer's record sequence provides the following mapping.

| Record sequences | Phase | Provider | Signed outcome |
|---|---|---|---|
| 2–3 | Rehearsal | A | START / COMPLETE |
| 4–5 | Rehearsal | B | START / COMPLETE |
| 6–7 | T01 | A | START / COMPLETE |
| 8–9 | T01 | B | START / COMPLETE |
| 10 | T03 | A | DENY / auth_spent |
| 11 | T03 | B | DENY / auth_spent |
| 12–13 | T04 | A | START / COMPLETE |
| 14–15 | T04 | B | START / COMPLETE |

The original observer records report:

- `sig_valid: true`
- `registry_match: true`
- `verification_code: ok`

for all 14 provider submissions.

These recorded verification outcomes should also be checked independently using the published signed envelopes, original public keys, and frozen verification implementation. A recorded `sig_valid` flag by itself is not a substitute for cryptographic verification.

## 6. Critical T03 Denials

T03 was the decisive replay test.

Both providers had already consumed their respective T01 authorizations.

The original requests were submitted through Hub B after Hub A was terminated.

### Provider A

Observer record sequence: `10`

Signed stage:

`DENY`

Signed reason:

`auth_spent`

Authorization ID:

`a92b2daf4e88cbb066ef5ce47431b8ca09144055d3b8e60c3a1c185303f1c3ea`

Recorded ledger sequence: `2`

### Provider B

Observer record sequence: `11`

Signed stage:

`DENY`

Signed reason:

`auth_spent`

Authorization ID:

`041315d147341d225acd07d925abcae408864bb52def806709b6b9def5e52b4a`

Recorded ledger sequence: `2`

Both denials identify the original T01 authorizations.

Neither provider advanced its consumption ledger or recorded another execution for those replayed authorizations.

Subsequent T04 fresh-authority executions advanced both provider ledgers to sequence 3.

## 7. Independent Signature Verification

The observer uses an approved public-key registry located at the scored-run root:

`association/provider_registry.json`

The corresponding public keys are stored under:

`association/trust/`

The frozen verification dependencies include:

- `observer.py`
- `observer_support/association_recorder.py`
- `observer_support/common.py`

All paths above are relative to `MH001_R43_RUN001/`.

### Verification Requirements

An independent reviewer should:

1. Verify `observer.jsonl` against the final SHA-256 manifest.
2. Parse all 16 JSONL records.
3. Validate the observer record sequence and hash chain.
4. Confirm exactly one SESSION_START and one SESSION_END.
5. Inspect each provider submission's original `raw_body_b64` signed envelope.
6. Decode the signed envelope without modifying its original bytes.
7. Verify its Ed25519 signature using the registered provider public key and the frozen signing/verification format.
8. Confirm provider and signing-key identities match the registry.
9. Confirm the signed event contents agree with the observer's recorded claimed fields.
10. Confirm the signed authorization ID, nonce, binding, operation ID, and ledger state for the relevant test phase.

Do not assume that a valid provider signature proves the request actually traversed the claimed hub path.

Routing must be established using independent transport evidence.

Similarly, a correctly forwarded HTTP request is not proof of a valid provider signature.

## 8. Evidence Correlation

MH001 requires independent evidence sources to agree.

### T01 — Original Execution

Confirm:

- Requester submitted the original requests through Hub A.
- Hub A forwarded Provider A directly.
- Hub A forwarded Provider B through Hub B.
- Provider-ingress captures show the original HTTP requests.
- Observer records contain signed START and COMPLETE events for both providers.
- Both providers recorded one corresponding consumption and execution.
- The original authorizations became spent.

### T02 — Hub A Termination

Confirm the operator-authorized termination using the available process and session records.

The forwarding logs show no subsequent Hub A requests.

However, absence of later log entries is not independently sufficient to prove process termination.

### T03 — Exact Replay

Confirm:

- Requester used Hub B as the new first hop.
- The T01 request hashes were reused without modification.
- Hub B forwarded both requests.
- Both providers received the original request bytes again.
- Provider-ingress T01 and T03 HTTP requests are byte-identical.
- Observer records 10 and 11 are valid provider-signed `DENY / auth_spent` events.
- The signed denial identities match the corresponding original T01 authority.
- No new consumption or execution was recorded.

### T04 — Fresh Authority

Confirm:

- T04 used distinct, separately issued authorizations.
- Both requests passed through Hub B.
- Both providers produced signed START and COMPLETE events.
- Each provider recorded one new consumption and execution.
- Both final provider ledgers reached sequence 3.
- The original T01 authorizations remained spent.

## 9. Evidence Sources and Their Limits

| Evidence | Establishes | Does not independently establish |
|---|---|---|
| Requester receipts | First-hop destination and recorded transport result | Provider execution |
| Hub logs | Selected next hop and forwarding observations | Provider authorization |
| Provider PCAPs | HTTP requests actually observed at provider ingress | Valid signed decisions |
| Observer JSONL | Recorded and verifiable provider-signed events | Complete network route |
| Provider ledgers | Persistent consumption history | Independent network delivery |
| Execution logs | Provider-reported software execution | Physical actuator activity |
| Spent snapshots | Final provider consumption state | Every intermediate state transition |

No single file proves the entire MH001 result.

The experiment relies on cross-correlation between these separately collected sources.

## 10. Additional Observer Artifacts

### observer.pid

Contains the historical observer process ID:

`24912`

This identifies the process associated with the original run. It is not a live process-control instruction.

Do not use this historical PID to terminate a process on another system.

### Startup Logs

Files:

- `observer_startup.stdout.log`
- `observer_startup.stderr.log`

Both original files are zero bytes.

Their SHA-256 is the standard empty-file digest:

`e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855`

The empty logs do not independently prove successful startup or failure.

The completed observer session and its records are the relevant evidence of collection.

### Earlier Incomplete Startup

Directory:

`incomplete_startup/`

Contains an archived one-record observer startup attempt.

It is included in the original evidence manifest but excluded from scored provider-event correlation.

See that directory's README for its preservation and interpretation rules.

## 11. Procedural Limitations

Two observations specified by the frozen scoring protocol were not separately documented:

1. An independent observer cursor checkpoint immediately before T03.
2. An immediate pre-T04 reconfirmation that Hub A remained down.

The successful observer log, provider captures, hub records, and final provider states support the recorded functional outcomes.

However, these missing procedural checkpoints must not be presented as completed.

The distinction is between a demonstrated functional result and strict completion of every frozen procedural requirement.

These are documentation limitations, not observed accepted replays or unauthorized executions.

## 12. Reproduction Requirements

For a new, separately authorized MH001 experiment:

1. Use an independently controlled observer.
2. Configure the observer with only the approved provider public signing keys.
3. Establish an exclusive observer output file.
4. Record SESSION_START before rehearsal.
5. Capture each signed provider event without modifying its original envelope.
6. Validate signatures against the corresponding provider registry.
7. Preserve observer sequence and record-hash continuity.
8. Before every T03 replay, record an observer checkpoint and establish the absence of a matching earlier denial.
9. Confirm newly observed T03 denials occur after their corresponding checkpoints.
10. Correlate those denials with the provider-ingress requests and persistent state.
11. Record SESSION_END after the experiment.
12. Stop evidence collection cleanly.
13. Hash all collected evidence.
14. Preserve a new, independent manifest for the reproduction.

Never append a new experiment's events to the historical observer log.

A reproduction must establish its own evidence identities, signing trust, state, and session history.

## 13. Preservation Rules

The original 132-file manifest and all original evidence files are frozen historical artifacts.

Supplemental READMEs are not members of that manifest.

Do not:

- Rewrite JSONL files.
- Reformat original JSON records.
- Normalize original line endings.
- Regenerate original packet captures.
- Replace historical signing identities.
- Reset provider consumption history.
- Merge separate observer attempts.
- Rewrite the original final SHA-256 manifest.

New documentation must remain distinguishable from the original scored evidence.

## Conclusion

The independent evidence establishes that both providers received their previously consumed requests through the alternate route and returned signed `DENY / auth_spent` decisions.

Both providers subsequently accepted separately issued fresh authority.

**The forwarding path changed. The provider's authority boundary did not.**
