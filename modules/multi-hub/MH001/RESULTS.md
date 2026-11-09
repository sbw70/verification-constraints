# MH001 — Experimental Results

**Project:** Xer0trust / Neutral Unified Verification Layer (NUVL)

**Experiment:** MH001 — Multi-Hub Authority Persistence

**Implementation:** R4.3

**Scored session:** `MH001_R43_RUN001`

**Execution dates:** November 7–8, 2026 UTC

**Recorded functional result:** Provider A PASS / Provider B PASS

**Procedural qualification:** Two frozen scoring checkpoints were not separately documented.

---

## 1. Objective

MH001 evaluates whether changing the network forwarding path can restore previously consumed provider-controlled execution authority.

The experiment uses:

- Two independently operating forwarding hubs.
- Two independent provider-controlled authorization boundaries.
- Provider-issued single-use Ed25519 authorization.
- Provider-local persistent consumption ledgers.
- Independent provider-ingress packet capture.
- An independent recorder of provider-signed boundary events.

The central test is whether an authorization consumed through Hub A can execute again when the exact original request is submitted through Hub B.

The forwarding hubs do not validate provider authorization, maintain provider execution state, or originate authority.

Each provider independently determines whether its authorization is executable.

## 2. Recorded Results

The experiment consisted of a rehearsal followed by four scored phases.

| Phase | Provider A | Provider B |
|---|---|---|
| Rehearsal — original valid authority | Accepted | Accepted |
| T01 — valid authority through Hub A | Accepted | Accepted |
| T02 — Hub A termination | Operationally reported | Operationally reported |
| T03 — exact T01 replay through Hub B | DENY / auth_spent | DENY / auth_spent |
| T03 — additional consumption | None recorded | None recorded |
| T03 — additional execution | None recorded | None recorded |
| T04 — fresh authority through Hub B | Accepted | Accepted |
| Final consumption ledger entries | 3 | 3 |
| Final software execution records | 3 | 3 |
| **Functional classification** | **PASS** | **PASS** |

The two providers maintained separate authority and consumption histories throughout the experiment.

No previously consumed T01 authorization was recorded as executing again during T03.

### Procedural Classification

The published records support the functional replay-denial result.

However, two required procedural observations were not separately documented:

1. An immediate pre-T03 observer cursor checkpoint.
2. An immediate pre-T04 confirmation that Hub A remained terminated.

Therefore, **the functional result is supported, but full completion of every frozen scoring requirement is not documented**.

These limitations are detailed in Section 11.

## 3. Tested Network Topology

### Original T01 Routes

```text id="byri9v"
Requester
   |
   v
 Hub A
  |   \
  |    v
  |   Hub B
  |     |
  v     v
Provider A   Provider B
```

Provider A received its T01 request directly from Hub A.

Provider B received its T01 request through Hub A and then Hub B.

### Alternate T03/T04 Routes

```text id="fjuvm9"
Requester
   |
   v
 Hub B
  |   \
  v    v
Provider A   Provider B
```

The requester changed its first-hop destination to Hub B.

No provider authorization was reissued for T03.

Provider A's immediate upstream forwarding host changed from Hub A to Hub B.

Provider B continued receiving traffic from Hub B, but Hub A was no longer part of the requester's selected route.

## 4. Rehearsal

Both providers first received valid, independently issued authorizations.

The rehearsal established that the reviewed transport and provider mechanisms could complete an authorized software execution.

Each provider recorded:

- One authorization consumption.
- Consumption ledger sequence 1.
- One software execution.
- Signed START and COMPLETE events.

The completed observer log contains:

| Observer records | Provider | Outcome |
|---|---|---|
| 2–3 | A | START / COMPLETE |
| 4–5 | B | START / COMPLETE |

The rehearsal authorizations were distinct from the later T01 authorizations.

Preserved inputs:

- [Rehearsal authorization inputs](MH001_R43_RUN001/rehearsal_inputs/)
- [Prepared rehearsal requests](MH001_R43_RUN001/rehearsal_requests/)

## 5. T01 — Original Authorization Consumption

Both providers received newly issued provider-specific authority through the original forwarding topology.

### Provider A

**Authorization ID:**

`a92b2daf4e88cbb066ef5ce47431b8ca09144055d3b8e60c3a1c185303f1c3ea`

**Request body SHA-256:**

`83071f65a756aeb0c02206de5e331a564516818c1081a58905076de260afc99c`

Recorded outcome:

- Request entered through Hub A.
- Provider A accepted its authorization.
- Consumption ledger advanced to sequence 2.
- One software execution was recorded.
- The observer captured signed START and COMPLETE events.

Observer records: 6–7.

### Provider B

**Authorization ID:**

`041315d147341d225acd07d925abcae408864bb52def806709b6b9def5e52b4a`

