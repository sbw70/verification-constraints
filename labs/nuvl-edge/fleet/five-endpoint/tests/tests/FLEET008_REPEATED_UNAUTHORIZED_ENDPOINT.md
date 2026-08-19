# FLEET-008 — Repeated Unauthorized Endpoint

## Classification

**Category 1 — NUVL core / no architecture change**

FLEET-008 exercises the existing five-endpoint NUVL authority path while one autonomous participant repeatedly requests an action that the provider-controlled boundary denies.

No new authority mechanism, trust relationship, execution path, coordinator behavior, boundary behavior, or architectural component was introduced.

## Module / Use Case

Five-endpoint autonomous heterogeneous fleet.

Participant authorization isolation under repeated unauthorized activity.

## Objective

Determine whether one fleet endpoint can repeatedly receive an unauthorized result without altering the expected authorization behavior of the other four autonomous fleet participants.

The test evaluates whether:

- one selected endpoint can repeatedly receive `DENY`;
- the remaining four endpoints continue receiving their expected `ACCEPT` outcomes;
- denial remains bound to the requesting endpoint;
- acceptance elsewhere does not leak to the denied endpoint;
- denial on one participant does not become fleet-wide denial;
- all five endpoint identities continue appearing independently;
- duplicate transaction identifiers or cross-assigned results appear;
- the physical-effector endpoints continue receiving their expected authorization results; and
- repeated unauthorized activity produces errors, timeouts, unavailable results, or other shared-fleet failures.

## Test Fleet

The five-endpoint autonomous fleet consisted of:

- `esp32-field-01`
- `esp32-s3-02`
- `esp32-s3-03`
- `esp32-xiao-servo-01`
- `esp32-xiao-servo-02`

Shared infrastructure:

- Raspberry Pi 5 boundary/coordinator
- Archer network
- provider-controlled decision path
- autonomous endpoint-local request schedules

Authority path remained:

```text
endpoint
  ->
network
  ->
NUVL boundary
  ->
provider-controlled decision
  ->
endpoint action
```

## Unauthorized Participant

The selected unauthorized endpoint was:

```text
esp32-field-01
```

The existing autonomous firmware normally uses:

```python
mode = "accept"
```

For FLEET-008, only that value was changed to:

```python
mode = "deny"
```

No other source logic was intentionally changed.

The other four endpoints remained on their existing autonomous firmware and request schedules.

## Provider-Controlled Denial Path

The existing boundary implementation already defined the tested action mapping:

```text
requested_action="accept"
  ->
decision="accepted"
reason="provider_admissible"
```

and:

```text
requested_action="deny"
  ->
decision="denied"
reason="unauthorized_request"
```

FLEET-008 therefore exercised an existing NUVL decision path.

The boundary was not modified to create the test result.

## Firmware Handling

Before FLEET-008, the active baseline firmware for `esp32-field-01` had already been preserved from the endpoint.

Baseline firmware SHA-256:

```text
BE3103D0958AAB49EF325982C02A43CCD702544764526448B9CD77C8F684D954
```

The FLEET-008 test copy differed from that baseline only by:

```text
mode = "accept"
```

changing to:

```text
mode = "deny"
```

FLEET-008 repeated-deny test firmware SHA-256:

```text
A811FA38A6FE7065DD09CE67BBA403AB1987DF9B774BC8E4547CFFB72EDEC5EF
```

After completion of FLEET-008, the preserved baseline firmware was restored to `esp32-field-01`.

A post-restoration copy of endpoint `main.py` produced the same SHA-256 as the preserved baseline:

```text
BE3103D0958AAB49EF325982C02A43CCD702544764526448B9CD77C8F684D954
```

This verified byte-for-byte restoration of the pre-test firmware.

The exact FLEET-008 firmware contains local deployment configuration and is not published in its tested form.

## Test Procedure

1. Confirmed the existing five-endpoint autonomous fleet was operating.
2. Identified the existing provider-controlled unauthorized path:
   - `requested_action="deny"`
   - `decision="denied"`
   - `reason="unauthorized_request"`
3. Created a FLEET-008 endpoint firmware copy from the preserved autonomous baseline.
4. Changed only:
   - `mode = "accept"`
   - to `mode = "deny"`
5. Compared the baseline and test copies and confirmed that this was the only source difference.
6. Recorded the SHA-256 of the exact FLEET-008 test firmware.
7. Removed only `esp32-field-01` from independent runtime power.
8. Connected `esp32-field-01` to the Windows laptop by USB.
9. Copied the FLEET-008 firmware to endpoint `main.py`.
10. Returned `esp32-field-01` to independent power.
11. Allowed the endpoint to rejoin the autonomous fleet.
12. Confirmed live coordinator output showed:
    - repeated `DENY / unauthorized_request` for `esp32-field-01`;
    - continued `ACCEPT / provider_admissible` for the other four endpoints.
