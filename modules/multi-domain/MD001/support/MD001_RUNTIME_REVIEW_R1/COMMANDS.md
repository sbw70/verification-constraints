# Revised deployment commands for review

Nothing here has been run remotely. Existing deployment approval is acknowledged;
this request authorizes preparation only. Accept REVIEW.md's explicit system-runtime
exception before launching application services. requirements.txt remains unchanged.
Do not use the failed .venv, delete it, activate it, run ensurepip/APT/pip, or change DNS.

## Transfer and validate, one host at a time

Run from OmniBook PowerShell in the Multi Provider workspace. Supply the already
known SSH usernames through prompts; no host/path/network guesses are necessary.
These are native OpenSSH commands wrapped by the supplied, reviewable PS1.
Stage preserves Dell's existing extracted application, transfers the original app
archive only to Pi/HP, and installs no dependencies. It stages the separate review
probe into a new sibling directory on all three hosts. Refusal on existing files is
intentional: investigate/preserve them instead of overwriting or deleting them.

```powershell
$DellUser = Read-Host 'Dell SSH username'
$PiUser = Read-Host 'Pi SSH username'
$HpUser = Read-Host 'HP SSH username'
& .\MD001_RUNTIME_REVIEW_R1\PROPOSED_COMMANDS.ps1 -Profile dell -RemoteUser $DellUser -Action Stage
& .\MD001_RUNTIME_REVIEW_R1\PROPOSED_COMMANDS.ps1 -Profile dell -RemoteUser $DellUser -Action Validate
# Review Dell report and package identity before continuing.
& .\MD001_RUNTIME_REVIEW_R1\PROPOSED_COMMANDS.ps1 -Profile pi -RemoteUser $PiUser -Action Stage
& .\MD001_RUNTIME_REVIEW_R1\PROPOSED_COMMANDS.ps1 -Profile pi -RemoteUser $PiUser -Action Validate
& .\MD001_RUNTIME_REVIEW_R1\PROPOSED_COMMANDS.ps1 -Profile hp -RemoteUser $HpUser -Action Stage
& .\MD001_RUNTIME_REVIEW_R1\PROPOSED_COMMANDS.ps1 -Profile hp -RemoteUser $HpUser -Action Validate
```

Each Validate invocation performs only non-scored local cryptographic/parsing checks
on that host and writes uniquely identified host_validation evidence under the review
directory. It opens no socket and creates no application service. Expect20 PASS,
0 FAIL per host and PROBE_PASS_NOT_SCORED, with requirement_pin_satisfied=false.
Review dpkg package version/status against the supplied distro revisions as well as
the probe's upstream version. Do not continue on mismatch, failed import or UnsupportedAlgorithm.
The PS1 contains the exact underlying scp, SSH/bash, archive verification and probe
commands. It does not enable services or run artifact submissions. Do not change
PowerShell execution policy as a workaround; use an already approved script mechanism.

To copy retained reports back after reviewing their printed paths, use a fresh local
directory per host, for example from workspace PowerShell:

```powershell
$LocalReports = Join-Path $PWD ('MD001_HOST_REPORTS_' + (Get-Date -Format 'yyyyMMdd_HHmmss'))
New-Item -ItemType Directory -Path $LocalReports -ErrorAction Stop | Out-Null
scp -r "${DellUser}@10.10.10.10:MD001_RUNTIME_REVIEW_R1/host_validation" (Join-Path $LocalReports 'dell')
if ($LASTEXITCODE -ne 0) { throw 'Dell report transfer failed' }
scp -r "${PiUser}@30.30.30.30:MD001_RUNTIME_REVIEW_R1/host_validation" (Join-Path $LocalReports 'pi')
if ($LASTEXITCODE -ne 0) { throw 'Pi report transfer failed' }
scp -r "${HpUser}@40.40.40.40:MD001_RUNTIME_REVIEW_R1/host_validation" (Join-Path $LocalReports 'hp')
if ($LASTEXITCODE -ne 0) { throw 'HP report transfer failed' }
```

## Application provisioning/launch commands, only after all host checks pass

Use separate interactive SSH terminals. These commands are proposed replacements for
the old .venv/bin/python invocation; source/config/evidence conventions are unchanged.
At PowerShell, enter the appropriate host using the existing approved account:

