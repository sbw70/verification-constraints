# MD001 — Local Validation Evidence

## Overview

This directory preserves local validation evidence for the MD001 Multi-Domain Stateless Verification implementation.

The validation records document development-stage execution of the application, relay, ingress, verifier, and supporting test harness before the physical-network scored experiments.

Five validation result files are preserved.

**Validation classifications:**

- `LOCAL_LOOPBACK_ADAPTER_VALIDATION_ONLY`
- `SYNTHETIC_REASSEMBLED_STREAM_UNIT_CHECKS`

**Final successful local adapter validation:** 12 PASS / 0 FAIL  
**Synthetic stream unit checks:** 6 PASS / 0 FAIL

Earlier unsuccessful validation attempts are retained as historical evidence.

These results are not physical-network scored runs.

## 1. Validation Objective

The local validation examined whether the implementation could:

1. Generate and sign an operation-completion assertion.
2. Transport the assertion through the configured relay and ingress components.
3. Preserve the signed artifact bytes.
4. Accept a valid assertion.
5. Reject an assertion modified without replacing its signature.
6. Verify a previously issued assertion without contacting its original producer.
7. Reject selected invalid routing and request conditions.
8. Preserve the integrity of the frozen implementation.
9. Reject selected malformed or unsupported HTTP stream representations.

The tests exercise implementation behavior in controlled local environments.

They do not independently establish physical-network behavior.

## 2. Validation History

The directory preserves five validation executions.

| Validation directory | Mode | Passed | Failed |
|---|---|---:|---:|
| `20261118T035131Z_82147bd7` | Local loopback | 0 | 1 |
| `20261118T035153Z_9edc3256` | Local loopback | 0 | 1 |
| `20261118T035245Z_eef5c4c2` | Local loopback | 9 | 1 |
| `20261118T035328Z_c2e46f14` | Local loopback | 12 | 0 |
| `20261118T035639Z_b8352e18` | Synthetic stream unit checks | 6 | 0 |

The results demonstrate progression from incomplete validation attempts to successful completion of the defined local checks.

The failed attempts remain part of the historical record.

The successful runs do not retroactively change the recorded outcomes of earlier attempts.

## 3. Initial Validation Attempts

### Attempt 1

Directory:

```text
20261118T035131Z_82147bd7/
```

The preserved `RESULTS.json` records:

```json
{
  "mode": "LOCAL_LOOPBACK_ADAPTER_VALIDATION_ONLY",
  "passed": 0,
  "failed": 1,
  "physical_evidence": false
}
```

The failed check was:

```text
harness_completed
```

The directory preserves application, configuration, process, and diagnostic records associated with the attempt.

The result establishes that the harness did not complete successfully.

The summary alone does not establish the underlying cause.

### Attempt 2

Directory:

```text
20261118T035153Z_9edc3256/
```

The preserved result again records:

```json
{
  "mode": "LOCAL_LOOPBACK_ADAPTER_VALIDATION_ONLY",
  "passed": 0,
  "failed": 1,
  "physical_evidence": false
}
```

The failed check was:

```text
harness_completed
```

This attempt also failed to complete the defined validation sequence.

Its diagnostic records are retained separately.

### Attempt 3

Directory:

```text
20261118T035245Z_eef5c4c2/
```

The preserved result records:

```json
{
  "mode": "LOCAL_LOOPBACK_ADAPTER_VALIDATION_ONLY",
  "passed": 9,
  "failed": 1,
  "physical_evidence": false
}
```

Nine functional checks passed.

The failed check was:

```text
harness_completed
```

The passing checks included:

- Valid producer operation, signing, and submission.
- Byte identity between ingress and verifier.
- Relay body-hash agreement.
- Modified-signature rejection.
- Retention of the original signature during mutation.
- Verification using a fresh process without the producer.
- Acceptance of the original artifact again.
- Local denial of an unused route.
- Rejection of an incorrect request path.

The overall validation attempt did not pass because the harness-completion check failed.

The individual passing checks remain useful diagnostic evidence but must not be represented as a successful complete run.

## 4. Successful Local Adapter Validation

Directory:

```text
20261118T035328Z_c2e46f14/
```

