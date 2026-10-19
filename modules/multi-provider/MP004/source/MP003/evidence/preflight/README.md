# Preflight Artifacts

This directory contains artifacts generated while validating the MP003 attacker tooling before scoring.

They are not scored evidence and were never used in a scored case.

## Contents

| File | SHA-256 |
|---|---|
| `c01_request.json` | `57a6baab34dc6c0e332286172570a1e63d6222e86275e6ce7d7a9207749e1250` |
| `c01_compromised_a.json` | `06ed048647c89fcfd4bbac187365bd4e034e5ec866d43374699c77829fc1b704` |
| `c01_compromised_a.json.b64` | `55fd18e67e85c0528c06f1cccebe1e1353f222041b7a23cda00a7c185dc4de53` |
| `c03_request.json` | `3714b61b2a86d84038179d6890b02501ce6f054a0c77463b81a4fb8c0bf42a02` |
| `c03_claim_b_signed_by_a.json` | `e3fa0df4d7202da6d678f1bc6959ba7f48cb86f0aea3a200a846e9616a69af52` |
| `c03_claim_b_signed_by_a.json.b64` | `dbe6fe5104521a13bd95af4aa3b68a0ba859acda37136a3feff368506b8538cd` |

## What they are

Two dry-run mints, one for each attacker utility:

| Artifact | Mint utility | Claimed provider | Request | Context | Authorization ID |
|---|---|---|---|---|---|
| `c01_compromised_a.json` | `attacker/mint_compromised_a.py` | `PROVIDER_A` | `{"action":"mp003_preflight","nonce":"MP003-PREFLIGHT-C01"}` | `CTX_MP003_PREFLIGHT_C01` | `0baf733b…` |
| `c03_claim_b_signed_by_a.json` | `attacker/mint_forged_b_with_a_key.py` | `PROVIDER_B` | `{"action":"mp003_preflight","nonce":"MP003-PREFLIGHT-C03"}` | `CTX_MP003_PREFLIGHT_C03` | `2b184bc7…` |

Each authorization's `request_repr` equals the SHA-256 of its preflight request file.

## Offline check

Both packages were checked offline against the public keys published in this module:

| Artifact | Authorization ID derivation | Under Provider A issuance key | Under Provider B issuance key |
|---|---|---|---|
| `c01_compromised_a.json` | correct | valid | invalid |
| `c03_claim_b_signed_by_a.json` | correct | valid | invalid |

This confirms the attacker utilities produced well-formed packages signed with the compromised Provider A issuance key before any scored use.

## Not sent and not scored

- Neither preflight authorization ID appears in any association log, scored or retained, or in any provider state file. These artifacts were not presented to the providers.
- They were minted for preflight requests and contexts, so their `request_repr` and `verification_context` do not match any scored request.
- Every scored case used a fresh mint against its own scored request. See `../scored/`.

The operator notes record that preflight artifacts are not used for scoring.

## Related evidence

Attacker utilities and key copy:

`../../attacker/`

Scored campaign:

`../scored/`
