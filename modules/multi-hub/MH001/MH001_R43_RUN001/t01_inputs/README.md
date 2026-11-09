
# MH001 — T01 Original Operation Inputs

## Purpose

This directory preserves the original provider-specific operation bytes used in T01 of the MH001 R4.3 scored experiment.

T01 established the initial authorized executions before Hub A was terminated and the requests were replayed through Hub B during T03.

Each provider independently issued single-use authority for its own operation.

**Session:** `MH001_R43_RUN001`

**Test:** T01 — Initial Authority Consumption

**Recorded result:** Both providers accepted their valid authorizations and executed once.

## 1. Directory Contents

```text
t01_inputs/
├── provider_a_operation.bin
└── provider_b_operation.bin
```

These files contain operation bytes only.

They are not complete HTTP requests, authorization packages, or signing keys.

## 2. Original Operation Bytes

### Provider A

File:

`provider_a_operation.bin`

Exact contents:

```text
MH001_R43_RUN001|T01|PROVIDER_A|V1
```

SHA-256:

`db80f33bae15954673e98d341940e2eea32381200ccb0c0f1f8c0782339413a0`

Verification context:

`MH001_R43_RUN001_T01_PROVIDER_A_V1`

Original authorization ID:

`a92b2daf4e88cbb066ef5ce47431b8ca09144055d3b8e60c3a1c185303f1c3ea`

### Provider B

File:

`provider_b_operation.bin`

Exact contents:

```text
MH001_R43_RUN001|T01|PROVIDER_B|V1
```

SHA-256:

`2f3a4db161a9221d0105352ba3c66a738948681f5adc7f98e77daca84f219d6a`

Verification context:

`MH001_R43_RUN001_T01_PROVIDER_B_V1`

Original authorization ID:

`041315d147341d225acd07d925abcae408864bb52def806709b6b9def5e52b4a`

The original files contain no trailing newline.

Do not insert additional characters or alter their encoding when reproducing the exact input bytes.

## 3. Relationship to Provider Authorization

The provider-controlled issuance process calculates:

`request_repr = SHA256(operation_bytes)`

The resulting operation hash is incorporated into the provider-issued authorization package.

Each authorization is bound to:

- The issuing provider.
- The operation representation.
- The verification context.
- A generated nonce.
- The resulting authorization identity.

The authorization is signed using that provider's Ed25519 issuance key.

The requester does not generate the signature.

### Original Issued Packages

Provider A:

`authorizations/t01_provider_a.json`

Package SHA-256:

`cc19d4bf04579a2038af9fac9dadc581525903e89c52cce0c7bb32e61960e272`

Provider B:

`authorizations/t01_provider_b.json`

Package SHA-256:

`6133239a3c2b997cf29dc531c0672a582fdca0b5aae0fa8e51984fa04adc853a`

Paths are relative to the MH001 scored-run root.

## 4. Original Request Construction

The requester combined each provider's issued package, original operation hash, and verification context into a provider-bound request.

The resulting original artifacts are preserved in:

- `t01_requests/provider_a/`
- `t01_requests/provider_b/`

Each directory contains:

- `request.http`
- `body.bin`
- `requester_observation.json`

The requester's binding calculation is:

`binding = SHA256(UTF8("NUVL_BIND_V1|" + request_repr + "|" + verification_context))`

### Provider A Binding

`057804df4a7471b5053ea033a34ce317ae72d6ddf7d3829fcb855ba71ae9d3e2`

### Provider B Binding

`d7204aa416591cbb951c75fcf3760bfba5393ee4ded483e5f22e3e733ca4ef72`

These bindings connect the original operation representations and contexts to their prepared requests.

## 5. Verify Original File Integrity

Both files are included in the original 132-file scored evidence manifest.

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

Expected values are listed in Section 2.

These commands do not modify either file.

## 6. Reconstruct Original Input Bytes

For independent offline verification, recreate the original bytes in a separate directory.

From the `MH001_R43_RUN001` root on Linux:

```bash
mkdir -p ../MH001_T01_INPUT_RECONSTRUCTED

printf '%s' 'MH001_R43_RUN001|T01|PROVIDER_A|V1' > ../MH001_T01_INPUT_RECONSTRUCTED/provider_a_operation.bin

printf '%s' 'MH001_R43_RUN001|T01|PROVIDER_B|V1' > ../MH001_T01_INPUT_RECONSTRUCTED/provider_b_operation.bin
```

Verify their hashes:

```bash
sha256sum ../MH001_T01_INPUT_RECONSTRUCTED/*.bin
```

The resulting hashes should match the original values in Section 2.

Do not write reconstructed files over the original scored inputs.

The reconstructed operation bytes alone do not reproduce the historical signatures. Those signatures also depend on the original provider-issued authorization contents and signing identities.

## 7. T01 and T03 Relationship

T01 used the following original routes.

Provider A:

```text
Requester → Hub A → Provider A
```

Provider B:

```text
Requester → Hub A → Hub B → Provider B
```

Both providers consumed their respective T01 authorizations.

During T03, the original T01 HTTP requests were replayed through Hub B.

No new T03 operation input was created.

No replacement authorization was issued for T03.

The original T01 request bytes and their authorization identities were preserved.

Both providers rejected the replay with signed:

`DENY / auth_spent`

This behavior is evaluated using the request artifacts, provider-ingress captures, independently signed observer events, and persistent consumption records.

This directory alone does not establish the T03 outcome.

## 8. Independent Reproduction

For a new MH001 experiment:

1. Establish isolated provider-controlled signing identities and persistent state.
2. Prepare distinct operation bytes for Provider A and Provider B.
3. Record the SHA-256 of each operation.
4. Have each corresponding provider issue its own single-use authorization.
5. Construct the T01 requests using the frozen requester implementation.
6. Preserve the exact prepared request bytes before transmission.
7. Submit each original T01 request once through the reviewed initial route.
8. Independently verify the provider's signed execution events and recorded consumption.
9. Preserve the T01 requests for exact replay during T03.

A newly issued authorization will normally have a different nonce, authorization ID, and signature.

The new experiment must reproduce the authority-consumption and replay behavior, not necessarily the original generated cryptographic identifiers.

Do not use publicly disclosed historical test signing keys as trusted operational credentials.

## 9. Preservation Boundary

The original two `.bin` files belong to the MH001 132-file scored inventory.

This README is supplemental documentation.

Do not modify the original operation bytes or their historical hashes.

Do not regenerate the original T01 authorizations.

Do not modify the T01 request materials to make T03 replay succeed.

**Reproduction objective:** Preserve the relationship between each provider's original operation bytes, independently issued authority, and the exact request later replayed through an alternate hub.
