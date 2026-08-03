# NUVL Edge Laboratory

This directory contains the physical edge-validation work for NUVL and related provider-controlled bounded-authority mechanisms.

The laboratory uses ESP32-S3 endpoints, a Raspberry Pi verification boundary, local wireless networks, and a Windows control host to test:

- Provider-bound request validation
- Three-endpoint fleet coordination
- Per-device identity and result binding
- Mixed accept and deny outcomes
- Fail-closed behavior during boundary unavailability
- Bounded disconnected authority
- Replay rejection across restart and power loss
- Concurrent double-spend resistance
- Commit-before-accept crash behavior
- Recovery from interrupted persistent-state replacement

This is a curated reproduction package. It is not a dump of the original `esp32-main` working directory.

Only identified test source, required endpoint configuration, selected evidence, and documentation belong here.

## Scope

This laboratory is intended to show:

1. What was built
2. Which files were used
3. How each test was executed
4. What result constituted PASS
5. What was actually observed
6. Which limitations, anomalies, and failed approaches remain relevant

It is not:

- A production deployment guide
- A certification
- A claim that every network or hardware combination will produce identical timing
- A publication of every development file
- A publication of private key material or generated runtime state
- A representation that every embodiment described in related whitepapers or patent filings is implemented here

## Publication Boundary

The public repository should contain only material needed to reproduce or evaluate a documented result.

Suitable public material includes:

- Endpoint firmware
- Fleet coordinators and launchers
- Test clients
- Sanitized configuration examples
- Boundary interface descriptions
- Test procedures
- PASS criteria
- Curated logs and hashes
- Limitations, anomalies, and failed-test records

Some verification-boundary implementations may expose persistence ordering, crash-window handling, atomic-state replacement, or other mechanism-level details relevant to pending or future intellectual-property claims.

Those files should remain withheld until their release is an explicit publication and intellectual-property decision.

Withholding a verification-boundary implementation does not prevent publication of:

- The client sequence
- The boundary interface
- Expected requests and responses
- Failure-injection procedures
- PASS criteria
- Observed results
- Evidence files
- File hashes
- Known limitations

Where a boundary implementation is intentionally withheld, the corresponding test-folder README must state that directly and link back to this section.

The omission of a withheld boundary is intentional and should not be treated as a missing-file error.

A missing source file must not be replaced by a similarly named file without hash or source-history confirmation.

## Laboratory Topology

The primary fleet path is:

```text
Three ESP32-S3 endpoints
        |
        | outbound HTTP polling
        v
Raspberry Pi fleet coordinator
        |
        | assigned mode and relative wait_ms
        v
ESP32-S3 request generation
        |
        | POST /nuvl
        v
Raspberry Pi verification boundary
        |
        | provider-bound decision
        v
ESP32-S3 result report
        |
        v
Fleet launcher validates identity, IP, decision, reason, and timing
```

Primary ports:

```text
8089  NUVL verification boundary
19052 Fleet coordinator
```

The original Raspberry Pi boundary uses Python `HTTPServer` and is single-threaded.

The fleet demonstrations establish coordinated fan-in through one shared boundary. They do not claim parallel execution inside that boundary.

## Repository Layout

Create only the folders being populated.

Empty placeholder directories are not required.

```text
labs/nuvl-edge/
├── README.md
├── .gitignore
│
├── fleet/
│   ├── README.md
│   │
│   ├── baseline/
│   │   ├── README.md
│   │   ├── boundary/
│   │   ├── coordinator/
│   │   ├── firmware/
│   │   ├── launchers/
│   │   └── endpoint-config/
│   │
│   └── archer-validation/
│       └── README.md
│
├── disconnected-authority/
│   ├── README.md
│   ├── poc003-single-use/
│   ├── poc004b-power-loss/
│   ├── poc005-double-spend/
│   ├── poc006a-commit-before-accept/
│   └── wp2-t1-pre-replace/
│
└── evidence/
    ├── README.md
    └── SHA256SUMS.txt
```

The original POC004 process-restart test may be added later after the exact boundary version is tied to the recorded run.

## Release Status

