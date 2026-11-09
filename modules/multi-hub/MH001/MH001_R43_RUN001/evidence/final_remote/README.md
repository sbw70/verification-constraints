
# MH001 — Hub Forwarding and Provider Evidence

## Purpose

This directory preserves forwarding records from both independent coordination hubs and final persistent-state evidence from both providers during the MH001 R4.3 experiment.

These records allow an independent reviewer to correlate:

- Which hub received each request.
- Which downstream endpoint the hub selected.
- Whether the request body was preserved during forwarding.
- Whether an HTTP response was relayed.
- What authorization-consumption and execution history each provider ultimately recorded.

The hubs are mechanical forwarding components.

They do not issue authorizations, determine provider execution outcomes, or maintain provider consumption state.

**Session:** `MH001_R43_RUN001`

**Scored experiment:** T01–T04

## 1. Directory Contents

```text
final_remote/
├── hub_a.jsonl
├── hub_b.jsonl
├── provider_a/
│   ├── provider_a_consume_ledger.jsonl
│   ├── provider_a_execution.jsonl
│   ├── provider_a_spent_state.json
│   └── README.md
└── provider_b/
    ├── provider_b_consume_ledger.jsonl
    ├── provider_b_execution.jsonl
    ├── provider_b_spent_state.json
    └── README.md
```

The two hub JSONL files contain forwarding observations.

The provider directories contain independently maintained persistent consumption, execution, and spent-state records.

The provider-specific READMEs document their respective evidence in greater detail.

## 2. Recorded Hub Topology

### Hub A

**Hardware:** Raspberry Pi 3B+

**Endpoint:** `192.168.1.100:18080`

**Downstream timeout:** 15 seconds

Recorded routes:

| Destination | Next hop |
|---|---|
| PROVIDER_A | Provider A — 192.168.1.118:18090 |
| PROVIDER_B | Hub B — 192.168.1.106:18081 |

### Hub B

**Hardware:** HP Pavilion

**Endpoint:** `192.168.1.106:18081`

**Downstream timeout:** 10 seconds

Recorded routes:

| Destination | Next hop |
|---|---|
| PROVIDER_A | Provider A — 192.168.1.118:18090 |
| PROVIDER_B | Provider B — 192.168.1.107:18091 |

Both hubs used separately configured, statically defined routes.

The hub implementations did not select alternate endpoints or retry failed transmissions.

## 3. Hub Log Format

Each accepted request generates two principal log records.

### Ingress Record

An `observation` value of:

`ingress`

Records information including:

- Hub identity.
- Hub-local request sequence.
- Timestamp.
- Selected next hop.
- Request-body SHA-256.
- Preserved-header names and value hashes.
- Initial transport status.

The ingress record is flushed before downstream submission.

It does not establish successful downstream delivery.

### Result Record

An `observation` value of:

`result`

Records the final observed transport outcome.

For the successful MH001 forwarding operations:

`transport_result: response_forwarded`

The result record also includes the egress request-body SHA-256.

A `response_forwarded` result means the hub received and forwarded a framed downstream HTTP response.

It does not independently establish that a provider authorized or executed an operation.

Provider outcomes require independent signed-event and persistent-state verification.

## 4. Hub A — Recorded Forwarding

File:

`hub_a.jsonl`

The original log contains eight JSONL records representing four requests.

Each request has an ingress and result record.

| Hub sequence | Phase | Destination | Next hop |
|---|---|---|---|
| 1 | Rehearsal | PROVIDER_A | PROVIDER_A |
| 2 | Rehearsal | PROVIDER_B | HUB_B |
| 3 | T01 | PROVIDER_A | PROVIDER_A |
| 4 | T01 | PROVIDER_B | HUB_B |

All four result records report:

`response_forwarded`

For every request, the ingress and egress body hashes match.

### Hub A — T01 Provider A

Body SHA-256:

`83071f65a756aeb0c02206de5e331a564516818c1081a58905076de260afc99c`

Next hop:

`PROVIDER_A`

### Hub A — T01 Provider B

Body SHA-256:

`578455981c69b3955dad7c6a7cb15409fafc117d2dcc85dc34cb432f6d3fe1f0`

Next hop:

`HUB_B`

This request was forwarded to Hub B rather than directly to Provider B.

Hub A contains no T03 or T04 forwarding records.

The designated MH001 Hub A process was terminated during T02.

The absence of later records is consistent with that termination, but the log alone does not prove process or listener absence. That requires the separate operator and process observations.

## 5. Hub B — Recorded Forwarding

File:

`hub_b.jsonl`

The original log contains twelve JSONL records representing six requests.

| Hub sequence | Phase | Destination | Next hop |
|---|---|---|---|
| 1 | Rehearsal | PROVIDER_B | PROVIDER_B |
| 2 | T01 | PROVIDER_B | PROVIDER_B |
| 3 | T03 | PROVIDER_A | PROVIDER_A |
| 4 | T03 | PROVIDER_B | PROVIDER_B |
| 5 | T04 | PROVIDER_A | PROVIDER_A |
| 6 | T04 | PROVIDER_B | PROVIDER_B |

