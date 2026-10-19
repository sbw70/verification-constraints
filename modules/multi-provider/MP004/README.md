# MP004 — Independent offline re-verification

**PASS** — MP004_SCORED_20261018_R1 passed B01, N01, N02, N03, N04, N05a and N05b.

An independently implemented offline verifier authenticated all 17 preserved MP003 provider packages and checked all 15 frozen campaign expectations without using the recorder's sig_valid, registry_match or verification_code fields as signature-verification inputs. Two retained MP003 harness-misfire denials are separately labeled.

It rejected a modified signed event, a modified signature and the wrong provider trust anchor. A false unsigned summary claiming Provider B executed C02 was contradicted by Provider B's authenticated DENY auth_provider_mismatch. Altering recorder metadata did not change the underlying signature results.

See [RESULTS.md](RESULTS.md) for outcomes and [PROVENANCE.md](PROVENANCE.md) for preparation, identities, retained corrections and claim limits. The working files were copied into this flat local publication root. Its future repository destination is modules/multi-provider/MP004/.

## Reproduce offline

Use Python 3.10 or newer (tested with 3.12.14) and cryptography 50.0.2. From this directory:

    python -m pip install -r requirements.txt
    python verifier/test_verify_mp004_portable.py
    python verifier/verify_mp004.py --manifest configs/MP004_RUN_MANIFEST.json --output evidence/preflight/MY_FRESH_REPRODUCTION

The output directory must be new. The installed verifier targets the frozen MP004 campaign, checks all locked source bytes, verifies provider-specific boundary signatures and emits per-record/case reports. Reproduction requires no network after dependencies are installed, private keys, live providers, relay, association recorder, or other physical machines. Do not overwrite historical runs.

## Layout

| Directory | Contents |
|---|---|
| configs/ | Locked contract/input/source/comparison files and implementation manifest |
| source/MP003/ | Unchanged selected MP003 publication references and evidence |
| fixtures/ | Six deliberately modified or misleading laboratory artifacts |
| verifier/ | Original scored verifier, original tests and portable test adaptation |
| evidence/ | Original preflight, scored run, retained draft and later publication checks |
| notes/ | Installation correction and publication/process notes |

Each added folder README describes actual contents. Original pinned MP003 files and scored artifacts are unchanged. The root SHA256SUMS.txt covers the final staging tree; nested checksum lists have their own directory as base. .gitattributes prevents Git line-ending conversion from breaking locked byte identities.

## Boundaries

This authenticates provider-signed software statements under pinned keys. It does not prove physical consequences, completeness, universal absence of execution, immutable storage, global chronology or resistance to boundary-key compromise. Published laboratory keys support reproduction, not adversarial post-publication historical authenticity. NUVL transports authority; providers retain authority; the association and offline verifier provide evidence.
