
# MH001 — T04 Fresh Operation Inputs

## Purpose

This directory preserves the original provider-specific operation bytes used during T04 of the MH001 R4.3 scored experiment.

T04 tested whether both providers could still execute newly authorized operations after rejecting the replayed T01 authorizations during T03.

The experiment distinguished between:

- Previously consumed authority, which must remain spent.
- Separately issued fresh authority, which may execute once.

**Session:** `MH001_R43_RUN001`

**Test:** T04 — Fresh Authority Through Hub B

**Recorded result:** Both providers executed once using new authorizations.

## 1. Directory Contents

```text
t04_inputs/
├── provider_a_operation.bin
└── provider_b_operation.bin
```

Each file contains the original operation bytes submitted for authorization issuance.

These files do not contain private keys, signatures, or complete HTTP requests.

## 2. Original Operation Bytes

### Provider A

File:

`provider_a_operation.bin`

Exact contents:

```text
MH001_R43_RUN001|T04|PROVIDER_A|V1
```

SHA-256:

`c65f9a3bfbcdfc3046f8b5c9951da7da2d4a19803f9df15cca50614e2ceafeea`

Verification context:

`MH001_R43_RUN001_T04_PROVIDER_A_V1`

### Provider B

File:

`provider_b_operation.bin`

Exact contents:

```text
MH001_R43_RUN001|T04|PROVIDER_B|V1
```

SHA-256:

`3710b6e062a126e0827426a7a682da71cd2c36956dde7ebca807501631616bfd`

Verification context:

`MH001_R43_RUN001_T04_PROVIDER_B_V1`

Both input files contain exact UTF-8 bytes without trailing newlines.

The provider-specific contents must not be interchanged.

## 3. Original Authorization Issuance

Each provider independently issued new single-use authority for its T04 operation.

The issuance process used:

`request_repr = SHA256(operation_bytes)`

The authorization included the issuing provider identity, operation representation, verification context, generated nonce, and authorization identity.

The provider signed the resulting authorization using its Ed25519 issuance key.

The requester did not generate or sign these authorizations.

### Provider A

Authorization ID:

`295e8d3288b7923daf7c5beaf0cb6433e8dff8eb9b47c6c56bc3822bcb1276ea`

Nonce:

`65e2dfc333b7f9e4e51f719642f99fe8`

Original authorization package:

`authorizations/t04_provider_a.json`

Package SHA-256:

`2da52f8aa6ce03d926138d4300b9f2addb0caab95f7e8c3285c87ba1ec7d4f39`

### Provider B

Authorization ID:

`1d5777cc2f3dedba9a88d435b4d764ac749c77d6aea9f76e177d32e0fcea8226`

Nonce:

`54bf3a27fa2d31205c02bb44f6d7481d`

Original authorization package:

`authorizations/t04_provider_b.json`

Package SHA-256:

`81a729d885073b2bbce214aa5bbbcf71effe5d8289ff8442db4bf1a132a59fed`

Paths above are relative to the scored-run root.

These authorizations are separate from the original T01 authorizations.

## 4. Request Construction

The requester combined each operation representation, verification context, and already-issued provider authorization into a provider-bound HTTP request.

The original prepared requests are preserved in:

- `t04_requests/provider_a/`
- `t04_requests/provider_b/`

Each directory contains:

- `request.http`
- `body.bin`
- `requester_observation.json`

The requester calculated:

`binding = SHA256(UTF8("NUVL_BIND_V1|" + request_repr + "|" + verification_context))`

### Provider A Binding

`25f846c28dec489b275579c26cad72ad77ea218409bbe0ff4e1e9f0dab9ad98f`

### Provider B Binding

`90771cf9047bb088e0861e84db3f725421ca91d391735c370bcee4c2a34f8158`

The original requester implementation is:

`frozen_R43/requester.py`

The requester constructs the request but does not independently verify the provider's signature.

## 5. Verify Original Input Integrity

Both operation files are included in:

`evidence/MH001_FINAL_SHA256SUMS.txt`

The manifest paths are relative to `MH001_R43_RUN001/`.

### Linux

From this directory:

```bash
sha256sum provider_a_operation.bin
sha256sum provider_b_operation.bin
```

### Windows PowerShell

From this directory:

