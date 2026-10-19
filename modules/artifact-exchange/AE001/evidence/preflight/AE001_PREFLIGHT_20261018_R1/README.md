# AE001 Preflight — AE001_PREFLIGHT_20261018_R1

This directory preserves the first AE001 preflight attempt.

Run ID: **AE001_PREFLIGHT_20261018_R1**  
Phase: **preflight**  
Status: **INCOMPLETE**

No AE001 test case executed in this run.

## Result

The preflight stopped before deployment with:

```text
FileNotFoundError: [WinError 206] The filename or extension is too long
```

The initial harness attempted to transfer an encoded source bundle through the Windows command line. The resulting command exceeded the platform command-line length limit.

This was a harness/transport failure, not a failure of the AE001 property under test.

The scorecard therefore contains:

- zero executed cases;
- no PASS or FAIL case result; and
- overall status `INCOMPLETE`.

## Preserved Files

```text
AE001_PREFLIGHT_20261018_R1/
├── AE001_CONTRACT.md
├── AE001_RUN_MANIFEST.json
├── SCORECARD.json
├── SHA256SUMS.txt
├── canonical_state_after.json
└── input_identity.json
```

These files preserve the state of the attempted preflight rather than presenting it as a completed test.

## What Did Not Happen

Because the run stopped before deployment:

- Provider A was not exercised by an AE001 case;
- Provider B was not exercised by an AE001 case;
- the four-case matrix did not run;
- no AE001 execution result was scored; and
- no architectural conclusion is derived from this preflight.

The absence of case evidence in this directory is therefore expected.

## Correction

The source-transfer mechanism was changed for the next preflight so that source bytes were transferred through SSH standard input rather than embedded in an oversized Windows command line.

The corrected preflight is preserved separately at:

`../AE001_PREFLIGHT_20261018_R2/`

The original R1 harness is retained at:

`../../retained/PREFLIGHT_R1/run_ae001.py`

It is preserved for provenance and is not the final scored harness.

## Integrity

`SHA256SUMS.txt` records the hashes of the files retained from this incomplete run.

Those checksums identify the preserved run bytes. They do not convert the incomplete preflight into scored evidence.

## Status

**INCOMPLETE — no AE001 cases executed.**

The completed preflight and scored evidence must be used for evaluation of the tested property.