| Test | Repository folder | Result | Public-release status | Main property |
|---|---|---|---|---|
| Fleet three-endpoint baseline | `fleet/baseline/` | PASS | Release candidate | Correct endpoint identity and result binding |
| Fleet mixed outcomes | `fleet/baseline/` | PASS | Release candidate | Different outcomes remained bound to the correct devices |
| Single-endpoint diagnostic | `fleet/baseline/` | PASS | Release candidate after configuration cleanup | Individual board, Wi-Fi, and boundary-path reachability |
| Single-endpoint isolation | `fleet/archer-validation/` | PASS | Hold for later release | One unavailable endpoint did not corrupt the other results |
| Single-endpoint restoration | `fleet/archer-validation/` | PASS | Hold for later release | The isolated endpoint resumed participation |
| Shared-boundary outage | `fleet/archer-validation/` | PASS | Hold for later release | All endpoints failed unavailable with zero accepted action |
| Shared-boundary recovery | `fleet/archer-validation/` | PASS with anomaly | Hold for later release | Services recovered; one endpoint required reset for timely participation |
| POC003 | `disconnected-authority/poc003-single-use/` | PASS | Release after provider-version check | Bounded disconnected single use |
| POC004 | Not yet assigned | PASS | Hold pending exact-version confirmation | Replay state survived process restart |
| POC004B | `disconnected-authority/poc004b-power-loss/` | PASS | Clients and evidence releasable; boundary pending publication decision | Completed commit survived abrupt Raspberry Pi power loss |
| POC005 | `disconnected-authority/poc005-double-spend/` | PASS | Clients and evidence releasable; boundary pending publication decision | Competing attempts produced exactly one acceptance |
| POC006A | `disconnected-authority/poc006a-commit-before-accept/` | PASS | Clients and evidence releasable; boundary pending publication decision | Crash after commit and before response remained replay-denied |
| WP2-T1 | `disconnected-authority/wp2-t1-pre-replace/` | PASS | Clients and evidence releasable; boundary pending publication decision | Crash before atomic replacement did not falsely consume the artifact |

## Original Fleet Baseline

The original pre-latency-investigation fleet implementation consists of:

```text
nuvl_local_hardened.py
multi_endpoint_coordinator_v2.py
esp32_multi_poll_main_v2.py
esp32_multi_once.py
run_three_esp32_poll.py
run_three_esp32_mixed.py
```

Each physical ESP32 contains:

```text
main.py
device_id.txt
```

`main.py` is the deployed copy of the applicable ESP32 firmware.

Confirmed endpoint identities:

```text
esp32-field-01
esp32-s3-02
esp32-s3-03
```

Store the public identity examples as:

```text
fleet/baseline/endpoint-config/
├── esp32-field-01/
│   └── device_id.txt
├── esp32-s3-02/
│   └── device_id.txt
└── esp32-s3-03/
    └── device_id.txt
```

Each `device_id.txt` file contains only its corresponding endpoint identity.

COM port assignments are bench-specific and are not durable endpoint identities.

### Baseline File Placement

```text
fleet/baseline/
├── README.md
├── boundary/
│   └── nuvl_local_hardened.py
├── coordinator/
│   └── multi_endpoint_coordinator_v2.py
├── firmware/
│   ├── esp32_multi_poll_main_v2.py
│   └── esp32_multi_once.py
├── launchers/
│   ├── run_three_esp32_poll.py
│   └── run_three_esp32_mixed.py
└── endpoint-config/
    ├── esp32-field-01/device_id.txt
    ├── esp32-s3-02/device_id.txt
    └── esp32-s3-03/device_id.txt
```

## Original Fleet Tests

### Three-Endpoint Accepted Baseline

Launcher:

```text
run_three_esp32_poll.py
```

Expected result:

```text
esp32-field-01 -> accepted / provider_admissible
esp32-s3-02    -> accepted / provider_admissible
esp32-s3-03    -> accepted / provider_admissible
```

Recorded successful run:

```text
run_id=18c565fc0e9dfd5c
responses=3/3
accepted=3
identity_or_ip_mismatch=0
elapsed=33–34 ms
result=PASS
```

This test verifies:

- Three physical endpoint responses
- Correct endpoint identity
- Correct endpoint IP binding
- Three accepted outcomes
- No missing results
- No cross-assigned results

### Three-Endpoint Mixed Outcomes

Launcher:

```text
run_three_esp32_mixed.py
```

Expected binding:

```text
esp32-field-01 -> accepted / provider_admissible
esp32-s3-02    -> denied / unauthorized_request
esp32-s3-03    -> denied / stale_replay_malformed
```

Recorded successful run:

```text
run_id=18c5b11e874cd4cc
responses=3/3
accepted=1
denied=2
identity_or_ip_mismatch=0
elapsed=29–38 ms
result=PASS
```

