# NUVL Edge Lab Evidence

This directory contains the curated evidence supporting the test claims documented in the NUVL Edge Lab.

The evidence set is intentionally selective. It is not a complete export of the original development directory, terminal history, generated runtime state, or every experimental run.

Each included file must support a specific documented result and must be identifiable by filename, test, and SHA-256.

## What the Evidence Establishes

The files in this directory support observed behavior from the tested paths, including:

- Correct three-endpoint identity and result binding
- Mixed accepted and denied fleet outcomes
- Replay denial after process restart
- Replay denial after abrupt Raspberry Pi power loss
- Exactly one accepted result under overlapping attempts
- Replay denial after a crash following persistent commit
- Successful retry after a crash before atomic state replacement
- Fleet service recovery after a shared-boundary power cycle
- Documented anomalies, including an endpoint reset required during one restoration sequence

Evidence of a successful test does not establish behavior outside the documented topology, configuration, fault point, or PASS criteria.

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

Additional evidence should be added only after its filename, test association, source version, and SHA-256 have been confirmed.

## Current Evidence Index

| Test | Evidence file | SHA-256 | Purpose |
|---|---|---|---|
| POC004B | [`poc004b_archer_evidence_20260730_225507.log`](poc004b_archer_evidence_20260730_225507.log) | `9E60FF57BA28E53E081E768C04B298053B5653A505DF76F78D3F9D20837F73F1` | Records the abrupt-power-loss persistence sequence and replay result |
| POC004B restoration | [`post_powercycle_fleet_restoration_20260730_231251.log`](post_powercycle_fleet_restoration_20260730_231251.log) | `0087276A01D749938D92A3FF8EB059EA28F0017A4EEB8586C7BD95564F6A91A8` | Records restoration of the fleet after the Raspberry Pi power-cycle test |
| POC004B manifest | [`poc004b_local_manifest_20260731_232149.txt`](poc004b_local_manifest_20260731_232149.txt) | `14D17FA75B08240BFCF38EC2430EDFDEEA8AD3E4CB941926661C2595116EC8C1` | Records the local evidence manifest associated with the POC004B package |
| WP2-T1 | [`wp2_t1_final_evidence_20260801_010225.log`](wp2_t1_final_evidence_20260801_010225.log) | `5BB1053A0AF88831F59D8D346D524F10F1E432C5B6D7A3A2A2342312120BBF20` | Records the pre-replacement crash, retry, successful commit, and final replay denial |

Known WP2-T1 evidence size:

```text
wp2_t1_final_evidence_20260801_010225.log
5,374 bytes
```

The smaller WP2-T1 phase logs are not listed until their exact filenames, sizes, and hashes are captured.

## POC004B Evidence

POC004B tested whether a completed persistent spent-state commit remained effective after abrupt Raspberry Pi power loss.

The relevant evidence files are:

```text
poc004b_archer_evidence_20260730_225507.log
post_powercycle_fleet_restoration_20260730_231251.log
poc004b_local_manifest_20260731_232149.txt
```

The tested sequence was:

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

Observed property:

> A completed persistent-state commit remained effective after abrupt Raspberry Pi power loss.

The restoration evidence also records an operational anomaly:

> The shared boundary and coordinator recovered, and the three-endpoint fleet eventually returned to normal operation. One endpoint required reset before timely participation resumed.

The anomaly does not invalidate the persistent replay result. It remains relevant to recovery behavior and is retained rather than omitted.

## WP2-T1 Evidence

WP2-T1 tested the persistence window before atomic state replacement.

The tested sequence was:

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

Observed property:

> A crash before atomic replacement did not falsely consume the artifact. The interrupted commit could be retried after restart, after which replay remained denied.

The tested verification boundary was:

```text
wp2_t1_pre_replace_boundary_archer.py
```

Confirmed source SHA-256:

```text
87351DBDF539E0E44480B28B205AE04FAD796D9C60DA9C4084FDEFDA49A9BFC8
```

Do not substitute:

```text
wp2_t1_temp_fsync_boundary_archer.py
```

That similarly named file has different contents and was not the tested boundary.

## Evidence Integrity

SHA-256 is used to identify the exact bytes of each published evidence file.

The canonical repository hash list is:

```text
SHA256SUMS.txt
```

A hash confirms file identity. It does not independently prove that the contents are truthful, complete, or produced under the stated conditions.

Evidence credibility depends on the combined record:

- Exact filename
- SHA-256
- Test identifier
- Source version
- Test procedure
- Expected outcome
- Observed outcome
- PASS criteria
- Known anomaly or setup incident
- Consistency with related logs and manifests

## Verify on Windows

From the `evidence` directory in PowerShell:

```powershell
Get-FileHash .\poc004b_archer_evidence_20260730_225507.log -Algorithm SHA256
Get-FileHash .\post_powercycle_fleet_restoration_20260730_231251.log -Algorithm SHA256
Get-FileHash .\poc004b_local_manifest_20260731_232149.txt -Algorithm SHA256
Get-FileHash .\wp2_t1_final_evidence_20260801_010225.log -Algorithm SHA256
```

