
# MH001 — Provider-Ingress Packet Evidence

## Purpose

This directory contains the original network packet captures recorded at both provider hosts during the MH001 R4.3 experiment.

The captures provide independent evidence of the HTTP requests actually received by each provider, rather than relying exclusively on requester or hub forwarding logs.

**Session:** `MH001_R43_RUN001`

**Capture date:** November 7, 2026

**Result:** Eight provider-ingress requests verified.

## 1. Directory Contents

| File | Provider | Recorded endpoint |
|---|---|---|
| `provider_a_18090.pcap` | PROVIDER_A | 192.168.1.118:18090 |
| `provider_b_18091.pcap` | PROVIDER_B | 192.168.1.107:18091 |

These are original classic PCAP captures, not regenerated request representations.

Both were captured on the respective provider machines using `tcpdump`.

The capture processes were stopped cleanly after T04.

### Capture Statistics

| Property | Provider A | Provider B |
|---|---:|---:|
| Captured packets | 40 | 40 |
| Packets reported received by filter | 40 | 40 |
| Reported kernel drops | 0 | 0 |
| File size | 7,710 bytes | 7,710 bytes |
| HTTP request payloads | 4 | 4 |

The zero-drop counts are the reported `tcpdump` capture statistics. They do not establish absence of every possible packet loss outside the capture facility.

## 2. Original Capture Integrity

SHA-256 values:

| Capture | SHA-256 |
|---|---|
| `provider_a_18090.pcap` | `d5aad81b773d1f956473004e2118cc41fb965a7796cdc31e5ad81cce05cb3064` |
| `provider_b_18091.pcap` | `20fda67122fde9dec0eeefc8b121cdc2f6dfe0efe6900f90e9a6f4d435618f9c` |

These values were verified following transfer from the provider machines to the independent controller.

Both files are included in:

`evidence/MH001_FINAL_SHA256SUMS.txt`

The path above is relative to the MH001 scored-run root.

### Verify with Linux

From this directory:

```bash
sha256sum provider_a_18090.pcap
sha256sum provider_b_18091.pcap
```

### Verify with PowerShell

From this directory:

```powershell
Get-FileHash .\provider_a_18090.pcap -Algorithm SHA256
Get-FileHash .\provider_b_18091.pcap -Algorithm SHA256
```

All comparisons must use the original file bytes.

## 3. Captured Request Sequence

Each provider received four requests during the recorded experiment:

1. Rehearsal.
2. T01 original authorization.
3. T03 exact replay of T01.
4. T04 separately authorized fresh execution.

### Provider A

| Phase | Incoming source | Recorded destination |
|---|---|---|
| Rehearsal | 192.168.1.100 | 192.168.1.118:18090 |
| T01 | 192.168.1.100 | 192.168.1.118:18090 |
| T03 | 192.168.1.106 | 192.168.1.118:18090 |
| T04 | 192.168.1.106 | 192.168.1.118:18090 |

Provider A originally received requests from Hub A.

After Hub A was terminated, Provider A received the T03 and T04 requests from Hub B.

### Provider B

| Phase | Incoming source | Recorded destination |
|---|---|---|
| Rehearsal | 192.168.1.106 | 192.168.1.107:18091 |
| T01 | 192.168.1.106 | 192.168.1.107:18091 |
| T03 | 192.168.1.106 | 192.168.1.107:18091 |
| T04 | 192.168.1.106 | 192.168.1.107:18091 |

Provider B's immediately preceding hop was Hub B throughout the experiment.

During T01, Provider B's request first traversed Hub A and then Hub B.

During T03 and T04, the requester contacted Hub B directly.

The Provider B capture alone does not establish the upstream hop through Hub A. That route is corroborated by the separate hub logs and requester receipts.

## 4. Original Request Files

The packet captures should be compared against the original request representations preserved elsewhere in the scored-run directory.

| Phase | Provider A request | Provider B request |
|---|---|---|
| Rehearsal | `rehearsal_requests/provider_a/request.http` | `rehearsal_requests/provider_b/request.http` |
| T01 | `t01_requests/provider_a/request.http` | `t01_requests/provider_b/request.http` |
| T03 | Reuses T01 request | Reuses T01 request |
| T04 | `t04_requests/provider_a/request.http` | `t04_requests/provider_b/request.http` |

Paths are relative to `MH001_R43_RUN001/`.

Each request directory also contains:

- `body.bin` — original HTTP request body.
- `requester_observation.json` — prepared request and authorization hash identities.

The T03 replay deliberately has no separate reconstructed request directory.

It reused the original T01 request bytes.

## 5. Expected HTTP Host Rewrite

The prepared requests contain:

```http
Host: requester.invalid
```

The mechanical forwarding implementation rewrites the HTTP `Host` header to the next destination endpoint.

At Provider A ingress:

```http
Host: 192.168.1.118:18090
```

At Provider B ingress:

```http
Host: 192.168.1.107:18091
```

This behavior is implemented in:

`frozen_R43/wire.py`

The provider source review confirmed that `Host` was not included in the provider's signed authorization binding.

The comparison therefore permits this specific expected transport-header rewrite.

It does not permit changes to:

- HTTP method, path, or query.
- The provider destination header.
- Authorization body bytes.
- Content length.
- Other preserved header fields.
- Original authorization identity or bindings.

