# FLEET-007 — One Noisy Endpoint

## Classification

**Category 1 — NUVL core / no architecture change**

This test exercises the existing five-endpoint NUVL authority path under asymmetric participant load.

No new authority mechanism, trust relationship, execution path, or architectural component was introduced.

## Module / Use Case

Five-endpoint autonomous heterogeneous fleet.

Participant load isolation under disproportionate request generation by one fleet endpoint.

## Objective

Determine whether substantially increased request traffic from one endpoint can degrade, starve, contaminate, or alter expected authorization behavior for the other four fleet participants.

The test specifically evaluates whether:

- the noisy endpoint continues receiving correctly bound authorization results;
- the remaining four endpoints continue autonomous operation;
- authorization outcomes remain correctly associated with endpoint identity;
- physical-effector endpoints continue operating through the normal authority path; and
- asymmetric traffic produces errors, timeouts, unavailable results, duplicate run identifiers, or incorrect authorization outcomes.

## Test Fleet

The five-endpoint fleet consisted of:

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

## Noisy Participant

The selected noisy endpoint was:

```text
esp32-field-01
```

Its normal autonomous schedule was:

```text
base interval: 2000 ms
jitter:        0–750 ms
```

For FLEET-007, only its base interval was changed:

```text
base interval: 250 ms
jitter:        0–750 ms
```

Source change:

```text
"esp32-field-01": 2000,
```

became:

```text
"esp32-field-01": 250,
```

No other source logic was intentionally changed.

The other four endpoints remained on their existing autonomous schedules.

## Firmware Handling

Before modification, the active `main.py` from `esp32-field-01` was copied from the endpoint and preserved.

Pre-test baseline firmware SHA-256:

```text
BE3103D0958AAB49EF325982C02A43CCD702544764526448B9CD77C8F684D954
```

Noisy test firmware SHA-256:

```text
946C995DC8881FCF0E2B0BFFD917024FDAA7643E76B7E5AECDBD75187311855C
```

After completion of the test, the preserved baseline firmware was restored to `esp32-field-01`.

A post-restoration copy of endpoint `main.py` produced the same SHA-256 as the preserved pre-test firmware:

```text
BE3103D0958AAB49EF325982C02A43CCD702544764526448B9CD77C8F684D954
```

This confirmed byte-for-byte restoration of the pre-test firmware.

The tested noisy firmware contained local deployment configuration and is not published in its tested form.

## Test Procedure

1. Confirmed the existing five-endpoint autonomous fleet was operating.
2. Removed only `esp32-field-01` from independent runtime power.
3. Connected `esp32-field-01` to the laptop by USB.
4. Copied the active endpoint `main.py` as a pre-test backup.
5. Changed only the `esp32-field-01` base interval from 2000 ms to 250 ms.
6. Verified the source difference was limited to that interval value.
7. Copied the noisy firmware to the endpoint.
8. Recorded the noisy firmware SHA-256.
9. Returned `esp32-field-01` to independent power.
10. Allowed the modified endpoint to rejoin the autonomous fleet.
11. Established a measured coordinator-log window.
12. Allowed all five endpoints to operate autonomously during the measured window.
13. Froze the exact coordinator log range into a dedicated evidence file.
14. Analyzed the frozen dataset by endpoint.
15. Checked the measured window for errors, timeouts, exceptions, unavailable results, and failure indicators.
16. Restored `esp32-field-01` to the original baseline firmware.
17. Verified restored firmware against the preserved pre-test hash.

## Evidence Window

Measured start:

```text
2026-08-18T22:47:03.891522729-04:00
```

Coordinator start line:

```text
45188
```

Measured end:

```text
2026-08-18T22:50:08.702211736-04:00
```

Coordinator end line:

```text
45520
```

Approximate measured duration:

```text
3 minutes 5 seconds
```

The exact measured coordinator window was frozen into:

```text
FLEET007_NOISY_WINDOW.log
```

## Results

### Dataset Summary

```text
parsed_transactions=330
unique_run_ids=330
duplicate_run_ids=0
```

Fleet outcome totals:

```text
accepted=330
denied=0
other_decisions=0
```

All parsed results were:

```text
decision=accepted
reason=provider_admissible
```

### esp32-field-01

Noisy endpoint.

```text
transactions=215
latency_min_ms=31
latency_mean_ms=37.04
latency_median_ms=36
latency_max_ms=95
over_250_ms=0
over_1000_ms=0
over_3000_ms=0
```

