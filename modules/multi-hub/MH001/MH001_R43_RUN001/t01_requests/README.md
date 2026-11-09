
# MH001 — T01 Original Request Artifacts

## Purpose

This directory preserves the original provider-bound HTTP requests submitted during T01 of the MH001 R4.3 scored experiment.

T01 established that two independent providers could accept and consume their respective single-use authorizations through the initial hub topology.

These exact requests were subsequently reused during T03, after Hub A was terminated.

**Session:** `MH001_R43_RUN001`

**Test:** T01 — Initial Authority Consumption

**Recorded result:** Both providers accepted and executed once.

The original request bytes are central to verifying that the T03 replay did not contain newly issued, altered, or repaired authorization.

## 1. Directory Contents

```text
t01_requests/
├── provider_a/
│   ├── body.bin
│   ├── request.http
│   └── requester_observation.json
└── provider_b/
    ├── body.bin
    ├── request.http
    └── requester_observation.json
```

Each provider has three preserved artifacts.

| File | Description |
|---|---|
| `body.bin` | Original authorization-bearing HTTP body |
| `request.http` | Complete prepared HTTP request |
| `requester_observation.json` | Original request hashes, binding, and source identities |

These are historical scored-run artifacts.

They must not be overwritten by reconstructed or newly generated files.

## 2. Original Source Materials

The corresponding operation inputs are:

- `t01_inputs/provider_a_operation.bin`
- `t01_inputs/provider_b_operation.bin`

The independently issued authorization packages are:

- `authorizations/t01_provider_a.json`
- `authorizations/t01_provider_b.json`

The frozen requester implementation is:

`frozen_R43/requester.py`

All paths above are relative to `MH001_R43_RUN001/`.

The requester constructed each HTTP request using the original operation, an already-issued authorization package, the specified verification context, and the intended provider destination.

The requester did not issue or sign authority.

## 3. Original HTTP Request Format

Both requests use:

`POST /ingest HTTP/1.1`

Provider A's prepared request begins:

```http
POST /ingest HTTP/1.1
Host: requester.invalid
X-MH-Destination: PROVIDER_A
Content-Type: application/json
Content-Length: 847
```

Provider B uses:

`X-MH-Destination: PROVIDER_B`

For each provider:

| Property | Recorded value |
|---|---|
| HTTP method | POST |
| Request target | `/ingest` |
| Prepared Host | `requester.invalid` |
| Content type | `application/json` |
| Body length | 847 bytes |
| Complete prepared request length | 980 bytes |

The HTTP request body contains:

- `binding`
- `provider_authorization_b64`
- `request_repr`
- `verification_context`

The body contains the already-issued Ed25519 authorization package encoded as URL-safe Base64 without padding.

The requester's observation records:

`signature_verified_by_adapter: false`

This is intentional. Signature validation remains the provider's responsibility.

## 4. Provider A — Original Request

### Authorization Identity

Provider:

`PROVIDER_A`

Authorization ID:

`a92b2daf4e88cbb066ef5ce47431b8ca09144055d3b8e60c3a1c185303f1c3ea`

Verification context:

`MH001_R43_RUN001_T01_PROVIDER_A_V1`

### Operation Hash

`db80f33bae15954673e98d341940e2eea32381200ccb0c0f1f8c0782339413a0`

### Binding

`057804df4a7471b5053ea033a34ce317ae72d6ddf7d3829fcb855ba71ae9d3e2`

### Issued Authorization Package SHA-256

`cc19d4bf04579a2038af9fac9dadc581525903e89c52cce0c33`

Correction: use the complete package hash below when verifying:

`cc19d4bf04579a2038af9fac9dadc581525903e89c52cce0c7bb32e61960e272`

### Original Request SHA-256

`bf748793a91e35f53e5f2137d78239021e77036b3e462a639369cc3403cf0c33`

### Original Body SHA-256

`83071f65a756aeb0c02206de5e331a564516818c1081a58905076de260afc99c`

## 5. Provider B — Original Request

### Authorization Identity

Provider:

`PROVIDER_B`

Authorization ID:

`041315d147341d225acd07d925abcae408864bb52def806709b6b9def5e52b4a`

Verification context:

`MH001_R43_RUN001_T01_PROVIDER_B_V1`

### Operation Hash

`2f3a4db161a9221d0105352ba3c66a738948681f5adc7f98e77daca84f219d6a`

### Binding

