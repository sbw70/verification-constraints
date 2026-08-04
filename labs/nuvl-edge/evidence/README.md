# NUVL Edge Lab Evidence

This directory contains selected evidence from the NUVL Edge Lab test campaign.

The evidence supports specific results documented elsewhere in the repository, including:

- Three-endpoint identity and result binding
- Mixed accepted and denied fleet outcomes
- Replay denial after process restart
- Replay denial after abrupt Raspberry Pi power loss
- Exactly one accepted result under overlapping attempts
- Replay denial after a crash following persistent commit
- Successful retry after a crash before atomic state replacement
- Fleet recovery after a shared-boundary power cycle
- Documented recovery anomalies

The evidence set is intentionally curated. It is not a complete copy of the original development directory, terminal history, generated runtime state, or every experimental run.

A successful test record applies to the documented topology, configuration, fault point, and PASS criteria. It does not establish behavior outside those tested conditions.

## Directory Contents

```text
evidence/
├── README.md
├── SHA256SUMS.txt
├── poc004b_archer_evidence_20260730_225507.log
├── post_powercycle_fleet_restoration_20260730_231251.log
├── poc004b_local_manifest_20260731_232149.txt
└── wp2_t1_final_evidence_20260801_010225.log
```

## Evidence Index

| Test | Evidence file | Purpose |
|---|---|---|
| POC004B | [`poc004b_archer_evidence_20260730_225507.log`](poc004b_archer_evidence_20260730_225507.log) | Records the abrupt-power-loss persistence sequence and replay result |
| POC004B recovery | [`post_powercycle_fleet_restoration_20260730_231251.log`](post_powercycle_fleet_restoration_20260730_231251.log) | Records restoration of the Raspberry Pi services and three-endpoint fleet |
| POC004B manifest | [`poc004b_local_manifest_20260731_232149.txt`](poc004b_local_manifest_20260731_232149.txt) | Records the local evidence manifest associated with the POC004B package |
| WP2-T1 | [`wp2_t1_final_evidence_20260801_010225.log`](wp2_t1_final_evidence_20260801_010225.log) | Records the pre-replacement crash, restart, retry, successful commit, and final replay denial |

## Published Evidence Hashes

### POC004B Power-Loss Evidence

```text
File:
poc004b_archer_evidence_20260730_225507.log

SHA-256:
9E60FF57BA28E53E081E768C04B298053B5653A505DF76F78D3F9D20837F73F1
```

### POC004B Fleet-Restoration Evidence

```text
File:
post_powercycle_fleet_restoration_20260730_231251.log

SHA-256:
0087276A01D749938D92A3FF8EB059EA28F0017A4EEB8586C7BD95564F6A91A8
```

### POC004B Local Manifest

```text
File:
poc004b_local_manifest_20260731_232149.txt

SHA-256:
14D17FA75B08240BFCF38EC2430EDFDEEA8AD3E4CB941926661C2595116EC8C1
```

### WP2-T1 Final Evidence

```text
File:
wp2_t1_final_evidence_20260801_010225.log

Size:
5,374 bytes

SHA-256:
5BB1053A0AF88831F59D8D346D524F10F1E432C5B6D7A3A2A2342312120BBF20
```

The same values are listed in:

```text
SHA256SUMS.txt
```

## POC004B — Abrupt Power-Loss Persistence

POC004B tested whether a completed persistent spent-state commit remained effective after abrupt Raspberry Pi power loss.

The test sequence was:

```text
prepare single-use artifact
start persistent verification boundary
perform valid initial spend
confirm acceptance
remove Raspberry Pi power
restore Raspberry Pi power
restart verification boundary
replay the spent artifact
confirm replay denial
restore fleet services
```

Observed result:

> A completed persistent-state commit remained effective after abrupt Raspberry Pi power loss.

The relevant evidence files are:

```text
poc004b_archer_evidence_20260730_225507.log
post_powercycle_fleet_restoration_20260730_231251.log
poc004b_local_manifest_20260731_232149.txt
```

### Recovery Anomaly

The Raspberry Pi verification boundary and coordinator recovered after power restoration.

The three-endpoint fleet eventually returned to normal operation, but one endpoint required reset before timely participation resumed.

The recovery result is therefore recorded as:

```text
PASS with anomaly
```

The endpoint reset does not invalidate the persistent replay result. It remains relevant to operational recovery behavior.

## WP2-T1 — Crash Before Atomic Replacement

WP2-T1 tested the persistence window before atomic replacement of the spent-state file.

The test sequence was:

```text
prepare artifact
begin persistent-state update
write and fsync temporary state
inject crash before atomic replacement
restart verification boundary
retry the interrupted commit
confirm successful completion
attempt replay
confirm replay denial
```

Observed result:

> A crash before atomic replacement did not falsely consume the artifact. The interrupted commit could be retried after restart, after which replay remained denied.

The final evidence file is:

```text
wp2_t1_final_evidence_20260801_010225.log
```

The verification boundary used in the recorded test was:

```text
wp2_t1_pre_replace_boundary_archer.py
```

