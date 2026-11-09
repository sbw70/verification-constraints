
# MH001 — Rehearsal Request Artifacts

## Purpose

This directory preserves the original provider-bound HTTP requests prepared for the MH001 R4.3 rehearsal.

The rehearsal preceded the scored T01–T04 sequence and exercised the initial asymmetric hub routes.

Each request was constructed from:

1. Provider-specific operation bytes.
2. A provider-issued Ed25519 authorization package.
3. The original verification context.
4. The intended provider destination.

The requester assembled these materials but did not generate or sign authorization.

**Session:** `MH001_R43_RUN001`

**Phase:** Rehearsal

## 1. Directory Contents

```text
rehearsal_requests/
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
| `body.bin` | Exact authorization-bearing HTTP body |
| `request.http` | Complete prepared HTTP request, including headers and body |
| `requester_observation.json` | Original input, request, binding, and package hash identities |

These six files belong to the original scored-run inventory.

## 2. Source Materials

The original operation bytes are located at the scored-run root:

- `rehearsal_inputs/provider_a_operation.bin`
- `rehearsal_inputs/provider_b_operation.bin`

The corresponding provider-issued authorization packages are:

- `authorizations/rehearsal_provider_a.json`
- `authorizations/rehearsal_provider_b.json`

The request construction implementation is:

`frozen_R43/requester.py`

All paths above are relative to `MH001_R43_RUN001/`.

### Verification Contexts

Provider A:

`MH001_R43_RUN001_REHEARSAL_PROVIDER_A_V1`

Provider B:

`MH001_R43_RUN001_REHEARSAL_PROVIDER_B_V1`

The provider authorization's recorded context and the request body's context must agree.

Do not substitute one provider's operation, package, or context for the other's.

## 3. HTTP Request Format

Both prepared requests use:

`POST /ingest HTTP/1.1`

Their original headers include:

```http
Host: requester.invalid
X-MH-Destination: PROVIDER_A
Content-Type: application/json
Content-Length: 861
```

Provider B uses `PROVIDER_B` in the destination header.

The original body length is 861 bytes for each provider.

The `Host: requester.invalid` value is a preparation placeholder. The frozen hub transport replaces Host with the next-hop endpoint during forwarding.

This expected Host rewrite does not authorize changes to the provider-bound authorization body.

### Body Fields

The JSON request body includes:

- `binding`
- `provider_authorization_b64`
- `request_repr`
- `verification_context`

`provider_authorization_b64` contains the already-issued provider authorization package encoded using URL-safe Base64 without padding.

The requester does not create or independently verify that signature.

## 4. Request Binding

The requester computes:

`request_repr = SHA256(operation_bytes)`

Then computes:

`binding = SHA256(UTF8("NUVL_BIND_V1|" + request_repr + "|" + verification_context))`

The frozen implementation uses lowercase hexadecimal SHA-256 digests.

### Provider A

Operation SHA-256:

`48bf46f47e6f2961da909f580df905a3d03efe961264579e24a701020d0c760f`

Binding:

`d22c8ed6ff5dd6553608fe1b1ded8794f1b631224c9858560474c8c9a380926f`

### Provider B

Operation SHA-256:

`11904939c7b710e7bb1caa63ecdee71f2f01e15c372e8352f08d596ab4a0fa9b`

Binding:

`c7db4b64a96d3996bff03e987bcfbccb4a9f910e44e448514b6e85167613220e`

These values appear in the corresponding original requester observations.

## 5. Original SHA-256 Values

The following file hashes are recorded in:

`evidence/MH001_FINAL_SHA256SUMS.txt`

### Provider A

| File | SHA-256 |
|---|---|
| `body.bin` | `7542baa24b67649bd6ee99513943267d9a6c8ba3170418b5dba56ff209e77b2c` |
| `request.http` | `ef0128796ea78425c0a2cba99870027e389305326d5db4649e69d152b213134e` |
| `requester_observation.json` | `57e252d9b6440ce6ff1bb832e8a719e0189eb1d559704de2f8db038dd7169f48` |

Original issued-package SHA-256:

`56b51ed287d598840f300d09057328b03dea3011dc24fceccd4de65d5c9af5ee`

### Provider B

| File | SHA-256 |
|---|---|
| `body.bin` | `6b25e82ceb564d7b62ec238e2df5072beeeec89022b141d031cfc54e01fe7dc7` |
| `request.http` | `70bc8c11d4d8cebf4df5ee5cf9dc19d7f2cd36c52c711b45b626e59f0fa91d29` |
| `requester_observation.json` | `2d97aaaed59f30d56ff903cb9678e2f57a428ea85356a539e6f5e35f2be71ac2` |

Original issued-package SHA-256:

`41bedc437c6a09830bd0313bde539f6dac0206385185e5052de8b2b1151d83ec`

The issued-package hashes identify the original authorization JSON bytes, not the entire HTTP request.

## 6. Reconstruct the Original Requests

The published authorization packages can be used to reconstruct the prepared requests without using any private signing keys.

**This is offline reconstruction, not new authorization issuance or live execution.**

Start from `MH001_R43_RUN001/`.

Create a separate sibling output directory, outside the original scored-run root.

```bash
mkdir ../MH001_REHEARSAL_RECONSTRUCTED
```

### Provider A

```bash
python -B frozen_R43/requester.py prepare \
  --operation rehearsal_inputs/provider_a_operation.bin \
  --issued authorizations/rehearsal_provider_a.json \
  --context MH001_R43_RUN001_REHEARSAL_PROVIDER_A_V1 \
  --destination PROVIDER_A \
  --output ../MH001_REHEARSAL_RECONSTRUCTED/provider_a