The prepared and captured HTTP messages are not expected to have identical full-message SHA-256 values because their `Host` fields differ.

The T01 and T03 requests **at provider ingress**, however, must be fully byte-identical to one another.

## 6. Original Request Body Hashes

The following values identify the raw authorization-bearing HTTP bodies.

| Phase | Provider A SHA-256 | Provider B SHA-256 |
|---|---|---|
| Rehearsal | `7542baa24b67649bd6ee99513943267d9a6c8ba3170418b5dba56ff209e77b2c` | `6b25e82ceb564d7b62ec238e2df5072beeeec89022b141d031cfc54e01fe7dc7` |
| T01 | `83071f65a756aeb0c02206de5e331a564516818c1081a58905076de260afc99c` | `578455981c69b3955dad7c6a7cb15409fafc117d2dcc85dc34cb432f6d3fe1f0` |
| T03 | Same as T01 | Same as T01 |
| T04 | `c6591697c79a356b8ccf9ccb16da2dca2f379789ecfbf53fa6fbc3a1de605f39` | `855a7d10541370bdea080add62a90c9694cc697caa93365cfe920bc112c61ed6` |

These are body hashes, not PCAP-file hashes.

The body comparison verifies preservation of the authorization-bearing request data across the forwarding path.

## 7. Independently Inspect the Captures

Wireshark or `tcpdump` can inspect the captured connections without sending requests or modifying the files.

For example, from this directory:

```bash
tcpdump -nn -tttt -r provider_a_18090.pcap 'dst port 18090 and greater 200'
```

And:

```bash
tcpdump -nn -tttt -r provider_b_18091.pcap 'dst port 18091 and greater 200'
```

Each capture contains four distinct inbound HTTP request payloads in chronological order.

The recorded requests were contained in individual TCP payload packets. This permits direct byte extraction for this historical capture.

For a new experiment with fragmented or segmented requests, reconstruct the complete TCP streams before comparison. Do not assume that every request arrives in a single packet.

### Required Byte Comparison

For each provider:

1. Extract the four HTTP request payloads.
2. Confirm their source and destination addresses.
3. Read the corresponding original `request.http` file as bytes.
4. Replace only the prepared `Host` header with the expected provider endpoint.
5. Compare the resulting expected request to the captured HTTP payload byte-for-byte.
6. Confirm the captured body SHA-256 matches its recorded requester observation.
7. Confirm T01 and T03 captured HTTP requests are byte-identical.
8. Confirm T04 differs from the original authorization request.

If any unexpected byte differs, stop and report the discrepancy. Do not rewrite evidence or normalize the authorization.

## 8. Recorded Byte-Comparison Results

The original post-run verification returned:

| Check | Provider A | Provider B |
|---|---|---|
| Rehearsal request | PASS | PASS |
| T01 request | PASS | PASS |
| T03 replay request | PASS | PASS |
| T04 fresh request | PASS | PASS |
| T01/T03 exact replay | PASS | PASS |

**Total: 8/8 provider-ingress requests verified.**

For both providers, T01 and T03 had identical captured HTTP request bytes.

This result was reached after correcting the initial comparison to account for the expected `Host` rewrite.

The original PCAPs were not changed.

## 9. How to Capture Ingress During Reproduction

For a new, separately authorized laboratory experiment, use passive capture on each provider host before submitting any rehearsal or scored request.

A typical Linux capture command is:

```bash
sudo tcpdump -i <provider-interface> -s 0 -w <new-capture-file.pcap> 'tcp dst port 18090'
```

Use port `18091` for Provider B and the actual reviewed interface and port in a different deployment.

This is an example for a new experiment, not a command to rerun against the historical MH001 session.

For independent reproducibility:

1. Begin capture before rehearsal.
2. Preserve the original T01 requests.
3. Continue capture through T02, T03, and T04.
4. Do not retry a request whose execution outcome is uncertain.
5. Stop capture cleanly after the last transaction.
6. Record packet and drop statistics.
7. Preserve the original capture bytes.
8. Hash the resulting PCAP files.
9. Compare complete provider-ingress requests with the preserved requester originals.

Capture tooling must not modify provider authorization or execution logic.

## 10. Evidence Correlation and Limits

Packet captures establish observed network ingress.

They do not independently prove provider authorization acceptance, denial, consumption, or execution.

For those results, correlate the requests with:

- Independent signed provider events in `evidence/observer.jsonl`.
- Provider consumption ledgers in `evidence/final_remote/`.
- Provider execution records in `evidence/final_remote/`.
- Hub forwarding logs in `evidence/final_remote/`.
- Requester transmission receipts in `evidence/requester/`.

The packet capture is particularly important for T03.

It establishes that the replayed requests reached the providers again, through the alternate route, without changing the authorization-bearing request bytes.

The signed observer evidence establishes that both providers independently returned `DENY / auth_spent`.

Neither evidence source replaces the other.

## 11. Preservation

Both original PCAPs are members of the scored 132-file evidence inventory.

This README is supplemental documentation added after the scored run.

Do not edit, regenerate, truncate, or replace the original captures.

**Conclusion:** Both providers received the original spent requests again. Changing the forwarding route did not restore their authorization.