This is the stronger original fleet test because aggregate counts alone cannot earn PASS.

Each expected decision and reason must remain bound to the correct physical endpoint.

### Harness-Oracle Failure Preserved

An earlier mixed-outcome run produced the correct system outcomes but was marked FAIL by an all-accept launcher oracle:

```text
run_id=18c5b0a38b1d51b0
system outcomes=correct
launcher result=FAIL
cause=all-accept PASS oracle
classification=harness/oracle failure
```

This record should be retained as evidence that the test harness itself was challenged and corrected.

## Archer Validation

The later Archer validation branch contains environment-specific stage-timing, isolation, outage, and recovery variants.

Known files include:

```text
nuvl_local_hardened_latency.py
esp32_multi_poll_main_v2_pm_none_stage_v2_archer.py
esp32_multi_poll_main_v2_pm_none_stage_v2_archer_isolate_com9.py
run_three_esp32_poll_archer.py
run_three_esp32_mixed_archer.py
run_three_esp32_poll_isolate_com9_archer.py
run_three_esp32_poll_shared_boundary_outage_archer.py
```

These files are not the original fleet baseline.

The `COM9` designation records the bench mapping used during the test. It is not a durable endpoint identity and should be explained before that package is released.

### Archer-Era Results

- Three-endpoint baseline: PASS
- Mixed per-device outcomes: PASS
- Single-endpoint isolation: PASS
- Single-endpoint restoration: PASS
- Shared-boundary outage: PASS
- Shared-boundary recovery: PASS with anomaly

The recovery anomaly was that one endpoint required reset before timely participation resumed.

This should not be omitted from the public record.

## POC003 — Bounded Disconnected Single Use

Proposed folder:

```text
disconnected-authority/poc003-single-use/
```

Known files:

```text
poc003_pi_boundary_housewifi.py
poc003_esp32_prepare_housewifi.py
poc003_esp32_spend_v2_housewifi.py
```

Two provider candidates exist:

```text
poc003_ed25519_provider.py
poc003_ed25519_provider_1h.py
```

Only the provider version tied to the recorded house-network test should be released as the canonical reproduction file.

The tested matrix includes:

- Valid bounded offline exercise
- Replay rejection
- Context mismatch
- Action mismatch
- Nonce mismatch
- Device mismatch
- Tampering
- Unsigned material
- Expired material
- Missing artifact

Best last-known end-to-end client:

```text
poc003_esp32_spend_v2_housewifi.py
```

## POC004 — Persistent Replay Rejection

Known files:

```text
poc004_pi_boundary_persistent.py
poc004_pi_boundary_persistent_archer.py
poc004_esp32_spend_before_restart.py
poc004_esp32_replay_after_restart.py
```

This test demonstrated that replay state survived process restart.

The original and Archer boundary variants must not be mixed without identifying which boundary belongs to the recorded run.

Until that version mapping is resolved, POC004 should remain documented but should not be presented as a complete public reproduction package.

## POC004B — Abrupt Power-Loss Persistence

Proposed folder:

```text
disconnected-authority/poc004b-power-loss/
```

Known files:

```text
poc004b_pi_boundary_powercycle_archer.py
poc004b_prepare_powercycle_artifact_archer.py
poc004b_initial_spend_archer.py
poc004b_replay_after_powerloss_archer.py
```

Main property:

> A completed persistent-state commit remained effective after abrupt Raspberry Pi power loss.

Curated evidence:

```text
poc004b_archer_evidence_20260730_225507.log
post_powercycle_fleet_restoration_20260730_231251.log
poc004b_local_manifest_20260731_232149.txt
```

Known evidence hashes:

```text
poc004b_archer_evidence_20260730_225507.log
9E60FF57BA28E53E081E768C04B298053B5653A505DF76F78D3F9D20837F73F1

post_powercycle_fleet_restoration_20260730_231251.log
0087276A01D749938D92A3FF8EB059EA28F0017A4EEB8586C7BD95564F6A91A8

poc004b_local_manifest_20260731_232149.txt
14D17FA75B08240BFCF38EC2430EDFDEEA8AD3E4CB941926661C2595116EC8C1
```

The restoration sequence eventually returned the three-endpoint fleet to normal operation.

One endpoint required reset before timely participation resumed.

The public-release decision for `poc004b_pi_boundary_powercycle_archer.py` should be made separately from the client and evidence release.