### esp32-s3-02

```text
transactions=49
latency_min_ms=32
latency_mean_ms=36.37
latency_median_ms=36
latency_max_ms=42
over_250_ms=0
over_1000_ms=0
over_3000_ms=0
```

### esp32-s3-03

```text
transactions=32
latency_min_ms=31
latency_mean_ms=53.09
latency_median_ms=38
latency_max_ms=397
over_250_ms=1
over_1000_ms=0
over_3000_ms=0
```

One 397 ms result occurred on `esp32-s3-03`.

The outlier is preserved as part of the evidence.

No claim is made that asymmetric load produced zero latency effect.

### esp32-xiao-servo-01

```text
transactions=19
latency_min_ms=31
latency_mean_ms=33.42
latency_median_ms=33
latency_max_ms=37
over_250_ms=0
over_1000_ms=0
over_3000_ms=0
```

### esp32-xiao-servo-02

```text
transactions=15
latency_min_ms=30
latency_mean_ms=33.53
latency_median_ms=34
latency_max_ms=37
over_250_ms=0
over_1000_ms=0
over_3000_ms=0
```

## Fleet-Level Observation

`esp32-field-01` generated 215 of the 330 measured transactions.

The remaining four endpoints generated 115 transactions combined.

Despite the asymmetric request load:

- all five endpoints continued participating;
- all 330 parsed authorization outcomes were expected;
- no duplicate run IDs were observed;
- no incorrect authorization outcome was observed;
- no error, timeout, exception, unavailable, failed, or fail condition was found in the measured evidence window;
- both physical actuator endpoints continued participating; and
- one 397 ms latency outlier occurred on `esp32-s3-03` and was preserved.

## Result

**PASS**

The five-endpoint fleet maintained expected authorization behavior and continued autonomous operation under the tested asymmetric participant load.

The test supports the statement:

> Under the tested load, disproportionate request traffic generated by one fleet endpoint did not alter expected authorization behavior of the other four fleet participants.

## Supported Claim

FLEET-007 supports a bounded laboratory claim that one endpoint generating substantially more traffic than the other participants did not alter the observed authorization outcomes of the remaining four endpoints during the measured test window.

## What This Test Does Not Establish

This test does not establish:

- arbitrary denial-of-service resistance;
- unlimited request capacity;
- arbitrary fleet scalability;
- deterministic latency;
- tactical-network performance;
- absence of all latency effects from asymmetric traffic;
- isolation against every possible malicious participant behavior; or
- behavior beyond the tested hardware, software, traffic level, and laboratory topology.

The 397 ms latency outlier remains part of the technical record.

## Evidence Files

```text
FLEET007_NOISY_START.txt
FLEET007_NOISY_END.txt
FLEET007_NOISY_WINDOW.log
fleet007_noisy_analyze.py
```

## Evidence SHA-256

### FLEET007_NOISY_START.txt

```text
1981281F69AE20230E379B0E961FB5127BC568358AF9CF1198643B43A443BC93
```

### FLEET007_NOISY_END.txt

```text
F534641D809E97855D7B598F4934E905EB376BF99AFB69C5D107596632A83EAA
```

### FLEET007_NOISY_WINDOW.log

```text
028281A80CA13E4F8D0A442ED5592C33C632DB68B4E5E8F1AA6F94FED9B29BDE
```

### fleet007_noisy_analyze.py

Publication copy:

```text
0D06F4EC73DFF259F31D47BE39A51301718F57C67AA9F8FF96BBC0D273276122
```

The original Pi-side analyzer was preserved before publication sanitization.

Original Pi-side analyzer SHA-256:

```text
90A9113BA0FB0752308CF00D63FBB89E5A0739BFED65B35DD7BDB8E15E69B642
```

The publication analyzer differs only by removal of the machine-specific `/home/seth/` input path.

## Publication Note

The exact noisy endpoint firmware used during the test is not included in the public evidence package because the tested file contained local deployment configuration.

If a sanitized publication derivative is later added under `firmware/`, it must receive its own publication hash and must not reuse the tested-source hash.

## Final Disposition

FLEET-007 is complete.

`esp32-field-01` was restored to its original autonomous baseline firmware after testing, and restoration was verified byte-for-byte by SHA-256.

The five-endpoint fleet was returned to the pre-test operating configuration.
