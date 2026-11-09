# MH001 — Local Deployment Validation History

## Purpose

This directory preserves the three original local validation attempts for the MH001 R4.3 deployment package.

These checks were performed before live deployment. They tested the frozen multi-hub implementation, requester restrictions, deployment preconditions, and independent observer verification logic.

**Session:** `MH001_R43_RUN001`

**Validation date:** November 5, 2026 UTC

**Final local validation status:** `LOCAL_DEPLOYMENT_PACKAGE_VALIDATED_NOT_DEPLOYED`

These records demonstrate local software validation. They are not the subsequent live T01–T04 experiment evidence.

## 1. Directory Contents

```text
validation/
├── attempt-001/
│   ├── LOCAL_VALIDATION.json
│   ├── original_R43_29_tests.txt
│   └── new_deployment_tests.txt
├── attempt-002/
│   ├── LOCAL_VALIDATION.json
│   ├── original_R43_29_tests.txt
│   └── new_deployment_tests.txt
└── attempt-003/
    ├── LOCAL_VALIDATION.json
    ├── original_R43_29_tests.txt
    └── new_deployment_tests.txt
```

Each attempt contains three files:

| File | Responsibility |
|---|---|
| `LOCAL_VALIDATION.json` | Overall result, test counts, safety conditions, and remaining prerequisites |
| `original_R43_29_tests.txt` | Results from the 29 original R4.3 hub/requester tests |
| `new_deployment_tests.txt` | Results from 23 additional deployment and observer tests |

The three attempts are separate historical records. Later success does not erase an earlier failure.

## 2. Validation Results

| Attempt | Original R4.3 | Deployment tests | Overall |
|---|---|---|---|
| 001 | 29 run; 1 failure, 18 errors | 23/23 PASS | FAILED |
| 002 | 29/29 PASS | 23/23 PASS | PASS |
| 003 | 29/29 PASS | 23/23 PASS | PASS |

The two successful attempts each completed **52/52 tests**.

### Attempt 001 — Initial Failure

Started:

`2026-11-05T04:36:23Z`

Recorded status:

`LOCAL_DEPLOYMENT_VALIDATION_FAILED`

The original R4.3 suite encountered Windows socket-access errors, including:

`PermissionError: [WinError 10013]`

The failed direct/chained forwarding assertion recorded zero mock deliveries where two were expected.

The separate 23-test deployment suite passed.

This attempt was retained rather than replaced or represented as successful.

### Attempt 002 — Successful Validation

Started:

`2026-11-05T04:38:53Z`

Recorded status:

`LOCAL_DEPLOYMENT_PACKAGE_VALIDATED_NOT_DEPLOYED`

Results:

- Original R4.3 tests: 29 PASS.
- Deployment and observer tests: 23 PASS.
- Failures: 0.
- Errors: 0.
- Skipped: 0.

### Attempt 003 — Successful Repeat

Started:

`2026-11-05T04:43:36Z`

Recorded status:

`LOCAL_DEPLOYMENT_PACKAGE_VALIDATED_NOT_DEPLOYED`

Results:

- Original R4.3 tests: 29 PASS.
- Deployment and observer tests: 23 PASS.
- Failures: 0.
- Errors: 0.
- Skipped: 0.

Attempt 003 independently repeated the successful local validation result.

## 3. Original R4.3 Tests

The original 29-test group exercises the frozen hub and requester implementation.

Its coverage includes:

- Direct and chained hub forwarding.
- Preserving opaque request bodies and headers.
- Destination-header handling.
- Request and response framing.
- Unsupported or malformed messages.
- Static route validation and loop prevention.
- Timeout behavior.
- No automatic retry after transport failures.
- Requester destination allowlists.
- Rejection of unapproved remote endpoints.
- Preservation of provider authority boundaries.

These tests use local mocks and loopback connections.

They do not demonstrate live provider authorization or durable provider-state behavior.

The original source is preserved under:

`frozen_R43/`

## 4. Additional Deployment Tests

The 23-test deployment group exercises safeguards introduced for the MH001 live deployment package.

Its coverage includes:

**Configuration and routing**

- Approved endpoint matching.
- Reviewed route compatibility.
- Expected configuration hashes.
- Provider identity and isolation.
- Rejection of historical run-root reuse.
- Prevention of unapproved startup.
- No unapproved rerouting or retries.

**Observer and authorization evidence**