The preserved `RESULTS.json` records:

```json
{
  "mode": "LOCAL_LOOPBACK_ADAPTER_VALIDATION_ONLY",
  "passed": 12,
  "failed": 0,
  "physical_evidence": false
}
```

All 12 defined checks passed.

### Recorded Checks

| Check | Result |
|---|---|
| `B01_producer_operates_signs_and_sends` | PASS |
| `B01_ingress_and_verifier_identical_bytes` | PASS |
| `frozen_relay_records_same_body_hash` | PASS |
| `N01_rejected_invalid_signature` | PASS |
| `N01_original_signature_retained` | PASS |
| `B02_fresh_process_fresh_crypto_no_producer` | PASS |
| `same_artifact_accepted_again` | PASS |
| `unused_A_route_denied_locally` | PASS |
| `wrong_path_rejected` | PASS |
| `ingress_enforces_pi_peer` | PASS |
| `entire_original_project_unchanged` | PASS |
| `runtime_matches_frozen_copies` | PASS |

### Valid-Artifact Checks

The validation confirmed that the producer could perform the local operation, sign the resulting assertion, and submit it.

The relay and ingress checks confirmed preservation of the assertion bytes under the tested configuration.

These checks support the implementation behavior later examined in the B01 scored experiment.

### Mutation-Rejection Checks

The validation confirmed that the verifier rejected the tested modified assertion.

The original signature was retained during the modification.

These checks support the implementation behavior later examined in the N01 scored experiment.

### Producer-Independent Verification Checks

The validation confirmed that a fresh local verifier process could evaluate the previously issued assertion without contacting the producer.

The same original assertion was accepted again.

These checks support the implementation behavior later examined in B02.

They do not establish replay prevention.

### Routing and Integrity Checks

The validation also recorded successful checks for:

- Denial of the unused Domain A route.
- Rejection of an incorrect request path.
- Enforcement of the configured relay peer at ingress.
- Preservation of the original project.
- Agreement between the runtime and frozen application copies.

These results are limited to the conditions implemented by the local validation harness.

**Local adapter validation outcome: PASS — 12/12 checks.**

## 5. Synthetic Stream Validation

Directory:

```text
20261118T035639Z_b8352e18/
```

The preserved result identifies:

```text
SYNTHETIC_REASSEMBLED_STREAM_UNIT_CHECKS
```

It records:

```json
{
  "passed": 6,
  "failed": 0,
  "physical_capture_validated": false
}
```

### Recorded Checks

| Check | Result |
|---|---|
| `valid_one_direction_body_exact` | PASS |
| `truncated_rejected` | PASS |
| `extra_request_rejected` | PASS |
| `wrong_path_rejected` | PASS |
| `wrong_destination_rejected` | PASS |
| `chunked_rejected` | PASS |

The checks evaluate the handling of selected synthetic HTTP stream conditions.

The validation confirms that the tested stream-processing logic accepted the defined valid case and rejected the specified invalid cases.

The result explicitly records:

```text
physical_capture_validated = false
```

Therefore, the synthetic stream result must not be represented as validation of an actual physical-network packet capture.

**Synthetic stream validation outcome: PASS — 6/6 checks.**

## 6. Evidence Organization

Each local adapter validation directory preserves a `RESULTS.json` summary and supporting execution records.

Depending on the attempt, these include:

```text
RESULTS.json
SHA256SUMS.txt
ERROR.txt

B01/
N01/
B02/
repeat/

keys/

relay/
ingress/
ingress2/
tamper/
verifier1/

relay.json
ingress.json
ingress2.json
tamper.json
verifier1.json

*-stdout.txt
*-stderr.txt
```

The precise file inventory varies by attempt.

### Results and Diagnostics

`RESULTS.json` records the defined checks and their outcomes.

`ERROR.txt` and the standard-output and standard-error records preserve diagnostic information.

A failed result must be interpreted alongside the corresponding diagnostic evidence rather than inferred from the directory name alone.

### Artifact Evidence

The operation directories preserve signed assertions, submission records, and verification responses generated during local testing.

These are local validation artifacts.