All six result records report:

`response_forwarded`

For every request, ingress and egress body hashes match.

### T01 — Chained Forwarding

Provider B's T01 request traversed:

```text
Requester
    |
    v
  Hub A
    |
    v
  Hub B
    |
    v
Provider B
```

The same T01 Provider B body hash appears in both hub logs:

`578455981c69b3955dad7c6a7cb15409fafc117d2dcc85dc34cb432f6d3fe1f0`

Hub A records forwarding to Hub B.

Hub B records forwarding to Provider B.

This provides separate observations of the chained route.

### T03 — Alternate Path Replay

After Hub A was terminated, the requester sent the original requests directly to Hub B.

Provider A body SHA-256:

`83071f65a756aeb0c02206de5e331a564516818c1081a58905076de260afc99c`

Provider B body SHA-256:

`578455981c69b3955dad7c6a7cb15409fafc117d2dcc85dc34cb432f6d3fe1f0`

These match the respective T01 body hashes.

Hub B forwarded both requests and relayed their HTTP responses.

The independent observer subsequently verified both provider-signed `DENY / auth_spent` events.

The hub log itself does not classify those responses as authorization denials.

### T04 — Fresh Authority

The requester submitted separately issued fresh authorizations through Hub B.

Provider A body SHA-256:

`c6591697c79a356b8ccf9ccb16da2dca2f379789ecfbf53fa6fbc3a1de605f39`

Provider B body SHA-256:

`855a7d10541370bdea080add62a90c9694cc697caa93365cfe920bc112c61ed6`

Both bodies differ from their corresponding T01 requests.

Both were forwarded successfully at the transport layer.

Independent signed-event and provider-state records establish the fresh executions.

## 6. Original Hub Log Integrity

The original hub logs were transferred from their respective machines to the OmniBook.

Each transferred file was SHA-256 verified against its source.

| File | SHA-256 |
|---|---|
| `hub_a.jsonl` | `0b59483f08163e4ce216fffa5b4ec3934cb1b91eeb392c3d150a24ee9319df8c` |
| `hub_b.jsonl` | `5f5210a34780ecc2fac9f3fecf646bab3de627d0dbcc690e6046f0ef569a76bb` |

Both are included in the original MH001 final evidence manifest.

### Verify on Linux

From this directory:

```bash
sha256sum hub_a.jsonl
sha256sum hub_b.jsonl
```

### Verify on PowerShell

From this directory:

```powershell
Get-FileHash .\hub_a.jsonl -Algorithm SHA256
Get-FileHash .\hub_b.jsonl -Algorithm SHA256
```

The computed values must match the published hashes.

Do not normalize or reformat the original JSONL files.

## 7. Verify Hub Forwarding Records

Each original JSONL line represents one observation.

An independent reviewer should:

1. Parse each line as a JSON object.
2. Verify `hub_id` matches the file's designated hub.
3. Group records by hub-local `sequence`.
4. Confirm each successful request has one `ingress` and one `result` record.
5. Confirm the request's selected `next_hop` is consistent across those records.
6. Confirm the result's `ingress_body_sha256` and `egress_body_sha256` match.
7. Confirm `transport_result` is `response_forwarded`.
8. Compare preserved-header names and value hashes against the original request and corresponding observations at other hops.
9. Correlate each request with the appropriate requester receipt and provider-ingress capture.

For the recorded successful requests, the expected grouping is:

| Hub | Requests | Records |
|---|---:|---:|
| Hub A | 4 | 8 |
| Hub B | 6 | 12 |
| **Total** | **10** | **20** |

These are ten hub-handling events, not ten distinct provider authorizations.

Provider B's rehearsal and T01 requests each traversed both hubs, producing observations in both files.

## 8. Header Preservation

The original logs contain `preserved_headers` records.

For the recorded requests, these include:

- `X-MH-Destination`
- `Content-Type`
- `Content-Length`

The records preserve cryptographic hashes of the header values and their wire representations rather than recording the complete authorization-bearing requests.

The hub implementation may rewrite the HTTP `Host` field for the next endpoint.

`Host` is transport metadata and is excluded from the retained header set in the frozen forwarding implementation.

Other preserved header values must remain consistent across the forwarding path.

The complete provider-ingress HTTP bytes are independently preserved in:

`evidence/ingress/`

That path is relative to the scored-run root.

Hub logs do not replace the independent packet captures.

## 9. Final Provider Evidence

The `provider_a/` and `provider_b/` subdirectories contain the final provider-controlled state after T04.

Each includes:

- A hash-linked consumption ledger.
- A local execution log.
- A spent-authority snapshot.

### Provider A

Final ledger sequence: `3`