- Valid signatures and expected provider outcomes.
- Rejection of tampered signatures.
- Rejection of incorrect provider bindings.
- Rejection of incorrect ledger heads.
- Detection of truncated observer history.
- Rejection of reused historical signing identities.
- Rejection of previously observed denial events as fresh evidence.
- Rejection of a replay that produces new execution.
- Requirement for `DENY / auth_spent` during T03.
- Requirement for valid START and COMPLETE events for fresh authority.
- Refusal to infer provider execution solely from a hub response.

The original test implementation is:

`test_deployment.py`

## 5. Local Validation Safety Boundaries

All three `LOCAL_VALIDATION.json` files record:

```json
{
  "original_workspace_unchanged": true,
  "keys_generated": false,
  "actual_provider_imports": false,
  "provider_state_initialized": false,
  "observer_started": false,
  "lab_hosts_contacted": false,
  "deployed": false,
  "STOP_1": "ACTIVE"
}
```

The validation harness restricted network access to the original loopback mock hubs.

The reviewed live configurations were exercised using in-memory transports.

The harness also prevented provider imports, key generation, observer startup, and provider-state initialization.

These safeguards distinguish local preparation from live deployment.

**A successful local validation result did not authorize laboratory execution.**

## 6. Reproducing Local Validation

The original validation runner is:

`validate_review.py`

It loads the original R4.3 tests and the additional deployment tests, applies offline safety guards, and writes a separate output directory.

### Prerequisites

A reproduction requires:

- Python 3 and the test dependencies.
- The complete frozen R4.3 source.
- The deployment test code.
- The referenced original workspace required by `BASELINE.json`.
- Permission to use local loopback test sockets.
- A new, unused validation output directory.

The historical `BASELINE.json` references the original workspace. A different checkout or machine may require a separate, reviewed reproduction package with the appropriate baseline paths.

Do not alter the published original baseline to make a local command pass.

### Example Command

In a separate working copy with its prerequisites satisfied:

```bash
python3 -B validate_review.py --output validation/reproduction-001
```

The output directory must not already exist.

The runner creates:

- `LOCAL_VALIDATION.json`
- `original_R43_29_tests.txt`
- `new_deployment_tests.txt`

A successful run should report:

- 29 original R4.3 tests passed.
- 23 deployment tests passed.
- No failures or errors.
- `LOCAL_DEPLOYMENT_PACKAGE_VALIDATED_NOT_DEPLOYED`.

Local socket permissions and operating-system behavior must be considered when comparing results across machines.

Do not execute this command in the published historical evidence workspace.

## 7. Verify the Preserved Records

All nine original validation files appear in:

`evidence/MH001_FINAL_SHA256SUMS.txt`

From the scored-run root on Linux:

```bash
grep '  validation/attempt-' evidence/MH001_FINAL_SHA256SUMS.txt | sha256sum -c -
```

Expected result:

**9/9 historical validation files match.**

This verifies that the preserved results match the original final manifest.

It does not rerun the tests.

## 8. Relationship to the Live Experiment

The local validation attempts occurred on November 5, 2026.

The scored live experiment followed on November 7–8, 2026 UTC.

The later live evidence is located under:

`evidence/`

That evidence includes:

- Requester receipts.
- Hub forwarding logs.
- Provider-ingress captures.
- Provider consumption and execution records.
- Independently signed observer events.

These live observations must not be attributed to the earlier local validation attempts.

Likewise, a locally passing mock test is not proof that a particular live provider executed or denied a request.

## 9. Outstanding Requirements at Validation Time

The successful local reports still identified work requiring separate authorization or live preflight, including:

- Explicit STOP 1 approval.
- Fresh provider-host signing keys and approved public trust.
- New provider-controlled durable state.
- Verification of installed source hashes and isolated ports.
- Review of the Dell MP006 indirect autostart chain.
- Independent provider-ingress capture.
- Observer readiness and rehearsal latency assessment.

These are historical pending items from November 5.

Their presence does not mean they remained uncompleted during the later scored experiment. Their eventual completion must be established from separate live records.

## 10. Preservation Rules

All nine original files belong to the 132-file scored evidence inventory.

This README is supplemental documentation.

Do not:

- Delete attempt 001 because it failed.
- Replace attempt 001 logs with successful output.
- Merge multiple attempts into a single result.
- Rewrite original timestamps or test counts.
- Modify original validation records to reflect later live deployment.
- Regenerate historical hashes.

New validation runs must use independent output directories and manifests.

## Conclusion

The preserved validation history establishes a failed initial attempt followed by two successful 52-test local validation runs.

The records support readiness of the reviewed software package for separately authorized deployment.

They do not substitute for the subsequent live experiment, its independent evidence, or its procedural approval requirements.