`d7204aa416591cbb951c75fcf3760bfba5393ee4ded483e5f22e3e733ca4ef72`

### Issued Authorization Package SHA-256

`6133239a3c2b997cf29dc531c0672a582fdca0b5aae0fa8e51984fa04adc853a`

### Original Request SHA-256

`ddcec53dad222c60b134a8cb0145f18b241d6c7177febd2cd7925600591dbf84`

### Original Body SHA-256

`578455981c69b3955dad7c6a7cb15409fafc117d2dcc85dc34cb432f6d3fe1f0`

## 6. Original File Integrity

All six original files appear in the final scored-run SHA-256 manifest.

### Provider A

| File | SHA-256 |
|---|---|
| `body.bin` | `83071f65a756aeb0c02206de5e331a564516818c1081a58905076de260afc99c` |
| `request.http` | `bf748793a91e35f53e5f2137d78239021e77036b3e462a639369cc3403cf0c33` |
| `requester_observation.json` | `b4f9df3bd534f0742b23544727ddfd4bd83a516c25538d26cabd992c456ca860` |

### Provider B

| File | SHA-256 |
|---|---|
| `body.bin` | `578455981c69b3955dad7c6a7cb15409fafc117d2dcc85dc34cb432f6d3fe1f0` |
| `request.http` | `ddcec53dad222c60b134a8cb0145f18b241d6c7177febd2cd7925600591dbf84` |
| `requester_observation.json` | `f6238597839ac721123b0f1b929325afdc512b680d753dd71973ff39f84699e7` |

The complete manifest is located at:

`evidence/MH001_FINAL_SHA256SUMS.txt`

That path is relative to the scored-run root.

### Verify on Linux

From `t01_requests/`:

```bash
sha256sum provider_a/*
sha256sum provider_b/*
```

### Verify on PowerShell

From `t01_requests/`:

```powershell
Get-FileHash .\provider_a\* -Algorithm SHA256
Get-FileHash .\provider_b\* -Algorithm SHA256
```

The original files must match the published hashes.

## 7. Reconstruct the Original Requests Offline

The original prepared HTTP requests can be reconstructed without access to a provider's private signing key.

The published signed authorization packages are already available.

This procedure performs no network transmission.

From the scored-run root, create a separate reconstruction directory:

```bash
mkdir -p ../MH001_T01_RECONSTRUCTED
```

### Provider A

```bash
python3 -B frozen_R43/requester.py prepare \
  --operation t01_inputs/provider_a_operation.bin \
  --issued authorizations/t01_provider_a.json \
  --context MH001_R43_RUN001_T01_PROVIDER_A_V1 \
  --destination PROVIDER_A \
  --output ../MH001_T01_RECONSTRUCTED/provider_a
```

### Provider B

```bash
python3 -B frozen_R43/requester.py prepare \
  --operation t01_inputs/provider_b_operation.bin \
  --issued authorizations/t01_provider_b.json \
  --context MH001_R43_RUN001_T01_PROVIDER_B_V1 \
  --destination PROVIDER_B \
  --output ../MH001_T01_RECONSTRUCTED/provider_b
```

The output provider directories must not already exist.

Do not direct reconstructed output into the original `t01_requests/` directories.

### Compare Original and Reconstructed Bytes

From the scored-run root:

```bash
cmp t01_requests/provider_a/request.http ../MH001_T01_RECONSTRUCTED/provider_a/request.http
cmp t01_requests/provider_a/body.bin ../MH001_T01_RECONSTRUCTED/provider_a/body.bin

cmp t01_requests/provider_b/request.http ../MH001_T01_RECONSTRUCTED/provider_b/request.http
cmp t01_requests/provider_b/body.bin ../MH001_T01_RECONSTRUCTED/provider_b/body.bin
```

All four comparisons should complete without reporting differences.

The original `requester_observation.json` files use Windows-style CRLF line endings.

A reconstruction performed on Linux can produce logically identical JSON with different line endings.

Compare the observation fields semantically if file hashes differ for that reason.

Do not normalize or edit the historical originals.

## 8. Original T01 Routing

The initial routes were deliberately asymmetric.

### Provider A

```text
Requester → Hub A → Provider A
```

### Provider B

```text
Requester → Hub A → Hub B → Provider B
```

Hub A was the requester's first hop for both providers.

Provider A received its request directly from Hub A.

Provider B received its request after two hub forwarding stages.

Each provider independently validated its own authorization and consumed it once.

The accepted T01 events are preserved in the independent observer evidence.

