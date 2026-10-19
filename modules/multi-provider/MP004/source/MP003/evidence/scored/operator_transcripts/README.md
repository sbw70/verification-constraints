# Operator Transcripts

This directory contains console output from the four MP003 processes during the scored session.

## Contents

- `association_console.txt` — association recorder console (OmniBook, `Xer0trust`).
- `provider_a_console.txt` — Provider A console (`Xer0trust-3`).
- `provider_b_console.txt` — Provider B console (`Xer0trust2`).
- `relay_console.txt` — relay console (`nuvl-relay`).

| File | SHA-256 |
|---|---|
| `association_console.txt` | `771fdd630261495bd84ba37e1776a6c2657254cd79691bf9bbe0ab64e406cc8b` |
| `provider_a_console.txt` | `63096a08d9f1dfb218ca035dc1303977cb9f649c1e352ac5e54c3fddd58b30b5` |
| `provider_b_console.txt` | `9cec726be0f129de1930b4b32c72e64d03fd8aad4008f07a8203825bba8bc7f4` |
| `relay_console.txt` | `016c46a2e7faf80b5f0ac5679271a57ade807b5b67c096aadc210af7a6904782` |

## Provenance of these files

These are **operator transcripts**, not log files written by the processes.

None of the four processes writes its console output to disk. After shutdown, the operator copied each terminal's visible output, and it was saved verbatim into these files. The files were added to the scored evidence set after the session, and `../SHA256SUMS.txt` was regenerated to include them. No other evidence file changed. This is recorded in `../../../operator/MP003_OPERATOR_NOTES.txt`.

The authoritative scored evidence remains the hash-chained `../association.jsonl` and the provider state files. These transcripts corroborate that evidence; they do not replace it.

## What they show

**Association.** The recorder's startup lines report the locked contract, manifest, recorder, and registry hashes. It then printed one `OBSERVED` line per submission and the `FINAL_RECORD_HASH` on shutdown, which matches the last record in `../association.jsonl`. The console `seq` counts submissions only (1–17) and therefore runs one behind the log's `record_seq`, which also counts `SESSION_START`. The banner reads `MP001_ASSOCIATION_RECORDER` because the recorder implementation is unchanged from MP001.

**Provider A.** One line per decision, including the B01 harness-misfire `DENY auth_malformed`, `EXECUTED` at local_seq 1–3 for B01, C01, and C02, and `DENY auth_missing` for C03 and B02.

**Provider B.** The B01 misfire `DENY`, B01 executed at local_seq 1, then `DENY auth_missing` (C01), `DENY auth_provider_mismatch` naming `0e2ed472…` (C02), `DENY auth_bad_sig` naming `11e016ab…` (C03), and B02 executed at local_seq 2. Provider B's console independently shows no execution between B01 and B02.

**Relay.** The relay logs nothing per request. Its startup banner states `Provider authorization verification: False` and `Provider secrets present: False`. The banner reads `MP001_NUVL_MULTI_PROVIDER_RELAY` because the relay implementation is unchanged from MP001.

## Shutdown

The association recorder was stopped first so `SESSION_END` was written while the providers were still up. Providers A and B and the relay were then stopped with Ctrl+C. Each printed a `KeyboardInterrupt` traceback from `serve_forever()`. None of these scripts installs a signal handler, so this traceback is the normal stop path, not a fault. Final provider state had already been captured after B02.

## Content note

These transcripts include the lab username, host names, home-directory paths, and private LAN addresses. No passwords or credentials appear in them.