**Request body SHA-256:**

`578455981c69b3955dad7c6a7cb15409fafc117d2dcc85dc34cb432f6d3fe1f0`

Recorded outcome:

- Request entered through Hub A.
- Hub A forwarded it to Hub B.
- Hub B forwarded it to Provider B.
- Provider B accepted its authorization.
- Consumption ledger advanced to sequence 2.
- One software execution was recorded.
- The observer captured signed START and COMPLETE events.

Observer records: 8–9.

### T01 Result

Both providers independently consumed and executed their original T01 authorizations.

The original request bytes were preserved for later replay.

[Original T01 requests](MH001_R43_RUN001/t01_requests/)

[Original T01 authorization packages](MH001_R43_RUN001/authorizations/)

## 6. T02 — Hub A Termination

T02 changed the forwarding environment.

The designated MH001 Hub A process was terminated under operator control.

Hub B and the two providers remained the intended active components.

The preserved forwarding logs show:

- Hub A handled the rehearsal and T01 requests.
- Hub A recorded no subsequent T03 or T04 forwarding.
- Hub B handled the later T03 and T04 requests.

### Recorded Hub Activity

| Hub | Forwarded requests | JSONL records |
|---|---:|---:|
| Hub A | 4 | 8 |
| Hub B | 6 | 12 |
| **Total** | **10 hub-handling events** | **20** |

The ten hub-handling events are not ten independent provider executions. Provider B's rehearsal and T01 requests traversed both hubs and appear in both logs.

### T02 Evidence Boundary

The termination was reported as operationally verified.

The hub logs themselves do not contain a separate process-termination record.

Absence of later Hub A entries is consistent with termination but cannot independently prove that the process and listener remained absent.

The T02 observation is therefore distinguished from the cryptographically verified provider decisions.

[Original hub forwarding logs](MH001_R43_RUN001/evidence/final_remote/)

## 7. T03 — Exact Replay Through Hub B

T03 was the decisive test.

The requester submitted the original T01 requests again, this time directly through Hub B.

No replacement authorization was issued.

The request bodies, authorization identities, nonces, and provider bindings were preserved.

### Original Request Identity

| Provider | T01 request SHA-256 | T03 request SHA-256 | Match |
|---|---|---|---|
| A | `bf748793a91e35f53e5f2137d78239021e77036b3e462a639369cc3403cf0c33` | Same | PASS |
| B | `ddcec53dad222c60b134a8cb0145f18b241d6c7177febd2cd7925600591dbf84` | Same | PASS |

These hashes identify the prepared HTTP requests at the requester.

The forwarding implementation performed the expected transport-level Host header rewrite. Provider-ingress captures separately establish the actual received bytes.

### Provider-Ingress Verification

The original post-run comparison reported:

- Provider A T01/T03 ingress bytes identical.
- Provider B T01/T03 ingress bytes identical.
- Eight total provider-ingress requests verified across the experiment.

This establishes that both providers received their previously consumed requests again.

### Provider A Replay Denial

Observer record sequence: `10`

Signed stage:

`DENY`

Signed reason:

`auth_spent`

Authorization ID:

`a92b2daf4e88cbb066ef5ce47431b8ca09144055d3b8e60c3a1c185303f1c3ea`

Signed ledger sequence: `2`

Recorded result:

- No new consumption entry for the replay.
- No new execution entry.
- No START or COMPLETE event for the replayed authorization.

### Provider B Replay Denial

Observer record sequence: `11`

Signed stage:

`DENY`

Signed reason:

`auth_spent`

Authorization ID:

`041315d147341d225acd07d925abcae408864bb52def806709b6b9def5e52b4a`

Signed ledger sequence: `2`

Recorded result:

- No new consumption entry for the replay.
- No new execution entry.
- No START or COMPLETE event for the replayed authorization.

### T03 Result

**Provider A: PASS**

**Provider B: PASS**

Both providers rejected their original authorizations after the forwarding path changed.

The final consumption and execution histories contain no additional T03 entries.

This finding is based on correlation between the signed denials, provider-ingress captures, requester receipts, hub forwarding records, and final provider state.

The final provider-state files are not separate before-and-after T03 snapshots.

[Provider-ingress packet evidence](MH001_R43_RUN001/evidence/ingress/)

[Independent signed observer record](MH001_R43_RUN001/evidence/observer.jsonl)

## 8. T04 — Fresh Authorization Control

T04 established that the providers could still execute newly authorized operations through Hub B.

Both providers received independently issued new authorization packages.

### Provider A

Fresh authorization ID:

`295e8d3288b7923daf7c5beaf0cb6433e8dff8eb9b47c6c56bc3822bcb1276ea`

Body SHA-256:

