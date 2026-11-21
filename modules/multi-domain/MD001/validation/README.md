# MD001 — Local Adapter Validation

This directory contains local validation evidence for the MD001 physical-deployment adapter.

These tests were performed before physical deployment and scoring.

They evaluate application integration, artifact handling, relay behavior, negative-test mutation, and HTTP observation utilities.

They do not constitute physical-network scored results.

## Validation history

Five timestamped validation directories are retained.

| Directory | Purpose |
|---|---|
| `20261118T035131Z_82147bd7/` | Initial adapter-validation attempt |
| `20261118T035153Z_9edc3256/` | Subsequent adapter-validation attempt |
| `20261118T035245Z_eef5c4c2/` | Intermediate adapter validation |
| `20261118T035328Z_c2e46f14/` | Final successful adapter integration |
| `20261118T035639Z_b8352e18/` | Offline HTTP extraction validation |

The original validation report records two initial loopback-send failures and a subsequent 9-pass/1-fail run.

The latter exposed an HTTP handling issue involving rejection before the request body was drained.

The adapter was corrected, and the successful validation was retained separately.

Earlier attempts were not overwritten.

## Final adapter integration

The selected integration run is:

`20261118T035328Z_c2e46f14/`

Recorded result:

**12 PASS — 0 FAIL**

The validation exercised actual local subprocesses using loopback substitutions for the proposed physical network configuration.

Checks covered:

- Producer operation, signing, and transmission.
- B01 artifact delivery and matching observed bytes.
- Frozen relay diagnostic hashes.
- N01 downstream mutation and signature rejection.
- B02 acceptance by a restarted verifier.
- Repeated verification of the original artifact.
- Unused route denial.
- Invalid HTTP path rejection.
- Relay peer filtering.
- Original project preservation.
- Copied runtime integrity.

These are adapter integration checks, not additional physical scored cases.

## HTTP extraction validation

The extraction validation is recorded in:

`20261118T035639Z_b8352e18/`

Recorded result:

**6 PASS — 0 FAIL**

The tests evaluated extraction from synthetic, already-reassembled HTTP request streams.

They included:

- Valid single-request extraction.
- Truncated stream rejection.
- Extra-request rejection.
- Incorrect path rejection.
- Incorrect destination rejection.
- Unsupported chunked framing rejection.

These checks do not establish successful physical packet capture or TCP reassembly.

The observation utility processes supplied stream bytes. It does not reconstruct TCP packets independently.

## Combined local result

The original validation report records:

| Category | PASS | FAIL |
|---|---:|---:|
| Adapter integration | 12 | 0 |
| HTTP extraction | 6 | 0 |
| **Total** | **18** | **0** |

The recorded status was:

`LOCAL_ADAPTERS_VALIDATED_AWAITING_DEPLOYMENT_APPROVAL`

This status applies to the predeployment validation stage.

It must not be interpreted as the final physical experiment status.

## Source preservation

The adapter validation checked the copied runtime implementation against the retained source identities.

The original project lock recorded 208 files.

The final integration check reported that the original project mapping remained unchanged.

The desktop baseline was not rewritten or rerun as part of this adapter validation.

## Evidence interpretation

Local adapter validation supports conclusions about the tested implementation under simulated network conditions.

It does not independently establish:

- Physical network isolation.
- Actual firewall enforcement.
- Physical producer power loss.
- Complete TCP packet reconstruction.
- Independent physical host operation.
- Hardware execution isolation.

Those properties require separate physical evidence.

## Historical integrity

Each validation directory is retained under its original timestamped identity.

Do not modify:

- Original `RESULTS.json` files.
- Failure records.
- Process observations.
- Test artifacts.
- Source snapshots.
- Historical SHA-256 manifests.

New validation attempts must use new directories.

Do not replace failed runs with later successful results.

## Related documentation

The original adapter validation report is:

[`../VALIDATION.md`](../VALIDATION.md)

The physical test plan is:

[`../TEST_PLAN.md`](../TEST_PLAN.md)

The observation implementation is:

[`../observe.py`](../observe.py)

The deployment adapter is:

[`../md001.py`](../md001.py)

The original desktop baseline is retained separately under:

[`../MULTI_DOMAIN_001/`](../MULTI_DOMAIN_001/)

## Verification boundary

Successful local validation establishes that the adapter behaved as tested under the recorded local conditions.

It does not establish that the same behavior occurred on independently operated physical hosts.

The later B01, N01, and B02 physical cases must be evaluated using their own scored evidence.