## 9. T03 — Exact Replay Relationship

T03 deliberately reused the original T01 requests.

There is no separate `t03_requests/` directory containing newly prepared authorizations.

Instead, the requester sent the exact original T01 `request.http` bytes through Hub B.

### Provider A

T01 requester packet SHA-256:

`bf748793a91e35f53e5f2137d78239021e77036b3e462a639369cc3403cf0c33`

T03 requester packet SHA-256:

`bf748793a91e35f53e5f2137d78239021e77036b3e462a639369cc3403cf0c33`

### Provider B

T01 requester packet SHA-256:

`ddcec53dad222c60b134a8cb0145f18b241d6c7177febd2cd7925600591dbf84`

T03 requester packet SHA-256:

`ddcec53dad222c60b134a8cb0145f18b241d6c7177febd2cd7925600591dbf84`

The exact matches are recorded in the respective T01 and T03 requester receipts.

### Alternate Routing

```text
Requester → Hub B → Provider A
                  → Provider B
```

The original authorizations, nonces, operations, verification contexts, bindings, and request bodies were not changed.

Both providers returned signed:

`DENY / auth_spent`

Neither recorded an additional execution or consumption.

## 10. Provider-Ingress Byte Comparison

The prepared request contains:

`Host: requester.invalid`

The forwarding hubs rewrite the HTTP Host field to the next-hop endpoint.

Therefore, the prepared HTTP file is not expected to be byte-identical to the request captured at provider ingress.

The expected provider-ingress Host fields were:

Provider A:

`Host: 192.168.1.118:18090`

Provider B:

`Host: 192.168.1.107:18091`

The original post-run comparison accounted for this expected transport-header change.

No changes to the authorization-bearing body or other preserved request fields were permitted.

The provider-ingress captures confirmed that T01 and T03 were byte-identical **at each provider boundary**.

The captures are preserved at:

`evidence/ingress/`

The packet-capture README documents the independent byte comparison.

## 11. Independent Outcome Correlation

The following records must be examined together.

| Artifact | Verification responsibility |
|---|---|
| `t01_requests/` | Original prepared request bytes |
| `evidence/requester/` | T01 and T03 transmission hashes and first-hop destinations |
| `evidence/ingress/` | Actual provider-ingress request bytes |
| `evidence/final_remote/` | Hub forwarding and persistent provider state |
| `evidence/observer.jsonl` | Independently signed provider decisions |

All paths above are relative to the scored-run root.

The requester and hubs are not authoritative evidence of provider execution.

The signed provider events and persistent-state records establish the corresponding authorization outcomes.

The critical correlation is:

1. T01 request accepted.
2. T01 authorization consumed.
3. Hub A terminated.
4. Original T01 request replayed through Hub B.
5. Same request bytes observed at provider ingress.
6. Provider returned signed `DENY / auth_spent`.
7. No additional consumption or execution occurred.

## 12. Reproduction Requirements

For a new, separately approved live experiment:

1. Establish independent provider-controlled signing identities and persistent state.
2. Prepare provider-specific T01 operation inputs.
3. Have each provider issue valid single-use authority.
4. Use the frozen requester implementation to prepare the HTTP requests.
5. Save exact copies of both `request.http` files.
6. Verify and record their SHA-256 values.
7. Submit the original T01 requests once through Hub A.
8. Independently verify signed execution and persistent consumption.
9. Preserve the exact original request files without alteration.
10. Obtain operator approval and terminate the designated Hub A process.
11. Verify the altered forwarding topology.
12. Replay the same original HTTP bytes directly through Hub B.
13. Confirm byte-identical T01/T03 requests at provider ingress.
14. Verify independent signed `DENY / auth_spent` decisions.
15. Confirm neither provider executed or consumed authority again.

Newly issued authorizations will normally produce different cryptographic identifiers.

The relevant reproduction requirement is that each experiment preserves its own original T01 request bytes for exact replay.

The historical T01 authorizations are already spent and are not fresh trusted authority.

## 13. Preservation Boundary

The six original files in this directory belong to the 132-file scored evidence inventory.

This README is supplemental documentation.

Do not modify the historical HTTP requests, bodies, or requester observations.

Do not regenerate the original authorization packages.

Do not change the original T01 request bytes to accommodate T03.

Do not reset provider consumption state.

**Reproduction objective:** Demonstrate that the same previously consumed authorization cannot execute again merely because the requester changes the forwarding route.