They are not the same evidence as the later physical-network scored artifacts.

### Process and Configuration Evidence

The service directories preserve process identities, effective configurations, and recorded request observations.

These records support reconstruction of the local validation environment.

### Integrity Evidence

`SHA256SUMS.txt` provides a hash inventory for the corresponding validation export.

The inventories support independent detection of changes to the recorded files.

They do not independently establish that the application was free from defects.

### Test-Only Keys

Some validation directories include:

```text
keys/
├── TEST_ONLY_private.pem
├── provisioning.json
└── trust.json
```

These files preserve disposable laboratory cryptographic material used during validation.

The private keys are test fixtures.

They must not be reused as operational signing credentials.

## 7. Independent Evidence Review

A reviewer can inspect the historical validation results without executing the application.

### Step 1 — Review All Result Summaries

Inspect the five preserved `RESULTS.json` files.

Confirm the recorded pass/fail counts.

Do not omit the earlier failed attempts.

### Step 2 — Review the Failed Attempts

Inspect the corresponding:

```text
ERROR.txt
*-stdout.txt
*-stderr.txt
```

Determine what each attempt recorded before harness completion failed.

The failed attempts must remain distinguishable from the later successful validation.

### Step 3 — Review the Successful Local Run

Inspect:

```text
20261118T035328Z_c2e46f14/RESULTS.json
```

Confirm:

```text
passed = 12
failed = 0
physical_evidence = false
```

Review the preserved artifacts and service records supporting the individual checks.

### Step 4 — Review the Synthetic Stream Checks

Inspect:

```text
20261118T035639Z_b8352e18/RESULTS.json
```

Confirm:

```text
passed = 6
failed = 0
physical_capture_validated = false
```

### Step 5 — Verify Evidence Integrity

Use the preserved `SHA256SUMS.txt` files to check the corresponding evidence inventories.

### Step 6 — Compare Against Scored Evidence

Compare the local validation behavior with the separately published scored runs:

```text
../evidence/B01_SCORED_20261119_223940/

../evidence/N01_SCORED_20261119_224654/

../evidence/B02_SCORED_20261119_225126/
```

The scored runs contain the primary physical-network evidence.

The validation records provide supporting implementation and development evidence.

## 8. Relationship to MD001 Scored Experiments

| Local validation behavior | Related scored experiment |
|---|---|
| Valid assertion generation and verification | B01 |
| Artifact byte preservation | B01 |
| Modified assertion rejected | N01 |
| Original signature retained during mutation | N01 |
| Fresh verifier process without producer | B02 |
| Original assertion accepted again | B02 |

The local checks were conducted before the scored experiments.

They support readiness to conduct those experiments.

They do not establish the scored outcomes independently.

The scored-run evidence must be reviewed separately.

## 9. Scope and Limitations

The validation evidence establishes that the implementation passed the defined local adapter and synthetic stream checks in the successful recorded runs.

It also establishes that earlier attempts failed to complete.

The successful validation supports:

- Local signed-artifact generation.
- Local artifact transport and verification.
- Rejection of the tested signed-field modification.
- Verification without producer contact under the tested local conditions.
- Selected routing and ingress restrictions.
- Frozen-application integrity checks.
- Rejection of selected malformed HTTP stream conditions.

The validation does not establish:

- Physical-network execution of the scored experiments.
- Validation of physical packet captures.
- Prevention of replay or duplicate execution.
- Durable single-use authority consumption.
- Physical execution enforcement.
- Resistance to signing-key compromise.
- Correct behavior under arbitrary network failures.
- Security against arbitrary host or verifier compromise.

The local adapter results explicitly record:

```text
physical_evidence = false
```

The synthetic stream result explicitly records:

```text
physical_capture_validated = false
```

These limitations are part of the evidence and must remain visible.

## 10. Conclusion

The MD001 validation history contains three unsuccessful local adapter attempts followed by a successful 12-check local validation and a successful six-check synthetic stream validation.

The final successful results establish that the implementation satisfied the defined local test conditions.

The earlier failures remain preserved.

The validation evidence supports the implementation's readiness for the separately recorded MD001 physical-network experiments.

It does not replace their scored evidence.