## POC005 — Concurrent Double-Spend

Proposed folder:

```text
disconnected-authority/poc005-double-spend/
```

Known files:

```text
poc005_pi_boundary_persistent_archer.py
poc005_prepare_race.py
poc005_concurrent_double_spend.py
```

Main property:

> Overlapping attempts produced exactly one successful exercise and no duplicate acceptance.

This test does not claim mathematically simultaneous execution.

It demonstrates single-use enforcement under near-concurrent competing attempts.

The public-release decision for `poc005_pi_boundary_persistent_archer.py` should be made separately from the preparation client, race client, and evidence.

## POC006A — Commit Before Accept

Proposed folder:

```text
disconnected-authority/poc006a-commit-before-accept/
```

Known files:

```text
poc006_crash_window_boundary_archer.py
poc006_prepare_crash_artifact_archer.py
poc006_crash_spend_archer.py
poc006_replay_after_crash_archer.py
```

Main property:

> A crash after persistent commit but before response did not permit the artifact to be accepted again.

The public-release decision for `poc006_crash_window_boundary_archer.py` should be made separately from the preparation, crash-spend, replay clients, and evidence.

## WP2-T1 — Crash Before Atomic Replacement

Proposed folder:

```text
disconnected-authority/wp2-t1-pre-replace/
```

Known files:

```text
wp2_t1_pre_replace_boundary_archer.py
wp2_t1_prepare_temp_fsync_artifact_archer.py
wp2_t1_crash_spend_archer.py
wp2_t1_retry_commit_after_restart_archer.py
wp2_t1_replay_check_archer.py
```

The tested boundary was confirmed by SHA-256:

```text
wp2_t1_pre_replace_boundary_archer.py
87351DBDF539E0E44480B28B205AE04FAD796D9C60DA9C4084FDEFDA49A9BFC8
```

Do not substitute:

```text
wp2_t1_temp_fsync_boundary_archer.py
```

That similarly named file has different contents and was not the tested boundary.

Main property:

> A crash before atomic replacement did not falsely consume the artifact. The interrupted commit could be retried after restart, after which replay remained denied.

Curated final evidence:

```text
wp2_t1_final_evidence_20260801_010225.log
```

Known final-evidence details:

```text
Size: 5,374 bytes
SHA-256: 5BB1053A0AF88831F59D8D346D524F10F1E432C5B6D7A3A2A2342312120BBF20
```

The smaller phase logs should not be listed by placeholder name.

Add them only after their exact filenames, sizes, and hashes are captured.

The public-release decision for `wp2_t1_pre_replace_boundary_archer.py` should be made separately from the preparation, crash-spend, retry, replay clients, and evidence.

## Intentionally Withheld Boundary Notice

The READMEs for the following folders must contain an explicit withheld-boundary notice:

```text
disconnected-authority/poc004b-power-loss/
disconnected-authority/poc005-double-spend/
disconnected-authority/poc006a-commit-before-accept/
disconnected-authority/wp2-t1-pre-replace/
```

Use this wording:

> The verification-boundary implementation used for this test is intentionally not included in the current public release.
>
> The public package includes the available client sequence, boundary interface, expected requests and responses, failure-injection procedure, PASS criteria, observed results, evidence, and hashes needed to evaluate the documented behavior.
>
> This is an intentional publication-boundary decision, not a missing-file error.
>
> See the Publication Boundary section in the NUVL Edge Laboratory README.

## Network Configuration

Published source copies should not contain an active credential.

Replace bench-specific values with clear placeholders before release:

```python
SSID = "YOUR_WIFI_SSID"
PASSWORD = "YOUR_WIFI_PASSWORD"
PI_IP = "YOUR_PI_IP"
```

The original test environment used:

```text
SSID: GL-MT300N-V2-94f
Pi address: 192.168.8.234
```

The password present in the original bench files was the Mango factory-default value used during testing.

The test unit was later reconfigured.

A sanitized public source file is not byte-identical to the original tested source.

Documentation must distinguish:

- Original tested source
- Sanitized public derivative
- Rerun-confirmed public source

Do not attach an original tested hash to a modified public copy.

Each sanitized derivative must receive its own SHA-256 at publication.

Record the derivative hash in `SHA256SUMS.txt` and label the file as a sanitized derivative rather than the original tested source.

Example:

```text
# Sanitized public derivative — not byte-identical to tested source
<sha256>  fleet/baseline/firmware/esp32_multi_poll_main_v2.py
```