Final ledger head:

`c4a600ca733c67a95652c3fb3add5764a1d0fbff44111493ea0967d9d7338876`

Recorded software executions: `3`

### Provider B

Final ledger sequence: `3`

Final ledger head:

`1ed8542ff8885e1a7764b18b625626187efc6de2feea0ea69088d51308d73c41`

Recorded software executions: `3`

For both providers, the three recorded consumptions correspond to:

1. Rehearsal.
2. T01.
3. T04.

Neither provider recorded a fourth consumption or execution for T03.

The provider-specific READMEs document the original file hashes and verification procedures.

## 10. Cross-Evidence Verification

To independently evaluate MH001, correlate this directory with the other recorded evidence.

### Requester Receipts

`evidence/requester/`

Confirm the original first-hop routing:

- Rehearsal and T01 through Hub A.
- T03 and T04 through Hub B.

### Provider-Ingress Captures

`evidence/ingress/`

Verify that all eight HTTP requests arrived at their intended providers.

For both providers, compare the actual T01 and T03 ingress requests byte-for-byte.

The T03 replay must match T01 at the provider boundary.

### Independent Signed Events

`evidence/observer.jsonl`

Verify that:

- T01 produced signed START and COMPLETE events.
- T03 produced signed `DENY / auth_spent` events.
- T04 produced signed START and COMPLETE events.
- The events identify the correct providers and signing keys.
- Recorded authorization IDs, nonces, bindings, operation IDs, and ledger heads agree with provider evidence.

### Provider Persistent State

Confirm both consumption ledgers and spent snapshots contain the original T01 authorizations as spent.

Confirm no additional T03 consumption or execution exists.

All cross-evidence paths above are relative to `MH001_R43_RUN001/`.

## 11. Timestamp and Ordering Limitations

Hub A and Hub B used independent host clocks.

Cross-host timestamp comparisons must not be treated as authoritative proof of event ordering.

Use:

- Hub-local sequence numbers.
- Request body hashes.
- Preserved-header hashes.
- Requester receipts.
- Provider-ingress captures.
- Independent observer records.
- Provider ledger sequences.

These records establish relationships more reliably than assuming synchronized clocks.

A hub-local sequence number identifies its own request order. Hub A and Hub B sequence numbers are not interchangeable.

## 12. Reproduction Requirements

For a new, separately approved MH001 experiment:

1. Use the frozen R4.3 forwarding implementation.
2. Configure two independent hubs with separate static route files.
3. Verify both routing configurations together before startup.
4. Ensure Hub A forwards Provider A directly and Provider B through Hub B.
5. Ensure Hub B forwards directly to both providers.
6. Establish exclusive, new hub log files.
7. Enable independent provider-ingress capture.
8. Establish a separate independent signed-event observer.
9. Perform the rehearsal and T01 sequentially.
10. Preserve the original T01 requests and initial provider state.
11. Obtain the required operator approval before terminating Hub A.
12. Confirm that the designated Hub A process and listener are absent.
13. Submit the exact original T01 requests through Hub B.
14. Verify independent signed `DENY / auth_spent` results and unchanged consumption/execution history.
15. Reconfirm Hub A remains absent.
16. Submit separately issued fresh authority through Hub B.
17. Verify the fresh executions and ledger advancement.
18. Stop evidence collection cleanly and preserve original file hashes.

The reviewed runtime implementation is located in:

`frozen_R43/`

The original live route configurations are located in:

`frozen_R43/live_review_R43/`

Both paths are relative to the scored-run root.

Use new experiment-specific paths, keys, trust identities, logs, and persistent state for a fresh independent run.

Do not restart the historical experiment or reuse already-spent historical authorizations as live authority.

The original test private keys are publicly disclosed and must not be used as trusted credentials in an operational environment.

## 13. Evidence Limits

The hub logs establish observed forwarding behavior.

They do not independently establish:

- Provider authorization validity.
- Provider execution success.
- Persistent ledger integrity.
- Hub A process termination.
- Absence of every possible network delivery anomaly.

Those conclusions require the corresponding independent evidence.

The original T02 Hub A termination was verified operationally. There is no separate T02 termination event in these hub JSONL files.

An immediate pre-T04 Hub A reconfirmation was not separately documented in the final procedural review.

This limitation must not be silently replaced with an assumption derived from the absence of Hub A log entries.

Provider-outcome relay through hubs was outside MH001 scoring. Provider-signed outcomes were sent independently to the observer.

## 14. Preservation Boundary

The two hub logs and six provider-state files are members of the original 132-file scored evidence inventory.

This README is supplemental documentation added after publication.

Do not edit, regenerate, replace, truncate, or normalize the original JSONL or JSON evidence.

Do not add new records to the historical hub logs.

Do not reset or repair the historical provider consumption ledgers.

**Conclusion:** Hub forwarding remained mechanical. Changing the route did not restore either provider's spent execution authority.