To hash every file in the directory:

```powershell
Get-ChildItem -File |
    Where-Object { $_.Name -notin @("README.md", "SHA256SUMS.txt") } |
    Get-FileHash -Algorithm SHA256 |
    Sort-Object Path
```

Compare the returned values with `SHA256SUMS.txt`.

## Verify on Linux or Raspberry Pi

From the `evidence` directory:

```bash
sha256sum -c SHA256SUMS.txt
```

To calculate one file directly:

```bash
sha256sum wp2_t1_final_evidence_20260801_010225.log
```

A successful verification reports:

```text
filename: OK
```

## Source and Evidence Classes

Files in the repository are distinguished by their relationship to the original test.

### Original tested source

The exact source file used during the recorded test.

### Sanitized public derivative

A modified copy with credentials, private values, or environment-specific configuration removed.

### Rerun-confirmed public source

A sanitized or reorganized source file that was executed again and confirmed against its documented PASS criteria.

### Original evidence

An unmodified log, manifest, or capture produced during or immediately after a recorded test.

### Sanitized evidence derivative

A copy modified to remove information not required to evaluate the result.

A sanitized derivative must receive a new SHA-256. It must not reuse the hash of the original file.

Entries in `SHA256SUMS.txt` should identify sanitized derivatives explicitly.

Example:

```text
# Sanitized evidence derivative — not byte-identical to original evidence
<sha256>  sanitized_example.log
```

## Evidence Chain Rules

For every new evidence file:

1. Preserve the original file separately.
2. Do not edit the original in place.
3. Calculate its SHA-256 before making a sanitized copy.
4. Create a separately named derivative when redaction is required.
5. Calculate a new SHA-256 for the derivative.
6. Record the test identifier and relevant source files.
7. Record the expected and observed outcomes.
8. Record anomalies and setup incidents.
9. Add the public file to `SHA256SUMS.txt`.
10. Link the evidence from the applicable test-folder README.

Do not silently replace a file while keeping the same filename and documentation.

## Evidence Naming

Evidence filenames should identify:

- Test or work-package identifier
- Purpose or phase
- Date
- Time when available

Preferred format:

```text
<test>_<purpose>_YYYYMMDD_HHMMSS.<extension>
```

Examples:

```text
poc004b_archer_evidence_20260730_225507.log
post_powercycle_fleet_restoration_20260730_231251.log
wp2_t1_final_evidence_20260801_010225.log
```

Avoid generic names such as:

```text
output.log
test.txt
results-final.txt
new-log.log
```

## What Is Not Included

The public evidence directory does not include, by default:

```text
private signing keys
provider secret material
active credentials
generated runtime spent-state
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

Generated authority artifacts are not private keys, but they contain test-specific signatures and bindings. They remain outside the public evidence set unless a sanitized fixture is deliberately selected for publication.

## Withheld Boundary Implementations

Some disconnected-authority tests intentionally omit the verification-boundary implementation from the public repository.

In those cases, the evidence may still document:

- Client sequence
- Boundary interface
- Request and response behavior
- Failure-injection point
- Expected outcome
- Observed outcome
- PASS criteria
- Relevant source hashes
- Known limitations

Evidence of the recorded result is not the same as a complete independent reproduction package.

Each affected test-folder README identifies the withheld component and explains what remains available for evaluation.

See the [Publication Boundary](../README.md#publication-boundary) section in the main NUVL Edge Lab README.

## Fleet Evidence

The original fleet baseline and mixed-outcome runs are currently identified in the fleet documentation by run ID and observed result.

Three-accept baseline:

```text
run_id=18c565fc0e9dfd5c
responses=3/3
accepted=3
identity_or_ip_mismatch=0
elapsed=33–34 ms
result=PASS
```

Mixed-outcome run:

```text
run_id=18c5b11e874cd4cc
responses=3/3
accepted=1
denied=2
identity_or_ip_mismatch=0
elapsed=29–38 ms
result=PASS
```

Harness-oracle failure:

```text
run_id=18c5b0a38b1d51b0
system outcomes=correct
launcher result=FAIL
cause=all-accept PASS oracle
classification=harness/oracle failure
```

Fleet logs should be added to this directory only after the exact evidence files associated with those runs have been identified and hashed.

The run IDs should not be treated as substitutes for the underlying evidence files.

## Limitations

The current public evidence set does not establish:

- Independent external reproduction
- Behavior at persistence crash points not tested
- Correct startup behavior with corrupt persistent state
- Correct recovery from truncated or structurally invalid state
- Cross-process or multi-boundary contention behavior
- Long-duration repeated power-cycle endurance
- General performance across arbitrary access points or radio environments

The evidence supports the documented tests and fault points only.

## Adding Evidence

A new file belongs here only when it materially supports a documented claim.

Before adding it, confirm:

- The exact test it supports
- Whether it is original or sanitized
- Its SHA-256
- Its file size
- Its relevant source version
- Its expected and observed outcomes
- Its PASS or failure classification
- Any anomaly that affects interpretation

Do not add a file merely because it exists in the original working directory.