13. Established a measured coordinator-log window.
14. Allowed all five endpoints to continue autonomous operation during the measured window.
15. Froze the exact coordinator log range into a dedicated evidence file.
16. Analyzed the frozen dataset by endpoint, decision, reason, and latency.
17. Checked the frozen evidence window for:
    - error
    - timeout
    - traceback
    - exception
    - unavailable
    - failed
    - fail
18. Restored the original baseline firmware to `esp32-field-01`.
19. Copied the restored endpoint `main.py` back to the laptop.
20. Verified the restored file matched the preserved baseline byte-for-byte by SHA-256.
21. Returned `esp32-field-01` to normal independent autonomous operation.

## Evidence Window

Measured start:

```text
2026-08-19T17:41:37.547429707-04:00
```

Coordinator start line:

```text
63001
```

Measured end:

```text
2026-08-19T17:45:08.160715931-04:00
```

Coordinator end line:

```text
63217
```

Approximate measured duration:

```text
3 minutes 31 seconds
```

The exact measured coordinator window was frozen into:

```text
FLEET008_DENY_WINDOW.log
```

## Results

### Dataset Summary

```text
parsed_transactions=216
unique_run_ids=216
duplicate_run_ids=0
```

Fleet outcome totals:

```text
accepted=134
denied=82
other_decisions=0
```

## Per-Endpoint Results

### esp32-field-01

Selected repeatedly unauthorized endpoint.

```text
transactions=82
decisions={'denied': 82}
reasons={'unauthorized_request': 82}

latency_min_ms=30
latency_mean_ms=38.77
latency_median_ms=35.0
latency_max_ms=190

over_250_ms=0
over_1000_ms=0
over_3000_ms=0
```

Observed authorization result:

```text
82 / 82 denied
82 / 82 reason=unauthorized_request
```

No accepted result was observed for the selected unauthorized endpoint during the measured window.

### esp32-s3-02

```text
transactions=58
decisions={'accepted': 58}
reasons={'provider_admissible': 58}

latency_min_ms=31
latency_mean_ms=39.57
latency_median_ms=36.0
latency_max_ms=102

over_250_ms=0
over_1000_ms=0
over_3000_ms=0
```

Observed authorization result:

```text
58 / 58 accepted
58 / 58 reason=provider_admissible
```

### esp32-s3-03

```text
transactions=37
decisions={'accepted': 37}
reasons={'provider_admissible': 37}

latency_min_ms=30
latency_mean_ms=39.84
latency_median_ms=36
latency_max_ms=100

over_250_ms=0
over_1000_ms=0
over_3000_ms=0
```

Observed authorization result:

```text
37 / 37 accepted
37 / 37 reason=provider_admissible
```

### esp32-xiao-servo-01

Physical-effector endpoint.

```text
transactions=22
decisions={'accepted': 22}
reasons={'provider_admissible': 22}

latency_min_ms=29
latency_mean_ms=37.18
latency_median_ms=33.0
latency_max_ms=81

over_250_ms=0
over_1000_ms=0
over_3000_ms=0
```

Observed authorization result:

```text
22 / 22 accepted
22 / 22 reason=provider_admissible
```

### esp32-xiao-servo-02

Physical-effector endpoint.

```text
transactions=17
decisions={'accepted': 17}
reasons={'provider_admissible': 17}

latency_min_ms=30
latency_mean_ms=32.29
latency_median_ms=32
latency_max_ms=35

over_250_ms=0
over_1000_ms=0
over_3000_ms=0
```

Observed authorization result:

```text
17 / 17 accepted
17 / 17 reason=provider_admissible
```

## Fleet-Level Authorization Isolation

During the measured window:

```text
esp32-field-01:
82 denied
0 accepted
```

The remaining four endpoints produced:

```text
134 accepted
0 denied
```

Combined fleet result:

```text
216 total transactions
134 accepted
82 denied
0 other decisions
```

The authorization outcomes remained separated by endpoint.

The repeatedly unauthorized endpoint did not receive an accepted result.

The other four endpoints did not inherit the selected endpoint's denial state.

No cross-assignment or fleet-wide contamination of authorization outcome was observed.

## Transaction Identity

The measured dataset contained:

```text
216 parsed transactions
216 unique run IDs
0 duplicate run IDs
```

No duplicate run identifier was observed in the frozen evidence window.

## Latency

Fleet-wide latency:

```text
minimum=29 ms
mean=38.5 ms
median=35.0 ms
maximum=190 ms
```

Threshold counts:

```text
over_250_ms=0
over_1000_ms=0
over_3000_ms=0
```

No measured transaction exceeded 250 ms.

No sustained latency-degradation condition resembling the previously preserved autonomous-fleet anomaly appeared during this measured FLEET-008 window.

This result is limited to the measured FLEET-008 conditions and does not establish deterministic latency.

## Error / Failure Check

