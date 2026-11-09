
# MH001 — Requester Transmission Evidence

## Purpose

This directory preserves requester-side transport evidence from the MH001 R4.3 scored experiment.

The requester was the HP OmniBook. It submitted previously prepared provider-bound HTTP requests to approved coordination hubs.

The requester did not issue provider authorization, validate provider signatures, or determine whether an operation executed.

This directory records what the requester attempted to transmit, which hub it contacted, and whether an HTTP response was received.

**Session:** `MH001_R43_RUN001`

**Requester:** HP OmniBook

**Implementation:** `frozen_R43/requester.py`

## 1. Directory Contents

```text
requester/
├── MH001_requester1.etl
├── rehearsal_provider_a_via_hub_a_receipt.jsonl
├── rehearsal_provider_b_via_hub_a_receipt.jsonl
├── t01_provider_a_via_hub_a_receipt.jsonl
├── t01_provider_b_via_hub_a_receipt.jsonl
├── t03_provider_a_via_hub_b_receipt.jsonl
├── t03_provider_b_via_hub_b_receipt.jsonl
├── t04_provider_a_via_hub_b_receipt.jsonl
└── t04_provider_b_via_hub_b_receipt.jsonl
```

The eight JSONL files contain requester transport receipts.

`MH001_requester1.etl` contains the original Windows requester-side packet-monitoring capture.

The ETL is preserved in its original Windows format. It was not replaced with a reconstructed PCAP.

## 2. Requester Implementation

The frozen requester implementation is located at:

`frozen_R43/requester.py`

That path is relative to the MH001 scored-run root.

The requester supports two distinct operations.

### Prepare

The `prepare` action accepts:

- Original operation bytes.
- An already-issued provider authorization package.
- Verification context.
- Provider destination.
- An exclusive output directory.

It constructs:

- `request.http`
- `body.bin`
- `requester_observation.json`

The requester does not mint or sign authorization.

The recorded observation field:

`signature_verified_by_adapter: false`

means the requester adapter does not independently verify the issued provider signature.

Provider authorization validation remains the provider's responsibility.

### Send

The `send` action submits the preserved HTTP request bytes to one explicitly approved hub endpoint.

Remote transmission requires an exact IP-address and port match in the separate approved-hubs configuration.

The requester:

- Reads the existing request bytes.
- Validates HTTP framing.
- Creates an exclusive receipt file.
- Records the intended transport operation before submission.
- Makes one send attempt.
- Records the transport result.
- Does not automatically retry.

A transport response does not establish successful provider execution.

## 3. Recorded Hub Endpoints

| Hub | Recorded address |
|---|---|
| Hub A | `192.168.1.100:18080` |
| Hub B | `192.168.1.106:18081` |

The approved endpoint list used by the scored run is preserved at:

`configs/approved_hubs.json`

The addresses are historical laboratory values, not deployment defaults.

## 4. Transmission Sequence

Eight receipt files document the rehearsal and scored requests.

| Phase | Provider | Requester destination | Recorded transport result |
|---|---|---|---|
| Rehearsal | A | Hub A | response_received |
| Rehearsal | B | Hub A | response_received |
| T01 | A | Hub A | response_received |
| T01 | B | Hub A | response_received |
| T03 | A | Hub B | response_received |
| T03 | B | Hub B | response_received |
| T04 | A | Hub B | response_received |
| T04 | B | Hub B | response_received |

The T01 routing was intentionally asymmetric.

Provider A:

```text
Requester → Hub A → Provider A
```

Provider B:

```text
Requester → Hub A → Hub B → Provider B
```

Following Hub A termination, the requester submitted both T03 replays directly through Hub B.

T04 also used Hub B for both providers.

The receipts identify the requester's first network hop. They do not independently establish every downstream forwarding hop.

## 5. Receipt Format

Each successful receipt contains two JSONL records.

### First Record — Transmission Pending

The first record includes:

- `timestamp`
- `hub`
- `packet_sha256`
- `body_sha256`
- `provider_execution`
- `transport_result`

Its transport result is:

`send_pending`

