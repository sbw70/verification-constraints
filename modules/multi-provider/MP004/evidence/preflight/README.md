# MP004 Preflight Evidence

This directory contains the preflight verification run completed before the scored MP004 campaign.

Its purpose was to check that the independent verifier, fixture generation, source selection, trust-anchor handling, and case logic behaved as expected before scoring.

It is implementation-preparation evidence, not the authoritative scored result.

## Contents

### `MP004_PREFLIGHT_20261018_R1/`

This directory contains the complete preflight run output:

- `SUMMARY.md` — overall preflight result and case-level status.
- `case_results.json` — machine-readable results for B01 and N01–N05.
- `record_results.jsonl` — per-record verification output.
- `recorder_comparison.jsonl` — post-verification comparison against recorder metadata.
- `fixture_manifest.json` — exact negative-fixture recipes, source records, expected outcomes, and hashes.
- `run_metadata.json` — verifier, manifest, dependency, platform, source-count, and invocation metadata.
- `unit_tests.txt` — supplementary verifier unit-test transcript.
- `SHA256SUMS.txt` — integrity inventory for the preflight run directory.

## Preflight result

The preflight run returned:

**PASS**

All seven defined cases produced their expected result:

| Case | Purpose | Preflight result |
|---|---|---|
| B01 | Valid preserved provider evidence | PASS |
| N01 | Signed-field tamper | PASS |
| N02 | Signature tamper | PASS |
| N03 | Wrong provider trust anchor | PASS |
| N04 | False external summary | PASS |
| N05a | Recorder metadata falsely marks valid evidence invalid | PASS |
| N05b | Recorder metadata falsely marks invalid evidence valid | PASS |

For the negative cases, PASS means the verifier produced the expected rejection or contradiction. It does not mean the altered artifact was accepted.

## Supplementary verifier tests

Nine additional unit tests passed before scoring.

They exercised verifier behavior including:

- rejecting boolean values where integer version `1` is required;
- rejecting duplicate JSON fields;
- handling absence of recorder metadata;
- rejecting non-finite JSON numbers;
- rejecting padded signature encoding;
- rejecting path escape attempts;
- rejecting swapped provider trust anchors;
- detecting signed Unicode-field modification;
- preventing untrusted claims from selecting a verification key.

These tests supplement the defined MP004 case matrix. They are not additional scored cases.

## Source and implementation identity

The preflight run checked:

- 111 selected MP003 source files;
- all 67 entries in the MP003 scored evidence checksum manifest.

The recorded verifier SHA-256 was:

`452111ef7b7f96e2f42d14a416605ba53ee5b878b3dc05ce2729f6dc9db096c7`

The run used the locked MP004 run manifest and generated the same defined fixture classes later used for scoring.

## Evidence meaning

A successful preflight established that the test harness was capable of distinguishing:

- authentic from tampered provider-signed evidence;
- correct from incorrect provider trust anchors;
- provider evidence from unsupported later summaries;
- independently derived verification results from recorder-supplied classifications.

This reduced the risk that the scored run would fail because of an untested verifier or fixture-construction error.

It does not replace the scored campaign.

## Limits

The preflight does not establish an independent MP004 result beyond the later scored run.

It does not prove physical execution, evidence completeness, immutable storage, global chronology, or any execution-authority property.

The association recorder was not used as a verification engine. Recorder classifications were compared only after the independent verifier had reached its own result.
