# MP006-R01 — Original Authorization

## Purpose

This directory preserves the original Provider A authorization and request used in the MP006 physical power-loss experiment.

The same authorization was submitted twice:

1. Before power loss, when it was consumed and executed.
2. After recovery, when replay was expected to be denied.

Preserving the original request and authorization allows the experiment to distinguish replay of existing authority from issuance of new authority.

## Directory Contents

| File | Purpose |
|---|---|
| [request.json](request.json) | Original software-execution request |
| [authorization.json](authorization.json) | Provider A Ed25519-signed authorization package |
| [authorization.json.b64](authorization.json.b64) | Base64url-encoded package used in the authorization header |
| [identity.json](identity.json) | Request, authorization, binding, operation, and package identities |
| [mint_stdout.txt](mint_stdout.txt) | Original authorization-issuance output |
| [mint_stderr.txt](mint_stderr.txt) | Preserved issuance error output; empty in this run |
| [SHA256SUMS.txt](SHA256SUMS.txt) | Original six-file integrity inventory |

## Authorization Generation

The authorization was generated using the frozen MP005 Provider A issuance implementation.

The issuer:

1. Reads the preserved request bytes.
2. Computes their SHA-256 representation.
3. Generates a fresh authorization nonce.
4. Binds the authorization to Provider A, the request representation, and verification context.
5. Calculates the authorization identifier.
6. Signs the authorization using the laboratory Ed25519 issuance key.
7. Preserves the signed package and its encoded header representation.

The MP005 harness independently checks the generated authorization's request binding and identifier before recording `identity.json`.

The published issuance keys are laboratory fixtures, not production credentials.

## Recorded Identity

**Provider:** `PROVIDER_A`

**Session:** `MP006_R01_RUN001`

**Authorization ID:**

`0105b3696211a2f1e536e3b9f07d0c8688e6e05640fd50b1462bb864ece97a0c`

**Verification context:**

`CTX_MP005_MP006_R01_ORIGINAL`

**Request SHA-256:**

`ab09d724f9f66acd606a5120638a22235f76fa24474cbd29d5d6b8bfcfaba0bf`

**Authorization package SHA-256:**

`f459a15ae2d8e0940cc664d6d9d247400abf5de9d57af778d2c0e7f2408ac09a`

The preserved package, identity metadata, issuance output, and integrity inventory agree on the recorded authorization identity.

The request contains `"test":"MP005"` because MP006 reuses the frozen MP005 request-generation harness. Its case and session identifiers identify the MP006 experiment.

## Initial Submission and Replay

The original request and authorization were preserved in:

- [Initial submission](../send_consume/send.json)
- [Replay submission](../send_replay/send.json)

The two submission records contain identical request bytes, authorization headers, and authorization identity metadata.

The original submission produced Provider A `START` and `COMPLETE` boundary events.

The replay produced a verified Provider A `DENY` event with reason:

`auth_spent`

The associated persistent-state evidence records no additional consumption or execution during replay.

## Integrity Verification

The original [SHA256SUMS.txt](SHA256SUMS.txt) inventories six files.

From this directory:

```bash
sha256sum -c SHA256SUMS.txt
```

This README is additional documentation and is not included in the original inventory.

Do not modify the authorization package, request, issuance records, or historical hashes.

## Evidence Boundary

This directory establishes the exact authorization material used for the original request and subsequent replay.

It does not independently establish execution or replay rejection. Those outcomes require the provider-originated boundary events and persistent-state evidence.

See the [R01 evidence documentation](../README.md) for the complete experiment.
