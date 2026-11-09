
# MH001 — Rehearsal Operation Inputs

## Purpose

This directory contains the original operation bytes used during the MH001 R4.3 rehearsal.

These inputs were supplied to the respective providers' authorization issuance processes before constructing the rehearsal HTTP requests.

The rehearsal confirmed that both providers could accept valid, separately issued authority through the intended initial forwarding paths.

**Session:** `MH001_R43_RUN001`

**Phase:** Rehearsal, before T01

## 1. Directory Contents

```text
rehearsal_inputs/
├── provider_a_operation.bin
└── provider_b_operation.bin
```

Each file represents one provider-specific operation.

| File | Provider | Purpose |
|---|---|---|
| `provider_a_operation.bin` | PROVIDER_A | Original rehearsal operation |
| `provider_b_operation.bin` | PROVIDER_B | Original rehearsal operation |

These are operation inputs, not signing keys, authorization packages, or complete HTTP requests.

## 2. Original Operation Bytes

### Provider A

The file contains the exact UTF-8 bytes of:

```text
MH001_R43_RUN001|REHEARSAL|PROVIDER_A|V1
```

SHA-256:

`48bf46f47e6f2961da909f580df905a3d03efe961264579e24a701020d0c760f`

### Provider B

The file contains the exact UTF-8 bytes of:

```text
MH001_R43_RUN001|REHEARSAL|PROVIDER_B|V1
```

SHA-256:

`11904939c7b710e7bb1caa63ecdee71f2f01e15c372e8352f08d596ab4a0fa9b`

The files have different provider identities and therefore different SHA-256 values.

Do not append a newline, insert spaces, or change the encoding when reproducing the original input bytes.

## 3. Verify Original File Integrity

Both files are included in the scored experiment's final 132-file SHA-256 manifest.

From this directory on Linux:

```bash
sha256sum provider_a_operation.bin
sha256sum provider_b_operation.bin
```

On Windows PowerShell:

```powershell
Get-FileHash .\provider_a_operation.bin -Algorithm SHA256
Get-FileHash .\provider_b_operation.bin -Algorithm SHA256
```

Compare the calculated hashes to Section 2.

The files must remain unchanged.

## 4. Relationship to Authorization Issuance

Each provider's issuance process used its operation bytes to calculate:

`request_repr = SHA256(operation_bytes)`

The original rehearsal verification contexts were:

### Provider A

`MH001_R43_RUN001_REHEARSAL_PROVIDER_A_V1`

### Provider B

`MH001_R43_RUN001_REHEARSAL_PROVIDER_B_V1`

The provider-controlled minting implementation then combined the operation hash, verification context, provider identity, and a generated nonce to produce a signed single-use authorization package.

The original issuance tools are preserved at:

- `frozen_R43/providers/provider_a/mint_authorization_a.py`
- `frozen_R43/providers/provider_b/mint_authorization_b.py`

Paths are relative to the scored-run root.

The requester did not create or sign these authorizations.

## 5. Corresponding Published Artifacts

The resulting original signed authorization packages are preserved at:

- `authorizations/rehearsal_provider_a.json`
- `authorizations/rehearsal_provider_b.json`

The complete prepared HTTP request artifacts are preserved at:

- `rehearsal_requests/provider_a/`
- `rehearsal_requests/provider_b/`

The request preparation process embeds the signed authorization package into the provider-bound request body.

The original operation hash is also recorded in each `requester_observation.json`.

These files allow independent comparison of the original operation bytes, issuance package, request binding, and prepared HTTP request.

## 6. Reproducing the Rehearsal Inputs

For an independent reproduction, create new files containing the intended operation bytes.

On Linux, the original bytes can be reconstructed without adding a newline:

```bash
printf '%s' 'MH001_R43_RUN001|REHEARSAL|PROVIDER_A|V1' > provider_a_operation.bin
printf '%s' 'MH001_R43_RUN001|REHEARSAL|PROVIDER_B|V1' > provider_b_operation.bin
```

Run these commands only in a new reproduction workspace, not over the published originals.

Verify the resulting hashes before preparing authorization requests.

A new issuance using fresh keys and a randomly generated nonce will not necessarily reproduce the historical authorization ID or signature.

That difference is expected.

The important requirements are:

1. The operation bytes are preserved.
2. Each provider issues authority for its own operation and context.
3. The requester prepares an HTTP request using already-issued authority.
4. The provider independently validates that authority.
5. Successful execution consumes the authority once.
6. The resulting evidence is preserved separately from the published historical run.

## 7. Rehearsal Routing

The original rehearsal used Hub A as the requester's first hop.

Provider A:

```text
Requester → Hub A → Provider A
```

Provider B:

```text
Requester → Hub A → Hub B → Provider B
```

The rehearsal verified the intended asymmetric forwarding paths before T01.

It was not the alternate-path replay test.

The corresponding requester receipts and provider execution records are preserved elsewhere in the scored evidence.

## 8. Preservation

Both original `.bin` files belong to the 132-file scored evidence inventory.

This README is supplemental documentation.

Do not modify, replace, or regenerate the original input files.

For a new experiment, create separate input files and record their independently calculated hashes.

---

**Rehearsal input requirement:** Provider-specific operation bytes must be bound to provider-issued authority without giving issuance authority to the requester or hubs.