```powershell
ssh "${DellUser}@10.10.10.10"
# In another terminal, with the same username variables defined:
ssh "${PiUser}@30.30.30.30"
ssh "${HpUser}@40.40.40.40"
```

Each following block runs in its specified remote Linux shell, not PowerShell.
On Dell, generate a fresh deployment test key once, only if lab-key does not exist:

```sh
cd "$HOME/MD001_APPLICATION_R1"
umask 077
/usr/bin/python3 -B -E -s md001.py keygen --out lab-key
cat lab-key/provisioning.json
sha256sum lab-key/trust.json
```

Transfer ONLY the public trust through OmniBook; compare the hash/fingerprint out of
band before service launch. Example PowerShell staging uses a new local directory:

```powershell
$TrustStage = Join-Path $PWD ('MD001_TRUST_' + (Get-Date -Format 'yyyyMMdd_HHmmss'))
New-Item -ItemType Directory -Path $TrustStage -ErrorAction Stop | Out-Null
scp "${DellUser}@10.10.10.10:MD001_APPLICATION_R1/lab-key/trust.json" (Join-Path $TrustStage 'trust.json')
if ($LASTEXITCODE -ne 0) { throw 'Public trust retrieval failed' }
Get-FileHash -Algorithm SHA256 (Join-Path $TrustStage 'trust.json')
ssh "${HpUser}@40.40.40.40" 'test ! -e "$HOME/MD001_APPLICATION_R1/trust.json"'
if ($LASTEXITCODE -ne 0) { throw 'HP trust already exists; preserve and review it' }
scp (Join-Path $TrustStage 'trust.json') "${HpUser}@40.40.40.40:MD001_APPLICATION_R1/trust.json"
if ($LASTEXITCODE -ne 0) { throw 'HP public trust transfer failed' }
```

On HP, compare `sha256sum "$HOME/MD001_APPLICATION_R1/trust.json"` with the source
and operator record. Never copy the private signing key to HP or Pi. Synthetic public
probe seed is not the deployment signing key.

HP verifier terminal:

```sh
cd "$HOME/MD001_APPLICATION_R1"
/usr/bin/python3 -B -E -s md001.py serve --config configs/verifier.json --trust trust.json --out "evidence/SYS_PREFLIGHT_verifier_$(date -u +%Y%m%dT%H%M%SZ)_$$"
```

HP separate ingress terminal:

```sh
cd "$HOME/MD001_APPLICATION_R1"
/usr/bin/python3 -B -E -s md001.py serve --config configs/ingress.json --out "evidence/SYS_PREFLIGHT_ingress_$(date -u +%Y%m%dT%H%M%SZ)_$$"
```

Pi relay terminal:

```sh
cd "$HOME/MD001_APPLICATION_R1"
/usr/bin/python3 -B -E -s md001.py serve --config configs/relay.json --out "evidence/SYS_PREFLIGHT_relay_$(date -u +%Y%m%dT%H%M%SZ)_$$"
```

Services remain foreground and require no root/systemd changes. Run commands one at
a time, retain process.json and terminal output, and associate each PID with its
host runtime report. Stop only these processes via Ctrl+C for rollback; preserve
their output directories. Unexpected bind failure may be an existing preflight
listener: inspect it and stop only the operator-identified test process, not arbitrary
services. No assumption is made that ports are free merely because MD001 has not run.

After accepted runtime profiles and service starts, an explicitly non-scored end-to-end
preflight on Dell may use:

```sh
cd "$HOME/MD001_APPLICATION_R1"
/usr/bin/python3 -B -E -s md001.py produce-send --key lab-key/TEST_ONLY_private.pem --host 30.30.30.30 --port 18081 --out "evidence/SYS_NON_SCORED_PREFLIGHT_$(date -u +%Y%m%dT%H%M%SZ)_$$"
```

This operation signs/sends a new non-scored fixture; it is not part of runtime_probe
and has not been executed. Retain actual relay/HP evidence and independent capture
per the unchanged TEST_PLAN. Keep downstream mutation checks labeled non-scored too.
Stop before scored B01/N01/B02. No scored commands, producer power-off, firewall
changes or physical ESP execution are authorized by this review preparation.