This allows the published tree to be verified independently without confusing the derivative hash with the historical tested-source hash.

Changing credentials, addresses, persistence paths, timing parameters, or source structure creates a new source version.

Rerun the affected test before claiming that the modified public copy reproduces the historical result.

## Evidence Policy

Publish curated evidence, not every terminal capture.

Evidence should be included only when it materially supports a documented claim.

For each published evidence file, record:

- Filename
- Test identifier
- Date
- File size
- SHA-256
- Relevant source files
- Expected outcome
- Observed outcome
- Any anomaly or setup incident

Generated artifact files, runtime spent-state files, crash markers, private keys, and temporary files are not source evidence and should not be placed in the main public tree by default.

Provider-signed artifact packages are not private keys, but they are generated, test-bound fixtures.

Preserve them with the private evidence bundle unless a sanitized fixture is deliberately selected for publication.

## Reproduction Standard

Every supported test-folder README should contain:

1. Purpose
2. Architecture or invariant tested
3. Exact public files used
4. Any required withheld component or interface substitute
5. Topology and ports
6. Preconditions
7. Configuration changes required
8. Exact execution sequence
9. Expected outcome
10. Observed outcome
11. PASS criteria
12. Limitations
13. Known failures or setup incidents
14. Evidence filenames and SHA-256 values

Test-specific READMEs should link back to this file rather than repeating the full laboratory description.

## Known Development Failures

The following failed or superseded approaches informed the supported implementation:

- Concurrent Windows `mpremote` control was unreliable across three serial ports.
- Improved subprocess capture did not correct the concurrent serial-control failure.
- Inbound UDP triggering was unreliable through the tested access-point path.
- The original coordinator exchanged an incompatible absolute timestamp between Raspberry Pi Python and MicroPython.
- Relative `wait_ms` coordination corrected the cross-epoch timing defect.
- An early mixed-outcome launcher used an all-accept PASS oracle and incorrectly reported FAIL despite correct system outcomes.
- The corrected mixed launcher requires per-device identity, decision, and reason matching.

These failures may be documented without publishing every superseded script.

## Latency Incident

A later synchronized latency event was isolated through controlled comparison between the Mango path and house Wi-Fi.

Disposition:

- The incident is closed at the fault-domain level.
- The access-point-specific wireless path was isolated.
- The exact internal Mango mechanism remains unresolved.
- Do not attribute the behavior to a specific driver function or hardware defect without further evidence.
- The degraded Mango event is engineering incident evidence, not the normal NUVL product baseline.

The house-Wi-Fi A/B comparison completed:

```text
13/13 runs PASS
39/39 endpoint transactions correct
33–147 ms observed endpoint latency
approximately 49.9 ms mean
41.5 ms median
zero reproduction of the synchronized approximately 900 ms event
```

## Not Yet Tested

The following items remain open and should not be inferred from the PASS results above:

- Additional persistence crash points outside the POC006A and WP2-T1 windows
- Startup behavior with corrupt, truncated, or structurally invalid persistent spent-state
- Recovery behavior when persistent-state corruption is detected
- Cross-process or multi-boundary contention beyond the tested in-process serialization path
- Long-duration repeated power-cycle campaigns
- Independent reproduction by an external laboratory
- Generalization of observed latency to other access points, firmware versions, or radio environments

This section should be updated as new tests are completed.

## Release Rules

A file belongs in this public laboratory tree only when one or more of the following are true:

- It is required for a supported reproduction path.
- It is the exact source used in a documented successful test.
- It is a sanitized derivative clearly labeled as such.
- It is curated evidence supporting a specific claim.
- It documents a material limitation, anomaly, or corrective action.
- Its publication has passed any required intellectual-property review.

A file does not belong here merely because it exists in the original working directory.

The original `esp32-main` folder should remain untouched and should not be treated as the public release tree.

## Initial Publishing Order

1. Root README and `.gitignore`
2. Original fleet baseline
3. Fleet README
4. Endpoint identity examples
5. POC003 after selecting the correct provider version
6. POC004B clients, interface documentation, and curated evidence
7. POC005 clients, interface documentation, and curated evidence
8. POC006A clients, interface documentation, and curated evidence
9. WP2-T1 clients, interface documentation, and curated evidence
10. Verification-boundary implementations only after a separate, explicit publication and intellectual-property decision
11. Archer fleet validation after environment-specific setup is documented
12. Remaining evidence only when it materially supports a published claim
