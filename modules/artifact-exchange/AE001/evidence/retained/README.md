# AE001 Retained Harness Versions

This directory preserves earlier AE001 campaign-harness versions associated with the preflight runs.

They are retained as historical test artifacts. They are not the final scored harness and should not be substituted for the current campaign runner in `../../scripts/run_ae001.py`.

## Contents

```text
retained/
├── PREFLIGHT_R1/
│   └── run_ae001.py
└── PREFLIGHT_R2/
    └── run_ae001.py
```

### `PREFLIGHT_R1/run_ae001.py`

Harness version associated with `AE001_PREFLIGHT_20261018_R1`.

That preflight was **INCOMPLETE before deployment** because the encoded SSH source-transfer command exceeded the Windows command-line length limit. No AE001 case was scored from that run.

The harness is preserved so the incomplete preflight remains attributable to the exact campaign code used at the time.

### `PREFLIGHT_R2/run_ae001.py`

Harness version associated with `AE001_PREFLIGHT_20261018_R2`.

R2 replaced the oversized command-line source transfer with transfer over SSH standard input and completed the four-case preflight successfully.

After R2, and before the scored-run freeze, the harness classification logic was corrected so that authenticated unexpected admission in a rejection case is classified as **FAIL**, including when excess boundary events are also present.

That correction did not change the provider or relay implementation, artifact format, four-case matrix, or expected case outcomes.

The corrected and subsequently locked campaign harness is published at:

`../../scripts/run_ae001.py`

## Why These Files Are Retained

AE001 preserves superseded test harnesses rather than replacing them after the fact.

This directory therefore provides the code history needed to distinguish:

- an incomplete preflight caused by the test harness or execution environment;
- a successful preflight using the corrected transfer mechanism;
- the later pre-score harness correction; and
- the final harness used for scored execution.

The retained harnesses are provenance material. The scored result is established by the locked scored configuration, scored evidence, raw provider-signed boundary packages, provider state and execution records, and the final scorecard under `../scored/`.

## Related Evidence

Preflight outputs are under:

`../preflight/`

The scored run is under:

`../scored/AE001_SCORED_20261018_R1/`

Campaign provenance and the relationship between the retained harnesses and final scored version are documented in:

`../../PROVENANCE.md`