This record is written and flushed before the network send attempt.

It is not proof that the request reached the hub or provider.

### Second Record — Transport Completion

The second record retains the original request identity and adds:

- `transport_result: response_received`
- `response_sha256`

This confirms that the requester received a complete framed HTTP response through the transport path.

It does not independently establish authorization acceptance or execution.

Every preserved receipt retains:

`provider_execution: NOT_INFERRED`

That field is intentional.

The requester does not infer execution from an HTTP response.

### Transport Error Behavior

The implementation can instead record:

`TRANSPORT_ERROR_EXECUTION_UNKNOWN`

when transport fails.

An unknown transport outcome must not trigger an automatic replay, because the provider may already have consumed the authorization.

The eight published MH001 receipts ended with `response_received`, not that transport-error outcome.

## 6. Exact T01/T03 Request Identity

The central requester-side comparison is between T01 and T03.

### Provider A

T01 request SHA-256:

`bf748793a91e35f53e5f2137d78239021e77036b3e462a639369cc3403cf0c33`

T03 request SHA-256:

`bf748793a91e35f53e5f2137d78239021e77036b3e462a639369cc3403cf0c33`

Body SHA-256 for both:

`83071f65a756aeb0c02206de5e331a564516818c1081a58905076de260afc99c`

### Provider B

T01 request SHA-256:

`ddcec53dad222c60b134a8cb0145f18b241d6c7177febd2cd7925600591dbf84`

T03 request SHA-256:

`ddcec53dad222c60b134a8cb0145f18b241d6c7177febd2cd7925600591dbf84`

Body SHA-256 for both:

`578455981c69b3955dad7c6a7cb15409fafc117d2dcc85dc34cb432f6d3fe1f0`

Both providers' requester receipt pairs show identical original and replay request hashes.

The same T01 `request.http` files were used for the T03 replay.

These receipt hashes identify prepared requester HTTP bytes, before the hub's permitted transport-level `Host` rewrite.

Provider-ingress captures independently establish the bytes that actually arrived at each provider.

## 7. Fresh T04 Requests

T04 required separate, newly issued provider authorization.

### Provider A

Request SHA-256:

`d28618c574cc1867aa8cf5d696fcfb97908b6dcda709857d6679bdc7291d1139`

Body SHA-256:

`c6591697c79a356b8ccf9ccb16da2dca2f379789ecfbf53fa6fbc3a1de605f39`

### Provider B

Request SHA-256:

`d884a52fb6a4bd5bfc546b2eca6ef24129f0c2dbc2495d345c52e0b4acba7ecb`

Body SHA-256:

`855a7d10541370bdea080add62a90c9694cc697caa93365cfe920bc112c61ed6`

These differ from the corresponding T01 authorization-bearing requests.

Both T04 transmissions went directly to Hub B.

## 8. Windows Packet Capture

File:

`MH001_requester1.etl`

The capture was recorded using Windows Packet Monitor (PktMon) on the OmniBook.

It covered the requester-side network activity during the experiment and was stopped after the scored transactions.

The original capture was preserved without conversion or reconstruction.

### File Integrity

Size: 60,444 bytes

SHA-256:

`97262a251cf1430d5ac9e5e08b61599c90e490cf2448809caa2f049e8d0441c1`

### Inspecting the Capture

Use Windows Packet Monitor or compatible ETL analysis tooling to inspect the original file.

The ETL is supplemental requester-side network evidence.

Do not assume its contents are equivalent to the complete provider-ingress PCAPs.

The independent provider captures are preserved under:

`evidence/ingress/`

A requester-side observation cannot replace proof that the provider received the original request.

## 9. Verify Receipt File Integrity

Each receipt is included in the original MH001 scored manifest.

Expected SHA-256 values:

| Receipt | SHA-256 |
|---|---|
| Rehearsal A | `055fb5833db5c8b572f3707a5775c6330fd4396c2fd48eef0a538768cdf80a88` |
| Rehearsal B | `85c98a022292f61a6cf4f55f4ef7ada636bb06b4af495378b76c0d127e98b679` |
| T01 A | `43c8ec7a6f0cc6dc13c4b9d7a5b2160a5bb3f5060a6749151c2cd8187af074d1` |
| T01 B | `b72704212f74f18e2eaf7f58e6b1e08dffbab1b946c7a7b999d4e3336affd99e` |
| T03 A | `47213025f80ccf649eca822225ed7de31e9e0c90b17fbdf4ab13aa8f1cbeb552` |
| T03 B | `befb5cbb33e022503a6aea64250dfee0487fcd90c3a250dbe8c78f1563ff68c9` |
| T04 A | `866c1e89752c47d7ee6af16ad09e921dfaad8adc5eb8cffc8aa9bc38972572e3` |
| T04 B | `1719736a64da7240fcc27529988761b932260cd2494619937352068c894d2255` |

These are receipt-file hashes, not the request hashes recorded inside each receipt.

### Inspect the Original Receipts

From this directory on Linux:

```bash
cat t01_provider_a_via_hub_a_receipt.jsonl
cat t03_provider_a_via_hub_b_receipt.jsonl
```

Or in PowerShell:

```powershell
Get-Content .\t01_provider_a_via_hub_a_receipt.jsonl
Get-Content .\t03_provider_a_via_hub_b_receipt.jsonl
```

Repeat for Provider B.

### Verification Checklist

For each provider:

1. Confirm T01 contains `send_pending` followed by `response_received`.
2. Confirm T03 contains the same two recorded transport stages.
3. Confirm T01 contacted Hub A.
4. Confirm T03 contacted Hub B.
5. Confirm T01 and T03 have identical `packet_sha256`.
6. Confirm T01 and T03 have identical `body_sha256`.
7. Confirm `provider_execution` remains `NOT_INFERRED`.
8. Confirm T04 uses a different request identity.
9. Confirm each receipt-file hash matches the scored manifest.

A successful receipt is evidence of completed requester-side transport, not an independent provider execution decision.

## 10. Correlate with Other Evidence

For full MH001 verification, correlate the requester records with the following scored-run evidence:

| Evidence | Purpose |
|---|---|
| `t01_requests/` | Original prepared requests |
| `t04_requests/` | Separately authorized fresh requests |
| `evidence/ingress/` | Independently captured provider-ingress HTTP requests |
| `evidence/final_remote/` | Hub forwarding logs and provider persistent records |
| `evidence/observer.jsonl` | Independently verified provider-signed decisions |

All paths above are relative to the scored-run root.

The requester receipts establish that identical request bytes were submitted to different first-hop hubs.

The provider captures establish that the same authorization-bearing request bytes reached the providers.

The independent signed observer records and provider ledgers establish the resulting authorization and execution behavior.

These evidence sources serve different purposes and must not be substituted for one another.

## 11. Reproduction Requirements

For a new, separately approved MH001 experiment:

1. Use the reviewed requester implementation.
2. Establish an explicit, limited list of approved hub endpoints.
3. Obtain provider-issued authorization under the corresponding provider's control.
4. Prepare the request using the already-issued authorization.
5. Preserve the generated `request.http`, `body.bin`, and requester observation.
6. Submit the T01 request once and preserve its exclusive receipt.
7. After the authorized hub-termination stage, submit the same T01 request bytes through the alternate approved hub.
8. Preserve the T03 receipt without rewriting or reminting the original authorization.
9. Obtain separate fresh authorization for T04.
10. Submit the new request once and preserve its receipt.
11. Independently validate provider-ingress evidence, signed decisions, and persistent state.

Use new receipt paths for a new experiment.

Never overwrite historical receipts or resend automatically when the transport outcome is unknown.

## 12. Preservation Boundary

The original ETL file and eight receipts are members of the scored 132-file evidence inventory.

This README is supplemental publication documentation.

Do not regenerate the receipts, convert and replace the ETL, normalize line endings, or alter the original request hashes.

**Requester-side conclusion:** The same original authorization requests were submitted through a different hub without modifying their prepared bytes. Provider execution outcomes were determined independently.