The frozen FLEET-008 evidence window was searched for:

```text
error
timeout
traceback
exception
unavailable
failed
fail
```

The search returned no matches.

No such transport/runtime failure indicator was present in the measured evidence file.

## Physical-Effector Observation Boundary

Both XIAO physical-effector endpoints continued participating and received only:

```text
decision=accepted
reason=provider_admissible
```

during the measured window.

FLEET-008 does not independently establish physical actuation for every accepted transaction because the coordinator evidence records software authorization/result observations rather than an independent physical-command witness.

Physical execution claims therefore remain bounded by the existing actuator-test evidence and its stated limitations.

## Result

**PASS**

FLEET-008 demonstrated repeated endpoint-specific denial while the remaining four autonomous fleet participants continued receiving their expected provider-admissible results through the same shared NUVL authority path.

Observed result:

```text
selected endpoint:
82 / 82 DENY

remaining four endpoints:
134 / 134 ACCEPT

incorrect outcomes:
0

other decisions:
0

duplicate run IDs:
0

transactions over 250 ms:
0
```

## Supported Claim

FLEET-008 supports the bounded laboratory statement:

> Repeated unauthorized activity by one autonomous fleet participant did not alter expected authorization outcomes for the other four tested endpoints.

The test additionally supports the observation that, under the measured conditions:

- denial remained bound to the selected participant;
- acceptance elsewhere did not transfer to the denied participant;
- denial on one participant did not become fleet-wide denial; and
- the four unaffected participants continued autonomous operation through the shared authority path.

## What This Test Does Not Establish

FLEET-008 does not establish:

- arbitrary Byzantine fault tolerance;
- resistance to arbitrary hostile endpoint behavior;
- arbitrary denial-of-service resistance;
- unlimited request capacity;
- arbitrary fleet scalability;
- deterministic latency;
- geographically distributed operation;
- tactical-network performance;
- compromise resistance against the coordinator or boundary;
- isolation against every malformed, stale, replayed, or adversarial request class;
- independent physical confirmation for every actuator command; or
- behavior outside the tested hardware, software, traffic level, and laboratory topology.

Malformed, stale, and replay isolation are separate test conditions.

## Evidence Files

Public evidence set:

```text
FLEET008_DENY_START.txt
FLEET008_DENY_END.txt
FLEET008_DENY_WINDOW.log
fleet008_deny_analyze.py
```

## Evidence SHA-256

### FLEET008_DENY_START.txt

```text
CFBE0F25797B41C175D95991A5BE3586E5C7A2BB75965968088B726B7D463A3F
```

### FLEET008_DENY_END.txt

```text
F8CDCA66D804B8B93B6B9C053A6985FA8F5CB744AC87D630BB2410EA512A12D7
```

### FLEET008_DENY_WINDOW.log

```text
7053378494F00F20E50FBE4D9239016B9F24791455220A8297048B7F4C55078B
```

### fleet008_deny_analyze.py

Sanitized publication copy:

```text
C8869D55E5A38AB6FE62E75ECB3D1D44FFC60D4EDF3475528D5238D7CA905FFF
```

The original Pi-side analyzer was preserved before publication sanitization.

Original Pi-side analyzer SHA-256:

```text
AAE4CCB890EBB3BB4890B57DDF82C80A949038D69DBFDEB3829D814E36226FD1
```

The publication analyzer differs from the preserved Pi-side analyzer only by removal of the machine-specific `/home/seth/` input path.

## Test Firmware SHA-256

Exact repeated-deny test firmware:

```text
A811FA38A6FE7065DD09CE67BBA403AB1987DF9B774BC8E4547CFFB72EDEC5EF
```

Baseline firmware before and after FLEET-008:

```text
BE3103D0958AAB49EF325982C02A43CCD702544764526448B9CD77C8F684D954
```

The matching pre-test and post-restoration baseline hashes confirm that `esp32-field-01` was returned to its original autonomous firmware after testing.

## Publication Note

The exact FLEET-008 endpoint firmware is not included in the public evidence package because the tested source contains local deployment configuration.

If a sanitized repeated-deny firmware derivative is later published under `firmware/`, it must:

- remove local deployment credentials and environment-specific configuration;
- retain the tested authority-path behavior;
- be identified as a sanitized publication derivative; and
- receive its own publication-copy SHA-256.

The exact tested-source hash must not be reused for a modified publication copy.

## Final Disposition

FLEET-008 is complete.

The selected endpoint repeatedly received the expected unauthorized result while the other four autonomous participants continued receiving their expected provider-admissible outcomes.

No incorrect authorization outcome, duplicate run ID, >250 ms transaction, or searched failure indicator was observed in the measured evidence window.

After testing, `esp32-field-01` was restored to the original autonomous baseline firmware and restoration was verified byte-for-byte by SHA-256.

The five-endpoint fleet was returned to the pre-test operating configuration.