```powershell
Get-FileHash .\provider_a_operation.bin -Algorithm SHA256
Get-FileHash .\provider_b_operation.bin -Algorithm SHA256
```

Expected SHA-256 values are listed in Section 2.

Do not edit or normalize the files before verification.

## 6. Reconstruct Original Operation Inputs

For offline reproduction, create the original operation bytes in a separate workspace.

From the scored-run root on Linux:

```bash
mkdir -p ../MH001_T04_INPUT_RECONSTRUCTED
```

Create Provider A's input:

```bash
printf '%s' 'MH001_R43_RUN001|T04|PROVIDER_A|V1' > ../MH001_T04_INPUT_RECONSTRUCTED/provider_a_operation.bin
```

Create Provider B's input:

```bash
printf '%s' 'MH001_R43_RUN001|T04|PROVIDER_B|V1' > ../MH001_T04_INPUT_RECONSTRUCTED/provider_b_operation.bin
```

Verify the results:

```bash
sha256sum ../MH001_T04_INPUT_RECONSTRUCTED/*.bin
```

The resulting hashes must match Section 2.

These commands create operation inputs only.

They do not mint authorization, contact a hub, or execute provider operations.

A newly issued authorization using these same operation bytes will normally produce a different nonce, authorization ID, and signature.

Do not overwrite the historical files.

## 7. Relationship to T01 and T03

### T01 — Initial Authority

Both providers accepted valid single-use authorizations through the original Hub A routing.

Each provider recorded one execution and consumption.

The T01 authorizations became spent.

### T02 — Hub A Termination

The designated MH001 Hub A forwarding process was terminated.

Hub B and both providers remained available.

### T03 — Replay Denial

The original T01 HTTP requests were sent again through Hub B.

Both providers independently returned signed:

`DENY / auth_spent`

Neither recorded another consumption or execution.

### T04 — Fresh Authority

Both providers received different, newly issued authorizations for their T04 operations.

The T04 requests followed:

```text
Requester
    |
    v
  Hub B
   /   \
  v     v
Provider A   Provider B
```

Each provider independently accepted its new authorization and executed once.

The earlier T01 authorizations remained spent.

## 8. Recorded T04 Outcomes

The final provider consumption ledgers contain:

| Provider | T04 ledger sequence | T04 result |
|---|---|---|
| PROVIDER_A | 3 | Consumed and executed |
| PROVIDER_B | 3 | Consumed and executed |

The independent observer recorded signed START and COMPLETE events for both providers.

The final provider ledgers retained their earlier rehearsal and T01 consumption entries.

T04 did not require resetting or repairing previously consumed authority.

The corresponding evidence is preserved under:

- `evidence/requester/`
- `evidence/ingress/`
- `evidence/final_remote/`
- `evidence/observer.jsonl`

These paths are relative to the scored-run root.

The operation input files alone do not establish the execution outcome.

## 9. Independent Reproduction

For a new, separately authorized MH001 experiment:

1. Complete T01 using valid provider-issued single-use authority.
2. Verify both providers consumed their respective authorizations.
3. Complete the approved Hub A termination.
4. Replay the exact original T01 requests through Hub B.
5. Independently verify signed `DENY / auth_spent` decisions.
6. Preserve the existing provider consumption histories.
7. Prepare distinct fresh T04 operation inputs.
8. Have each provider independently issue a new single-use authorization.
9. Construct new provider-bound requests using the frozen requester.
10. Submit the fresh requests once through Hub B.
11. Verify signed START and COMPLETE events for both providers.
12. Confirm both ledgers advance exactly once for the fresh authorizations.

A reproduction should establish the same authorization behavior, not reproduce randomly generated historical nonces or signatures.

Provider signing authority and persistent state must remain under the corresponding provider's control.

## 10. Preservation Boundary

Both original `.bin` files belong to the 132-file scored evidence inventory.

This README is supplemental documentation.

Do not modify historical input bytes, overwrite original authorizations, or reset provider state to make a replay succeed.

A separate experiment must have its own inputs, signing identities, persistent state, and evidence.

## Conclusion

T04 demonstrated that rejecting previously consumed authority did not prevent either provider from accepting separately issued fresh authority through Hub B.

The providers retained control over both decisions.