`c6591697c79a356b8ccf9ccb16da2dca2f379789ecfbf53fa6fbc3a1de605f39`

Recorded result:

- Signed START and COMPLETE.
- New consumption ledger sequence 3.
- One new software execution.

Observer records: 12–13.

### Provider B

Fresh authorization ID:

`1d5777cc2f3dedba9a88d435b4d764ac749c77d6aea9f76e177d32e0fcea8226`

Body SHA-256:

`855a7d10541370bdea080add62a90c9694cc697caa93365cfe920bc112c61ed6`

Recorded result:

- Signed START and COMPLETE.
- New consumption ledger sequence 3.
- One new software execution.

Observer records: 14–15.

### T04 Result

Both providers accepted fresh authorization through Hub B.

The original T01 authorizations remained in their persistent spent-authority histories.

The providers did not require the return of Hub A to execute fresh operations.

[Original T04 requests](MH001_R43_RUN001/t04_requests/)

## 9. Final Provider State

The final provider-state records were copied from the respective provider hosts after T04.

### Consumption and Execution Summary

| State property | Provider A | Provider B |
|---|---:|---:|
| Rehearsal consumption | 1 | 1 |
| T01 consumption | 1 | 1 |
| T03 consumption | 0 | 0 |
| T04 consumption | 1 | 1 |
| Final ledger entries | 3 | 3 |
| Final spent authorizations | 3 | 3 |
| Final execution entries | 3 | 3 |

### Provider A Final Ledger Head

`c4a600ca733c67a95652c3fb3add5764a1d0fbff44111493ea0967d9d7338876`

### Provider B Final Ledger Head

`1ed8542ff8885e1a7764b18b625626187efc6de2feea0ea69088d51308d73c41`

Both final spent-state snapshots identify ledger sequence 3.

Both snapshot ledger heads match the final corresponding consumption-ledger entry.

The execution logs identify the same three authorization-consumption phases:

1. Rehearsal.
2. T01.
3. T04.

No T03 execution appears.

Evidence:

- [Provider A final state](MH001_R43_RUN001/evidence/final_remote/provider_a/)
- [Provider B final state](MH001_R43_RUN001/evidence/final_remote/provider_b/)

These are provider-reported software execution records, not physical actuator measurements.

## 10. Independent Observer Evidence

The completed independent observer log is:

[observer.jsonl](MH001_R43_RUN001/evidence/observer.jsonl)

It contains 16 JSONL records.

| Record type | Count |
|---|---:|
| SESSION_START | 1 |
| Signed START submissions | 6 |
| Signed COMPLETE submissions | 6 |
| Signed DENY submissions | 2 |
| SESSION_END | 1 |
| **Total** | **16** |

All 14 provider submissions recorded:

- `sig_valid: true`
- `registry_match: true`
- `verification_code: ok`

The original event envelopes and approved public keys permit independent Ed25519 verification.

### Observer Integrity

Observer log SHA-256:

`e4b6e09413081e0d5f932a8485acfd1f27e1c79e43dbfc290c7f01cc3f9ea5dd`

Final observer record hash:

`df02d012c01efa7c9e12a4b86020c4af34d25474b7b09bc0ad54510309c4f9b4`

The observer records use a SHA-256 hash chain.

A reviewer must verify both the recorded hash chain and the individual provider signatures.

A recorded `sig_valid` field alone is not independent cryptographic verification.

The signed events authenticate the provider statements under the published test keys.

They do not independently establish network routing or physical execution.

## 11. Procedural Limitations

The frozen scoring procedure required additional operator and observer checkpoints.

Two were not separately documented.

### 11.1 Immediate Pre-T03 Observer Checkpoint

The frozen procedure required an observer cursor and a check that no matching signed denial already existed before each T03 replay.

The final evidence contains the completed observer session and new T03 denial records in the session sequence.

However, a separate immediate pre-T03 checkpoint artifact was not preserved.

The requirement must not be marked as independently completed.

### 11.2 Immediate Pre-T04 Hub A Reconfirmation

The frozen procedure required reconfirming that Hub A's process and listener remained absent before T04.

The preserved records show that T04 requests were submitted through Hub B and that Hub A recorded no later forwarding.

An immediate pre-T04 reconfirmation artifact was not separately documented.

Absence of a Hub A log entry is not a substitute for that observation.

### Interpretation

These limitations do not identify a successful replay or an unauthorized execution.

They do limit claims concerning complete fulfillment of the original scoring procedure.

**Functional replay denial:** Supported.

**Every frozen procedural checkpoint independently documented:** No.

## 12. Validation History and Incomplete Attempts

### Offline Validation

The preserved local deployment validation includes three attempts.

| Attempt | Result |
|---|---|
| 001 | Failed — original R4.3 socket-access errors |
| 002 | 52/52 tests passed |
| 003 | 52/52 tests passed |