Confirmed source SHA-256:

```text
87351DBDF539E0E44480B28B205AE04FAD796D9C60DA9C4084FDEFDA49A9BFC8
```

Do not confuse it with:

```text
wp2_t1_temp_fsync_boundary_archer.py
```

That similarly named file has different contents and was not the boundary used in the recorded WP2-T1 test.

## Fleet Run Records

The original fleet baseline and mixed-outcome tests are currently identified by run ID and summarized result.

### Three-Accept Baseline

```text
run_id=18c565fc0e9dfd5c
responses=3/3
accepted=3
identity_or_ip_mismatch=0
elapsed=33–34 ms
result=PASS
```

### Mixed-Outcome Fleet Run

```text
run_id=18c5b11e874cd4cc
responses=3/3
accepted=1
denied=2
identity_or_ip_mismatch=0
elapsed=29–38 ms
result=PASS
```

### Preserved Harness-Oracle Failure

```text
run_id=18c5b0a38b1d51b0
system outcomes=correct
launcher result=FAIL
cause=all-accept PASS oracle
classification=harness/oracle failure
```

The harness-oracle failure is retained because the system produced the expected mixed endpoint results, but the original launcher evaluated them using an incorrect all-accept PASS rule.

The corrected launcher evaluates the expected decision and reason for each endpoint individually.

## What a SHA-256 Establishes

SHA-256 provides a fingerprint of the exact bytes in a file.

When a published file produces the expected SHA-256, it confirms that the file has not changed from the version represented in `SHA256SUMS.txt`.

A matching hash does not independently prove:

- That the test was performed
- That the test conditions were correctly described
- That the log is complete
- That the result applies outside the tested path

The hash identifies the file. The engineering claim depends on the complete record:

- Test description
- Source version
- Execution sequence
- Expected result
- Observed result
- PASS criteria
- Evidence file
- Known anomalies
- Limitations

## Verify on Windows

Open PowerShell in the `evidence` directory.

Verify one file:

```powershell
Get-FileHash .\poc004b_archer_evidence_20260730_225507.log -Algorithm SHA256
```

Verify the current evidence files:

```powershell
Get-FileHash .\poc004b_archer_evidence_20260730_225507.log -Algorithm SHA256
Get-FileHash .\post_powercycle_fleet_restoration_20260730_231251.log -Algorithm SHA256
Get-FileHash .\poc004b_local_manifest_20260731_232149.txt -Algorithm SHA256
Get-FileHash .\wp2_t1_final_evidence_20260801_010225.log -Algorithm SHA256
```

Hash every evidence file except the README and hash list:

```powershell
Get-ChildItem -File |
    Where-Object { $_.Name -notin @("README.md", "SHA256SUMS.txt") } |
    Get-FileHash -Algorithm SHA256 |
    Sort-Object Path
```

Compare the returned values with:

```text
SHA256SUMS.txt
```

## Verify on Linux or Raspberry Pi

From the `evidence` directory:

```bash
sha256sum -c SHA256SUMS.txt
```

A successful verification reports:

```text
filename: OK
```

To calculate one file directly:

```bash
sha256sum wp2_t1_final_evidence_20260801_010225.log
```

## Withheld Verification Boundaries

Some disconnected-authority tests do not include the complete verification-boundary implementation in the public repository.

Those test folders may still include:

- Client sequence
- Boundary interface
- Request and response behavior
- Failure-injection point
- Expected result
- Observed result
- PASS criteria
- Evidence
- Source hashes
- Known limitations

This allows the documented behavior to be evaluated without publishing every mechanism-level implementation detail.

Evidence of a recorded result is not the same as a complete independent reproduction package.

See the [Publication Boundary](../README.md#publication-boundary) section in the main NUVL Edge Lab README.

## Evidence Naming

Evidence filenames identify the test, purpose, and capture time where available.

The general form is:

```text
<test>_<purpose>_YYYYMMDD_HHMMSS.<extension>
```

Examples:

```text
poc004b_archer_evidence_20260730_225507.log
post_powercycle_fleet_restoration_20260730_231251.log
wp2_t1_final_evidence_20260801_010225.log
```

This makes each file easier to associate with the relevant test and phase.

## Excluded Runtime Material

The evidence directory does not include:

```text
private signing keys
provider secret material
active credentials
generated spent-state
temporary commit files
crash markers
PID files
Python cache files
complete shell history
unrelated terminal output
duplicate logs
superseded evidence copies
raw development-directory exports
```

Provider-signed artifacts are not private keys, but they contain test-specific bindings and signatures. They are not required for the current public evidence set.

## Limitations

The current evidence does not establish:

- Independent reproduction by an external laboratory
- Behavior at persistence crash points that were not tested
- Startup behavior with corrupt persistent state
- Recovery from truncated or structurally invalid persistent state
- Cross-process contention
- Multi-boundary contention
- Long-duration repeated power-cycle endurance
- General performance across arbitrary access points
- General performance across arbitrary radio environments

The evidence supports the documented tests and fault-injection points only.