```

### Provider B

```bash
python -B frozen_R43/requester.py prepare \
  --operation rehearsal_inputs/provider_b_operation.bin \
  --issued authorizations/rehearsal_provider_b.json \
  --context MH001_R43_RUN001_REHEARSAL_PROVIDER_B_V1 \
  --destination PROVIDER_B \
  --output ../MH001_REHEARSAL_RECONSTRUCTED/provider_b
```

Use the appropriate Python 3 interpreter on the reproduction machine.

The output provider directories must not already exist. The requester deliberately refuses to reuse an existing output directory.

Do not point the output argument at the original `rehearsal_requests/` directories.

### Expected Reconstruction

For each provider, compare the newly generated:

- `request.http`
- `body.bin`
- `requester_observation.json`

against the historical equivalents.

The original `request.http` and `body.bin` bytes should reproduce exactly when the published input bytes, package bytes, context, and frozen requester implementation are unchanged.

The generated observation JSON should contain matching logical values.

Its complete file hash can differ across operating systems because of newline encoding. The published original observations use Windows-style CRLF line endings.

A newline-format difference in an observation file is not permission to alter an original scored artifact.

## 7. Verify the Reconstructed Requests

On Linux, from the scored-run root:

```bash
sha256sum ../MH001_REHEARSAL_RECONSTRUCTED/provider_a/request.http
sha256sum ../MH001_REHEARSAL_RECONSTRUCTED/provider_a/body.bin
sha256sum ../MH001_REHEARSAL_RECONSTRUCTED/provider_b/request.http
sha256sum ../MH001_REHEARSAL_RECONSTRUCTED/provider_b/body.bin
```

Compare these four digests with Section 5.

For an additional byte-for-byte comparison:

```bash
cmp rehearsal_requests/provider_a/request.http ../MH001_REHEARSAL_RECONSTRUCTED/provider_a/request.http
cmp rehearsal_requests/provider_a/body.bin ../MH001_REHEARSAL_RECONSTRUCTED/provider_a/body.bin

cmp rehearsal_requests/provider_b/request.http ../MH001_REHEARSAL_RECONSTRUCTED/provider_b/request.http
cmp rehearsal_requests/provider_b/body.bin ../MH001_REHEARSAL_RECONSTRUCTED/provider_b/body.bin
```

Each `cmp` command should exit successfully without reporting a difference.

These commands operate on preserved historical files and separate reconstruction outputs. They do not transmit requests to any hub or provider.

## 8. Original Rehearsal Routing

Both requests were submitted to Hub A.

Provider A:

```text
Requester → Hub A → Provider A
```

Provider B:

```text
Requester → Hub A → Hub B → Provider B
```

The asymmetric routing deliberately exercised both direct and chained forwarding.

The original transmission receipts are preserved under:

`evidence/requester/`

Provider-ingress captures are preserved under:

`evidence/ingress/`

Hub forwarding logs and provider final state are preserved under:

`evidence/final_remote/`

These paths are relative to the scored-run root.

### Historical Rehearsal Outcome

Both providers accepted their respective valid rehearsal authorizations, recorded consumption, and executed once.

The independent observer recorded signed START and COMPLETE events for each provider.

The rehearsal authorizations were subsequently spent.

## 9. New Live Reproduction

The published authorization packages are historical, already-consumed test artifacts.

They are suitable for offline reconstruction and examination, not as fresh trusted authority for another live experiment.

For a new independent rehearsal:

1. Establish fresh, isolated provider-controlled persistent state.
2. Establish approved provider signing identities.
3. Prepare provider-specific operation inputs.
4. Have each provider issue authorization for its own operation and verification context.
5. Transfer only the issued package and permitted request materials to the requester.
6. Use the frozen requester to construct each new provider-bound HTTP request.
7. Preserve the prepared request bytes before transmission.
8. Submit each request once through the approved initial route.
9. Independently verify provider-signed decisions and consumption history.
10. Preserve the new evidence separately.

The requester and hubs must not acquire provider private signing authority.

A new issuance normally produces different nonces, authorization IDs, and signatures.

Those differences do not invalidate a behavioral reproduction.

## 10. Preservation Boundary

The six original files in this directory are part of the 132-file scored evidence inventory.

This README is supplemental documentation.

Do not alter the original files to match a reconstructed version.

Do not rewrite original JSON formatting or line endings.

Do not regenerate historical authorization packages.

Do not submit already-spent historical requests to an operational provider.

**Reproduction objective:** Reconstruct the original provider-bound rehearsal request bytes using the published operation inputs, provider-issued packages, and frozen requester implementation, then independently verify the recorded rehearsal outcomes.