The passing local result was:

`LOCAL_DEPLOYMENT_PACKAGE_VALIDATED_NOT_DEPLOYED`

That was the correct historical preparation-stage classification.

It is not the final live experiment classification.

[Validation history](MH001_R43_RUN001/validation/)

### Incomplete Observer Startup

An earlier observer startup attempt produced a one-record, incomplete session.

It was preserved under:

[Incomplete observer startup](MH001_R43_RUN001/evidence/incomplete_startup/)

That attempt was excluded from the scored provider-event correlation.

The separate completed 16-record observer session supplies the scored signed-event evidence.

The incomplete attempt must not be deleted, repaired, or merged with the completed log.

## 13. Scored Evidence Integrity

The original scored-run manifest is:

[MH001_FINAL_SHA256SUMS.txt](MH001_R43_RUN001/evidence/MH001_FINAL_SHA256SUMS.txt)

It contains 132 original file entries.

The published final verification reported:

**132/132 files matched their recorded SHA-256 values.**

### Verify the Original Files

From `MH001_R43_RUN001/` on Linux:

```bash id="x9co3u"
sha256sum -c evidence/MH001_FINAL_SHA256SUMS.txt
```

This verifies original file integrity.

It does not repeat the live test or replace independent examination of the evidence.

The eight original host-generated test signing-key files were published separately under:

[original_host_test_keys/](original_host_test_keys/)

They are supplemental reproducibility material and are not members of the original 132-file manifest.

Original signatures, key bytes, and evidence hashes must remain unchanged.

## 14. Evidence Correlation

The complete MH001 result depends on agreement between distinct evidence sources.

| Evidence source | Establishes |
|---|---|
| Requester receipts | Prepared request identity, selected first hop, transport result |
| Hub A and B logs | Actual recorded forwarding paths and body-hash preservation |
| Provider-ingress PCAPs | Requests observed at the provider network boundaries |
| Signed observer events | Provider-originated START, COMPLETE, and DENY statements |
| Consumption ledgers | Provider-local authorization consumption history |
| Execution logs | Provider-reported software executions |
| Spent-state snapshots | Final durable consumed-authority state |
| SHA-256 manifests | Original published file identities |

No individual transport receipt, hub log, or provider event proves the entire experiment.

The T03 conclusion specifically requires matching the original T01 requests to fresh provider ingress, authenticated denial events, and unchanged recorded consumption/execution history.

The final evidence supports that correlation.

## 15. Findings and Limitations

### Supported Findings

Within the recorded MH001 environment:

1. Two separate forwarding hubs operated with static routes.
2. Both independent providers accepted valid T01 authority.
3. Requests were subsequently delivered through a changed forwarding path.
4. Both providers received exact replays of their spent T01 authorizations.
5. Both providers signed `DENY / auth_spent`.
6. No additional replay consumption or execution appears in the final provider histories.
7. Both providers subsequently accepted fresh T04 authority.
8. The independent observer preserved verifiable provider-originated events.

### Outside the Tested Scope

MH001 does not establish:

- Physical actuator execution.
- Security following provider private-key compromise.
- Comprehensive malicious-hub compromise resistance.
- Correctness across arbitrary routing topologies.
- Universal absence of packet loss or unobserved traffic.
- Global ordering based on synchronized host clocks.
- Provider-outcome relay through the hubs.
- Strict completion of the two undocumented procedural checkpoints.

Provider-outcome relay was explicitly excluded from MH001 scoring and deferred to subsequent work.

The tested result concerns authority enforcement across the specified forwarding-path change.

## 16. Reproduction and Preservation

The experiment design and operator requirements are preserved in:

- [MH001 experiment overview](README.md)
- [Scored-run documentation](MH001_R43_RUN001/README.md)
- [Frozen operator gates](MH001_R43_RUN001/frozen_R43/OPERATOR_GATES.md)
- [Source and evidence records](MH001_R43_RUN001/)

A new independent run must use separately approved signing trust, persistent state, and evidence paths.

The historical run must not be reset, rerun in place, repaired, or overwritten.

Original failures and incomplete attempts remain part of the published record.

This RESULTS.md is supplemental documentation, not an original scored evidence artifact.

---

## Conclusion

MH001 tested whether a consumed provider authorization could become executable again when the same request reached the provider through a different forwarding hub.

Both providers rejected the exact replay with signed `DENY / auth_spent` decisions.

Neither recorded additional replay consumption or execution.

Both subsequently accepted distinct fresh authorizations.

**Functional result: Provider A PASS / Provider B PASS.**

**Procedural qualification: Two frozen checkpoints were not separately documented.**

The experiment supports the conclusion that the tested forwarding-path change did not restore consumed provider-controlled execution authority.
