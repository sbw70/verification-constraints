# Association Recorder

This directory contains the association recorder, its provider registry, and the trust anchors it uses to verify provider boundary events.

The association is evidence infrastructure. It records and verifies what providers say they did. It does not authorize, approve, combine, or override any provider decision.

## Contents

| File | Role | SHA-256 |
|---|---|---|
| `association_recorder.py` | recorder implementation | `fad60dfc8df53337d2e41288c2c4973442258cae4240945ebbd0aa8920550bfc` |
| `provider_registry.json` | maps each provider ID to its expected boundary key ID and public key file | `59d739588427d87313e3434982d943a9c82bad26c3fe3deb7d5488efadb6088d` |
| `trust/provider_a_public.pem` | Provider A boundary verification key | `4f9f01b0296f75a7acf8c3fd11bf7f27d75f0526e7912a02d0a725b1e6fbaa19` |
| `trust/provider_b_public.pem` | Provider B boundary verification key | `bcb4441a3ad143b5a3d646189d15ba806340c52530ba9b5ef4e19f30e0c59e47` |

The trust files are byte-identical to `../provider_a/provider_a_public.pem` and `../provider_b/provider_b_public.pem`. They are the providers' **boundary** public keys. The association holds no issuance keys, public or private, and cannot verify or produce provider authorization.

The recorder and registry are byte-identical to MP001 and MP002. The recorder's startup banner therefore still reads `MP001_ASSOCIATION_RECORDER`. That banner does not change its behavior.

## Registry

| Provider | Boundary key ID |
|---|---|
| `PROVIDER_A` | `sha256:e4664ee3b7bb0012fb7d8f763c9df74594d8a6bec8488d97532a5846cc04b6ff` |
| `PROVIDER_B` | `sha256:db764408aa319642363057d804f0c2a3d2c7dd22de86ae4a6d6549cb97f60225` |

At startup the recorder loads each public key, recomputes its key ID, and refuses to start if it does not match the registry.

## Deployment in MP003

- Host: OmniBook operator host (`Xer0trust`, 192.168.1.102)
- Listens on `0.0.0.0:9191`
- `POST /boundary` — receives provider boundary submissions
- `GET /health` — status check

## What the recorder does

**Session start.** It refuses to start if the target log file already exists, so a log cannot be silently overwritten. It writes a `SESSION_START` record containing the SHA-256 of the recorder, registry, run manifest, and contract it was started with, plus the registered providers.

**Each submission.** For every `POST /boundary`, it appends one `SUBMISSION` record containing:

- receive sequence number, UTC time, monotonic time, source address and port;
- SHA-256 and base64 of the raw received bytes;
- the claimed fields: provider ID, operation ID, stage, key ID, binding, boundary value, authorization ID and nonce, reason code;
- `registry_match`, `sig_valid`, and `verification_code`;
- `duplicate_of_seq` if an identical validly signed event was already recorded;
- any unrecognized fields.

Malformed, unknown-provider, wrong-key, bad-signature, and duplicate submissions are all recorded, not dropped.

Signature verification uses the registered boundary public key over `NUVL-MP-BOUNDARY-v1|` plus the canonical JSON of the event.

**Hash chain.** Each record contains `record_seq`, `prev_record_hash`, and `record_hash = SHA256(canonical JSON of the record without record_hash)`. The first record chains from 64 zeros. Records are written with `fsync`.

**Session end.** On orderly shutdown (Ctrl+C), it writes `SESSION_END` with the submission count and prints `FINAL_RECORD_HASH`.

## What the recorder does not do

- It does not authorize or cause provider execution. It replies `204` to every boundary submission and returns nothing a provider acts on.
- It does not decide whether a provider's decision was correct.
- It does not compute quorum, cross-provider success, or transaction outcome. Pass/fail scoring was done separately, after the session, from the preserved evidence.
- It does not make provider-local timestamps globally authoritative. Its record order reflects arrival order at the recorder only.

## The recorder in MP003

Scored session `MP003_SCORED_20261015_R2`:

- 19 records: `SESSION_START`, 17 submissions, `SESSION_END`;
- all 17 submissions `sig_valid`, `registry_match`, `verification_code=ok`, no duplicates;
- hash chain verified; final record hash `4c3282924708f504323bbd2cb1188bd0f2071e54a66b5bdb928e344abaa0a906`, matching the value the recorder printed on shutdown.

The recorder accurately recorded Provider B's refusals in C02 and C03 as signed Provider B statements, and Provider A's executions of attacker-minted authorizations as signed Provider A statements. It did not judge either.

In the first attempt (`../evidence/retained_partial/`), the recorder was not stopped cleanly, so that log has no `SESSION_END`.

## Known limitations

- The console `seq` counts submissions only and runs one behind the log's `record_seq`.
- The recorder trusts the registered boundary keys. MP003 did not compromise any boundary key. If a provider's boundary key were compromised, the recorder would accept forged statements from that provider as valid. That case is outside MP003's scope.
- Independent offline re-verification of the association log, without relying on the recorder's own `sig_valid` judgments, is the planned subject of MP004.

## Related material

`../evidence/scored/association.jsonl`

`../evidence/scored/operator_transcripts/association_console.txt`

`../configs/MP003_CONTRACT.md` — §§13–14 and §18
