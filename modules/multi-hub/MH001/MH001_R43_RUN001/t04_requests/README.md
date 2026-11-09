
# MH001 — T04 Fresh Authorization Requests

## Purpose

This directory preserves the original HTTP requests used in T04 of the MH001 R4.3 multi-hub experiment.

T04 tested whether both providers could accept **new, independently issued authority** after rejecting the replayed T01 requests during T03.

The distinction is important:

- T03 reused already-consumed authority and was denied.
- T04 used new authority and was accepted.
- Neither provider reset its consumption history.

**Session:** `MH001_R43_RUN001`

**Test:** T04 — Fresh Authority Through Hub B

**Recorded outcome:** Both providers executed once.

## 1. Directory Contents

```text id="6unht8"
t04_requests/
├── provider_a/
│   ├── body.bin
│   ├── request.http
│   └── requester_observation.json
└── provider_b/
    ├── body.bin
    ├── request.http
    └── requester_observation.json
```

Each provider directory contains three original artifacts.

| File | Purpose |
|---|---|
| `request.http` | Complete prepared HTTP request |
| `body.bin` | Original authorization-bearing request body |
| `requester_observation.json` | Operation, package, binding, body, and request hashes |

These six files are part of the original scored-run evidence inventory.

## 2. Original Source Materials

The T04 requests were prepared using:

| Material | Provider A | Provider B |
|---|---|---|
| Operation | `t04_inputs/provider_a_operation.bin` | `t04_inputs/provider_b_operation.bin` |
| Issued authority | `authorizations/t04_provider_a.json` | `authorizations/t04_provider_b.json` |

The frozen request construction implementation is:

`frozen_R43/requester.py`

All paths above are relative to the `MH001_R43_RUN001/` root.

Each provider independently issued its own signed authorization package before the requester prepared the HTTP request.

The requester did not mint, sign, or enlarge provider authority.

## 3. Original Request Format

Both T04 requests use:

```http id="06gaev"
POST /ingest HTTP/1.1
Host: requester.invalid
X-MH-Destination: PROVIDER_A
Content-Type: application/json
Content-Length: 847
```

Provider B uses `PROVIDER_B` in the destination header.

Recorded properties:

| Property | Both providers |
|---|---|
| Method | POST |
| Path | `/ingest` |
| Prepared Host | `requester.invalid` |
| Content type | `application/json` |
| Body length | 847 bytes |
| Complete request length | 980 bytes |

The JSON body contains:

- `binding`
- `provider_authorization_b64`
- `request_repr`
- `verification_context`

The `provider_authorization_b64` field contains the already-issued Ed25519 authorization package, encoded as URL-safe Base64 without padding.

The requester observation contains:

`signature_verified_by_adapter: false`

This records the requester's limited role. Provider-signature verification occurs at the provider, not in the requester adapter.

## 4. Provider A — Original T04 Request

### Authorization

Provider ID:

`PROVIDER_A`

Authorization ID:

`295e8d3288b7923daf7c5beaf0cb6433e8dff8eb9b47c6c56bc3822bcb1276ea`

Verification context:

`MH001_R43_RUN001_T04_PROVIDER_A_V1`

### Operation SHA-256

`c65f9a3bfbcdfc3046f8b5c9951da7da2d4a19803f9df15cca50614e2ceafeea`

### Request Binding

`25f846c28dec489b275579c26cad72ad77ea218409bbe0ff4e1e9f0dab9ad98f`

### Issued Authorization Package SHA-256

`2da52f8aa6ce03d926138d4300b9f2addb0caab95f7e8c3285c87ba1ec7d4f39`

### Prepared HTTP Request SHA-256

`d28618c574cc1867aa8cf5d696fcfb97908b6dcda709857d6679bdc7291d1139`

### HTTP Body SHA-256

`c6591697c79a356b8ccf9ccb16da2dca2f379789ecfbf53fa6fbc3a1de605f39`

## 5. Provider B — Original T04 Request

### Authorization

Provider ID:

`PROVIDER_B`

Authorization ID:

`1d5777cc2f3dedba9a88d435b4d764ac749c77d6aea9f76e177d32e0fcea8226`

Verification context:

`MH001_R43_RUN001_T04_PROVIDER_B_V1`

### Operation SHA-256

