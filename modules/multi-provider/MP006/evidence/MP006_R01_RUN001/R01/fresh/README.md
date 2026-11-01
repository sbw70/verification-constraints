# MP006-R01 — Fresh Authorization

## Purpose

This directory preserves the separate Provider A authorization issued after physical power-loss recovery and successful rejection of the original authorization's replay.

The fresh authorization tests whether Provider A can continue accepting valid, previously unused authority while retaining its existing consumption history.

## Directory Contents

| File | Purpose |
|---|---|
| [request.json](request.json) | Fresh software-execution request |
| [authorization.json](authorization.json) | Provider A Ed25519-signed authorization package |
| [authorization.json.b64](authorization.json.b64) | Base64url-encoded package used in the authorization header |
| [identity.json](identity.json) | Request, authorization, binding, operation, and package identities |
| [mint_stdout.txt](mint_stdout.txt) | Original authorization-issuance output |
| [mint_stderr.txt](mint_stderr.txt) | Preserved issuance error output; empty in this run |

## Authorization Generation

The authorization was generated using the frozen MP005 Provider A issuance implementation.

The issuer:

1. Reads the preserved request bytes.
2. Calculates the request's SHA-256 representation.
3. Generates a fresh authorization nonce.
4. Binds the authorization to Provider A, the request representation, and verification context.
5. Calculates the authorization identifier.
6. Signs the authorization using the laboratory Ed25519 issuance key.
7. Preserves the signed package and encoded header representation.

The MP005 harness checks the authorization's request binding and identifier before recording its identity metadata.

The issuance keys are laboratory fixtures, not production credentials.

## Recorded Identity

**Provider:** `PROVIDER_A`

**Session:** `MP006_R01_RUN001`

**Authorization ID:**

`821ca36878ef72241d6bb02815ad5de8ce2e867f49d1807f6bf0cdd99ff24695`

**Verification context:**

`CTX_MP005_MP006_R01_FRESH`

**Request SHA-256:**

`86a190c781cc7aea213b156cec1d79790abbf88de8c7fb4945191c7a2a25cd78`

**Authorization package SHA-256:**

`bfd6350e5663b3eec39a4c2ae6a01b28a381b75c1084b7b20cacd9f44d94bb3f`

The preserved authorization, identity metadata, issuance output, and parent evidence inventory agree on the recorded identities.

The request retains `"test":"MP005"` because MP006 reuses the frozen MP005 harness. Its case and session identifiers identify the MP006 experiment.

## Separation From Original Authority

The fresh authorization differs from the original in:

- Authorization identifier.
- Authorization nonce.
- Request representation.
- Verification context.
- Operation binding.

The [pre-execution state](../before_fresh/) confirms that the fresh authorization was absent from both the consumption ledger and spent-state snapshot.

The original authorization remained consumed.

This distinction allows the test to evaluate new authorization execution without reusing previously spent authority.

## Submission and Execution

The preserved request and authorization were submitted through the NUVL relay.

The submission evidence is located in:

[send_fresh/](../send_fresh/)

The associated Provider A boundary records contain:

| Recorder sequence | Stage | Ledger sequence |
|---|---|---|
| 8 | `START` | 2 |
| 9 | `COMPLETE` | 2 |

Both records identify the fresh authorization and final ledger head.

The recorder marked both signatures as valid.

The [post-execution state](../after_fresh/) records:

- One additional consumption-ledger entry.
- One additional spent authorization.
- One additional software execution record.
- Preservation of the original consumption history.
- Valid hash linkage between ledger sequences 1 and 2.

The MP006 scorer returned `PASS` for all twelve fresh-execution checks.

## Integrity Verification

This directory does not contain a separate `SHA256SUMS.txt`.

All six files are included in the original [R01 evidence inventory](../SHA256SUMS.txt).

From the parent R01 directory:

```bash
sha256sum -c SHA256SUMS.txt
```

This README is additional documentation and is not included in the historical inventory.

Do not modify the authorization package, request, issuance records, or original evidence hashes.

## Evidence Boundary

This directory establishes the identity and preserved material of the fresh authorization.

Execution is established through the corresponding signed boundary records and provider-local persistent evidence, not through authorization issuance alone.

The experiment demonstrates successful use of fresh authority after the observed power interruption while previously consumed authority remained spent.

It does not establish hardware-level execution or protection against arbitrary replacement of persistent history.

See the [R01 evidence documentation](../README.md) for the complete experiment.
