# Provider A

This directory contains the Provider A runtime, the Provider A mint utility, and Provider A's laboratory keys as used in MP003.

In MP003, Provider A is the provider whose authorization-issuance key is treated as compromised.

## Contents

| File | Role | SHA-256 |
|---|---|---|
| `provider_a.py` | Provider A runtime | `c875582b275f270b8e68af69ed4ee84896e83815cdf33b7d7c5ccc813fe2e606` |
| `mint_authorization_a.py` | legitimate Provider A authorization mint | `1a485e8a5d3de854cb31303b8d3bf1339ef72cb9b42f308490bd02519e76d7ec` |
| `provider_a_issuance_private.pem` | issuance signing key (**the key treated as compromised**) | `37f808b6901f5020fb7b68924217d76f7923d898e44913a6338008d85ac15fd8` |
| `provider_a_issuance_public.pem` | issuance verification key | `a52276369981962b878311ec4e33186af25ac10cd359fafbc760e118e607ad71` |
| `provider_a_private.pem` | boundary-signing key | `f4fb81ff6901b6f9ef8ea4f870430760cf7cdc2eb28dff74125e277fa6465ff9` |
| `provider_a_public.pem` | boundary verification key | `4f9f01b0296f75a7acf8c3fd11bf7f27d75f0526e7912a02d0a725b1e6fbaa19` |

All six files are byte-identical to the MP002 Provider A files. The runtime and mint hashes match the locked MP003 run manifest.

These are laboratory keys, published deliberately so the evidence can be verified. They are not used outside this test series.

## Deployment in MP003

- Host: Dell laptop (`Xer0trust-3`, 192.168.1.118)
- Listens on `0.0.0.0:9090`, endpoint `POST /ingest`
- Sends signed boundary events to the association recorder at `http://192.168.1.102:9191/boundary`
- Boundary key ID: `sha256:e4664ee3b7bb0012fb7d8f763c9df74594d8a6bec8488d97532a5846cc04b6ff`

The scored session started with `Spent entries loaded: 0`, recorded in `../evidence/scored/operator_transcripts/provider_a_console.txt`.

## Two keypairs, two roles

Provider A has two separate Ed25519 keypairs:

- **Issuance keypair.** The mint utility signs authorizations with the private key. The runtime verifies incoming authorizations with the public key. The runtime itself does not load the issuance private key.
- **Boundary keypair.** The runtime signs `START`, `COMPLETE`, and `DENY` events with the private key. The association recorder verifies them with the registered public key.

MP003 compromises only the issuance private key. The boundary-signing key was not compromised, so every Provider A boundary event in the scored record is a genuine Provider A statement.

## What the runtime does

For each artifact received from the relay, the runtime follows the contract's 17-step validation order (see `../configs/README.md`). In outline:

- it recomputes the binding and operation ID itself;
- it requires an authorization whose `provider_id` is `PROVIDER_A`, with a correct authorization ID and a valid signature under Provider A's issuance public key;
- it checks the request representation and context;
- it rejects already-spent authorizations;
- it durably records the authorization as spent before emitting `START`;
- it records local execution durably, then emits `COMPLETE`;
- for any rejection, it emits a signed `DENY` with a reason code and does not consume.

Spent state and execution records are written with `fsync`. Spent state is written atomically via a temporary file and rename.

The runtime refuses to start if the spent-state file is missing or invalid, and if the boundary private and public keys do not match.

## Provider A in MP003

| Case | Received | Result |
|---|---|---|
| B01 | legitimate Provider A authorization | executed (`local_execution_seq` 1) |
| C01 | authorization minted with the compromised issuance key | executed (`local_execution_seq` 2) |
| C02 | authorization minted with the compromised issuance key | executed (`local_execution_seq` 3) |
| C03 | nothing | `DENY auth_missing` |
| B02 | nothing | `DENY auth_missing` |

Provider A executed both authorizations minted with the compromised key. This is expected: an attacker holding Provider A's issuance private key can produce authority that Provider A cannot distinguish from its own. MP003 does not claim Provider A resists compromise of its own issuance key.

## Known implementation limitation

Boundary events are sent to the association recorder once, with a 2-second timeout and no retry or durable outbox. If the recorder were unreachable, the event would be lost from the association record, although provider-local state would still be correct. Every MP003 boundary event was delivered (`sent=True` in the console transcript), and all 17 appear in the association log. Late or offline delivery is out of scope for MP003.

## Related material

`../attacker/` — the attacker's byte-identical copy of `provider_a_issuance_private.pem` and the attacker mint utilities

`../provider_b/`

`../association/`

`../evidence/scored/final_provider_a/`