`3710b6e062a126e0827426a7a682da71cd2c36956dde7ebca807501631616bfd`

### Request Binding

`90771cf9047bb088e0861e84db3f725421ca91d391735c370bcee4c2a34f8158`

### Issued Authorization Package SHA-256

`81a729d885073b2bbce214aa5bbbcf71effe5d8289ff8442db4bf1a132a59fed`

### Prepared HTTP Request SHA-256

`d884a52fb6a4bd5bfc546b2eca6ef24129f0c2dbc2495d345c52e0b4acba7ecb`

### HTTP Body SHA-256

`855a7d10541370bdea080add62a90c9694cc697caa93365cfe920bc112c61ed6`

## 6. Original File Integrity

All six files are recorded in:

`evidence/MH001_FINAL_SHA256SUMS.txt`

### Provider A

| File | SHA-256 |
|---|---|
| `request.http` | `d28618c574cc1867aa8cf5d696fcfb97908b6dcda709857d6679bdc7291d1139` |
| `body.bin` | `c6591697c79a356b8ccf9ccb16da2dca2f379789ecfbf53fa6fbc3a1de605f39` |
| `requester_observation.json` | `7edd2b0e56da0fc9e44f49fcd9b67a3caedf605b726f619e71720b94e9891819` |

### Provider B

| File | SHA-256 |
|---|---|
| `request.http` | `d884a52fb6a4bd5bfc546b2eca6ef24129f0c2dbc2495d345c52e0b4acba7ecb` |
| `body.bin` | `855a7d10541370bdea080add62a90c9694cc697caa93365cfe920bc112c61ed6` |
| `requester_observation.json` | `47933b09d1e0cf0cb18cdc07b53da946590c0ba0ccd3a86e3a2f2bcf0ca53cc8` |

### Verify on Linux

From `t04_requests/`:

```bash id="a9hizb"
sha256sum provider_a/*
sha256sum provider_b/*
```

### Verify on PowerShell

From `t04_requests/`:

```powershell id="sz90jz"
Get-FileHash .\provider_a\* -Algorithm SHA256
Get-FileHash .\provider_b\* -Algorithm SHA256
```

All six calculated hashes must match the original manifest.

## 7. Reconstruct the Original Requests Offline

The published T04 requests can be reconstructed using the original operation files, issued authorization packages, and frozen requester implementation.

This does not require private signing keys.

**These commands create files only. They do not transmit HTTP requests or execute provider operations.**

From the scored-run root on Linux, create a separate reconstruction directory:

```bash id="r12exz"
mkdir -p ../MH001_T04_RECONSTRUCTED
```

### Provider A

```bash id="4mnie0"
python3 -B frozen_R43/requester.py prepare \
  --operation t04_inputs/provider_a_operation.bin \
  --issued authorizations/t04_provider_a.json \
  --context MH001_R43_RUN001_T04_PROVIDER_A_V1 \
  --destination PROVIDER_A \
  --output ../MH001_T04_RECONSTRUCTED/provider_a
```

### Provider B

```bash id="f9s1gw"
python3 -B frozen_R43/requester.py prepare \
  --operation t04_inputs/provider_b_operation.bin \
  --issued authorizations/t04_provider_b.json \
  --context MH001_R43_RUN001_T04_PROVIDER_B_V1 \
  --destination PROVIDER_B \
  --output ../MH001_T04_RECONSTRUCTED/provider_b
```

The output directories must not already exist.

The requester deliberately refuses to overwrite an existing preparation directory.

### Compare the Original Bytes

From the scored-run root:

```bash id="7w48vu"
cmp t04_requests/provider_a/request.http ../MH001_T04_RECONSTRUCTED/provider_a/request.http
cmp t04_requests/provider_a/body.bin ../MH001_T04_RECONSTRUCTED/provider_a/body.bin

cmp t04_requests/provider_b/request.http ../MH001_T04_RECONSTRUCTED/provider_b/request.http
cmp t04_requests/provider_b/body.bin ../MH001_T04_RECONSTRUCTED/provider_b/body.bin
```

Each comparison should report no difference.

The generated `requester_observation.json` files should contain the same logical values as the originals.

The original observations use Windows-style CRLF line endings. Linux-generated observations may have different file hashes because of newline encoding.

Do not alter the historical observation files to match reconstructed formatting.

