# Operator Records

This directory contains the operator's running notes for MP003 and the pre-run baseline captured before scoring.

## Contents

| File | SHA-256 |
|---|---|
| `MP003_OPERATOR_NOTES.txt` | `3fd3cdd2d6ef0b356f37ea3445001ef5248f5fc50abd3e4bb1831503738df065` |
| `MP003_PRE_RUN_BASELINE.txt` | `72d4cf87109e4f59ed71a531cb2dd5247aa26631fcb2ff1f36ad40b5a6a0a4ff` |

Both files use Windows (CRLF) line endings.

## MP003_PRE_RUN_BASELINE.txt

Captured 2026-10-15 17:53:29 −04:00, before any R2 scored case.

It records the SHA-256 of the contract, run manifest, relay, association recorder, provider registry, both provider runtimes and mint utilities, Provider A's issuance keypair, and Provider B's issuance public key. Its own hash, `72d4cf87…`, is recorded in the operator notes under pre-run conditions.

## MP003_OPERATOR_NOTES.txt

The notes are append-only. Entries were added in time order beneath the header template, and earlier entries were never edited. Where an entry turned out to be wrong, a later entry corrects it and the original stays in place.

The header sections (`CASE LOG`, `OPERATOR ERRORS / MISFIRES`, `FINAL STATE`, `SHUTDOWN`) were left as a template. The actual record is in the timestamped entries that follow them.

### Entry index

| Local time (−04:00) | Entry |
|---|---|
| 21:52 | Pre-run residual state discovered (later corrected — see 22:18) |
| 22:00 | Pre-run state reset |
| 22:18 | B01 reconstruction / correction: the "residual" state was the first attempt's B01 |
| 22:27 | R2 clean restart |
| 22:39 | B01 R2 harness misfire (records 2–3) |
| 22:41 | B01 R2 scored PASS |
| 23:17 | Correction to the B01 misfire note |
| 23:17 | Pre-C01 provider state |
| 23:23 | C01 scored PASS |
| 23:26 | C02 scored PASS |
| 23:29 | C03 scored PASS |
| 23:34 | B02 scored PASS |
| 23:34 | Final state (R2) and association shutdown |
| 23:37 | Shutdown complete / transcripts retained |
| 23:54 | Correction: requester host |

### Corrections recorded in the notes

Three statements in the notes are known to be wrong. Each is corrected by a later entry, and the original wording is retained:

1. **Pre-run residual state (21:52).** Provider state found before the C cases was first recorded as pre-run residue. It was the first attempt's B01. Corrected at 22:18.
2. **B01 R2 misfire (22:39).** The note says empty authorization headers were forwarded. The provider code maps an empty value to `auth_missing`, but the providers reported `auth_malformed`, so the forwarded values were non-empty and undecodable. Corrected at 23:17. The misfire classification is unchanged.
3. **Requester host (header).** The header lists the Chromebook as the requester and attacker harness, and lists "Chromebook connected" as a network change. The Chromebook was not involved in MP003. C01 through B02 were sent from the OmniBook operator host. Corrected at 23:54.

### Preparation of entries

Entries from 23:17 onward were drafted with an AI assistant during the session and appended at the operator's direction. Each records values taken directly from command output, association records, and provider state files at that time.

## How to use these records

The notes are the operator's contemporaneous account. They explain sequence, intent, misfires, and corrections.

They are not the authoritative evidence. Where the notes and the evidence differ, the evidence governs:

- `../evidence/scored/association.jsonl` — hash-chained signed provider statements;
- provider state files in each case directory and in `final_provider_a/` and `final_provider_b/`;
- `../configs/` — the locked contract and run manifest.

The notes are not covered by `../evidence/scored/SHA256SUMS.txt`. Their hash is listed above.

## Related material

`../evidence/`

`../PROVENANCE.md`