## 8. T04 Compared with T01

T04 did not reuse the T01 authorizations.

The requests were distinct at both provider boundaries.

| Provider | T01 request SHA-256 | T04 request SHA-256 |
|---|---|---|
| A | `bf748793a91e35f53e5f2137d78239021e77036b3e462a639369cc3403cf0c33` | `d28618c574cc1867aa8cf5d696fcfb97908b6dcda709857d6679bdc7291d1139` |
| B | `ddcec53dad222c60b134a8cb0145f18b241d6c7177febd2cd7925600591dbf84` | `d884a52fb6a4bd5bfc546b2eca6ef24129f0c2dbc2495d345c52e0b4acba7ecb` |

The original T01 authorizations remained spent following T03.

T04 used different operations, verification contexts, nonces, authorization IDs, and signed packages.

This distinguishes fresh authority from a retried or modified spent authorization.

## 9. T04 Forwarding Route

Both T04 requests were submitted directly to Hub B.

```text id="51p85f"
           Requester
               |
               v
             Hub B
            /     \
           v       v
     Provider A  Provider B
```

Hub A had been terminated during T02.

The T04 forwarding route did not depend on Hub A.

The hub forwarding records and provider-ingress captures document the paths used.

### Expected Host Rewrite

The prepared requests contain:

`Host: requester.invalid`

The frozen hubs rewrite that transport header to the destination endpoint.

At Provider A:

`Host: 192.168.1.118:18090`

At Provider B:

`Host: 192.168.1.107:18091`

A comparison against provider-ingress captures must account for this expected Host rewrite.

It must not permit changes to the authorization-bearing request body or other preserved fields.

## 10. Verify the T04 Outcome

The request files establish the exact authorization-bearing data submitted.

They do not, by themselves, prove execution.

For the complete T04 result, correlate:

| Evidence | Location |
|---|---|
| Requester transport receipts | `evidence/requester/` |
| Provider-ingress captures | `evidence/ingress/` |
| Hub forwarding observations | `evidence/final_remote/` |
| Provider consumption and execution records | `evidence/final_remote/provider_a/` and `provider_b/` |
| Independently signed events | `evidence/observer.jsonl` |

All paths are relative to the scored-run root.

### Expected Provider Results

For each provider:

1. The original T01 authorization remains spent.
2. The T03 replay adds no execution or consumption.
3. The new T04 request arrives through Hub B.
4. The provider validates its new authorization.
5. The independent observer receives signed START and COMPLETE events.
6. The provider records exactly one new consumption.
7. The provider records exactly one new software execution.
8. The final consumption ledger reaches sequence 3.

The historical observer records are:

| Provider | START | COMPLETE |
|---|---:|---:|
| Provider A | 12 | 13 |
| Provider B | 14 | 15 |

These are observer record sequence numbers.

The final provider ledger sequence is 3 for both providers because each recorded rehearsal, T01, and T04 consumption.

## 11. New Independent Reproduction

For a separately authorized reproduction:

1. Preserve the provider histories established by T01.
2. Complete T03 using the exact original T01 requests.
3. Verify both signed `DENY / auth_spent` outcomes.
4. Do not reset either provider's consumption state.
5. Prepare distinct T04 operations.
6. Have each provider issue new authority.
7. Construct new HTTP requests using the frozen requester.
8. Preserve the new request files and calculate their hashes.
9. Submit each request once through Hub B.
10. Independently verify provider-ingress bytes, signed outcomes, consumption, and execution.
11. Confirm the prior T01 authorizations remain spent.

A new reproduction will ordinarily have different authorization IDs, nonces, signatures, and request hashes.

The test requirement is the preservation of provider-controlled single-use authority across the route change, not reproduction of the historical random values.

## 12. Preservation Boundary

All six original T04 request files belong to the 132-file scored evidence inventory.

This README is supplemental documentation.

Do not replace the original request files with reconstructed versions.

Do not normalize original JSON, HTTP headers, or line endings.

Do not regenerate historical authorization packages or reset provider state.

Use a separate workspace and evidence manifest for any new test.

## Conclusion

T04 demonstrated that both providers could accept newly issued authority through Hub B while retaining the spent state of their earlier T01 authorizations.

**The alternate route remained available for valid new requests but did not restore previously consumed authority.**
