# MP006 R01 operator handoff — REVIEW REQUIRED

This is a staged procedure, not permission to deploy or run. Execute ONE command,
read its actual output, and obtain the next instruction. Never paste a whole section.
Addresses below are LAST KNOWN and must be verified. No Linux host was contacted
while preparing this document. Missing service paths/configurations are unresolved
preconditions, not permission to guess. There is no authorization expiry or required
outage duration. Do not reset, repair, delete, retry a send, or overwrite evidence.

## STOP 1 — before deployment or execution

Review these files, local validation, source hashes, proposed commands, and the
read-only machine inspection results. Only read-only environment inspection may
precede approval; it still requires the operator to authorize Linux contact.
Review the actual Dell startup configuration, relay command/configuration, recorder
command/configuration/log path, machine identities, no unrelated Dell work, and data
preservation. Then obtain explicit deployment/execution approval. Current readiness
flags are false and no live authorization exists.

### Local review on OmniBook (PowerShell)

```powershell
Set-Location -LiteralPath 'C:\Users\holiw\OneDrive\Documents\ChatGPT\Multi Provider\MULTI_PROVIDER_006'
```

Expected: working directory changes. Problem: missing directory; STOP for review.

```powershell
python -B .\mp006.py inspect
```

Expected: LOCAL_INSPECTION_ONLY, correct source hash, readiness false. Any hash,
path or dependency error: PRECONDITION_NOT_MET; STOP. This does not inspect Linux.

```powershell
Get-Content -LiteralPath .\SOURCE_REVIEW.md
```

Expected: source findings and explicit limitations, not a claim of live verification.

### Dell read-only review (Dell local terminal, Bash)

Run these individually only after permission to inspect this machine.

```bash
hostnamectl
```

Expected: operator-recognized Dell/Linux identity. Wrong machine: STOP.

```bash
ip -brief address
```

Expected: actual Dell LAN address, believed 192.168.1.118. Mismatch: STOP; update
reviewed commands/configuration before any traffic or deployment.

```bash
sha256sum /home/seth/MULTI_PROVIDER_005/provider_a/provider_a.py
```

Expected: 79e4994c955ca842af04a8fd650a33d49de040bab95b821ded9e63e16866f2b6.
Missing historical path or mismatch: STOP; do not replace the historical file.

```bash
ps -eo user,pid,ppid,lstart,args --width 300
```

Expected: review all provider, Python, nohup, supervisor, shell and unrelated jobs.
A provider can be named indirectly; a keyword-only search is insufficient.

```bash
sudo ss -ltnp
```

Expected: port owners known; no competing 9090 listener when MP006 begins.
Unknown listener or inability to inspect: STOP. Do not kill anything automatically.

```bash
systemctl list-unit-files --type=service --no-pager
```

Expected: inspect enabled/static/generated services and dependencies for launchers.

```bash
systemctl --user list-unit-files --type=service --no-pager
```

Expected: inspect user startup services; error requires review, not an empty result.

```bash
systemctl list-timers --all --no-pager
```

Expected: inspect delayed startup mechanisms too.

```bash
systemctl --user list-timers --all --no-pager
```

Expected: inspect user timers.

```bash
crontab -l
```

Expected: no provider launcher; "no crontab" is a documented absence, not success
for other accounts or system cron.

```bash
sudo crontab -l
```

Expected: inspect root jobs; no automatic provider launch.

```bash
sudo grep -RInE 'python|provider|MULTI_PROVIDER|mp006|nohup|supervisor|pm2|docker' /etc/systemd/system /etc/cron.d /etc/crontab /etc/rc.local /etc/xdg/autostart /etc/profile /etc/profile.d
```

Expected: review every match and invoked script. Missing paths and access errors
must be recorded; an exit code alone is not proof of absence.

```bash
grep -RInE 'python|provider|MULTI_PROVIDER|mp006|nohup|supervisor|pm2|docker' /home/seth/.config/systemd /home/seth/.config/autostart /home/seth/.profile /home/seth/.bashrc /home/seth/.bash_profile
```

Expected: same review for login/autostart mechanisms. Follow referenced scripts
with individual `cat` commands after observing their actual paths. Inspect other
accounts if the process/service review identifies them. For an identified service,
use `systemctl cat` with its observed exact unit name in the next reviewed command.
These checks are discovery, not an exhaustive proof against arbitrary hidden jobs.
Do not set autostart-reviewed true until the operator understands the launch chain.
Any disable change requires preserved original configuration and separate review.

```bash
python3 -B -c "import sys,cryptography; print(sys.version); print(cryptography.__version__)"
```

Expected: working Python and cryptography. Missing dependency: STOP; no installation
is authorized by this document.

### Pi read-only review (Pi local Bash terminal)

```bash
hostnamectl
```

Expected: recognized Raspberry Pi relay.

```bash
ip -brief address
```

Expected: verified LAN address, believed 192.168.1.100.

```bash
sudo ss -ltnp
```

Expected: identify actual 8080 relay PID; unknown/absent relay: STOP.

```bash
ps -eo user,pid,ppid,args --width 300
```

Expected: identify relay launcher and arguments. Inspect the observed source and
any launcher/configuration in subsequent single commands with exact observed paths.
Its effective Provider A destination must be the verified Dell /ingest endpoint;
Provider B destination must also be understood. Frozen relay defaults contain a
historical B address: source defaults alone do not prove effective configuration.
No Pi deployment or new relay code is proposed. If its actual configuration cannot
be established, STOP 1 remains unresolved. Do not start a guessed relay command.

### OmniBook recorder review (PowerShell)

```powershell
Get-NetIPAddress -AddressFamily IPv4
```

Expected: controller/association address verified, believed 192.168.1.102.

```powershell
Get-NetTCPConnection -State Listen -LocalPort 9191 | Select-Object LocalAddress,LocalPort,OwningProcess
```

Expected: actual recorder PID. Missing/multiple unexpected owners: STOP.

```powershell
Get-CimInstance Win32_Process | Where-Object { $_.CommandLine -match 'association|launch_service|9191' } | Select-Object ProcessId,ExecutablePath,CommandLine | Format-List
```

Expected: inspect actual recorder source, launcher, registry, log, session and
manifest/contract arguments. Confirm source bytes against frozen reference and
registry/trust identities. An indirect launcher requires source/config inspection.

```powershell
Invoke-RestMethod -Uri 'http://192.168.1.102:9191/health'
```

Expected: healthy recorder with understood session identity. Health alone is not
execution evidence or proof of registry configuration. STOP for inconsistencies.

Do not change or append test traffic to frozen MP005 evidence. If the recorder's
current log is MP005 evidence, STOP: review a separate new recorder session using
the unchanged recorder's existing CLI. The exact launch command must be completed
from actual inspection before STOP 1 can be approved. No generic placeholder
launch command is safe to execute here. Keep the reviewed relay and continuous
recorder running through Dell's entire interruption. Provider B stays powered and
unchanged; it is not scored by R01.

## Dependency placement after STOP 1 approval

OmniBook: entire MP006 build, authority preparation, sends through NUVL, recorder,
witness, independent evidence copies, scoring. Dell: byte-identical mp006.py,
configuration, reference/MP005 dependencies (all 48 copied files, including harness
manifest dependencies and laboratory keys), procedure and build manifest. Dell
creates its own state and runtime/evidence folders. Pi: existing verified relay;
no MP006 code. Do not copy Windows state/evidence into Dell's persistent state.

Use final roots in configuration. First ensure the final Windows directory is
absent; do not merge with an old session. The following are PROPOSED, not executed:

```powershell
Test-Path -LiteralPath 'C:\Users\holiw\esp32-main\MULTI_PROVIDER_006'
```

Expected: False. True: STOP for review.

```powershell
Copy-Item -LiteralPath 'C:\Users\holiw\OneDrive\Documents\ChatGPT\Multi Provider\MULTI_PROVIDER_006' -Destination 'C:\Users\holiw\esp32-main\MULTI_PROVIDER_006' -Recurse -ErrorAction Stop
```

Expected: successful copy into absent destination; verify the file inventory there.

```powershell
Set-Location -LiteralPath 'C:\Users\holiw\esp32-main\MULTI_PROVIDER_006'
```

Expected: final Windows workspace. All remaining PowerShell commands assume this cwd.

Before changes, verify the copied build inventory on OmniBook:

```powershell
python -B -c "import mp006 as m; p=m.ROOT; rows=(p/'SHA256SUMS.txt').read_text().splitlines(); assert rows; assert all(m.h.digest((p/line.split('  ',1)[1]).read_bytes())==line.split('  ',1)[0] for line in rows); print('BUILD COPY VERIFIED')"
```

Expected: message. Then, ONLY AFTER STOP 1 approval, review/edit configuration:

```powershell
notepad.exe .\configs\MP006_R01.json
```

Expected: operator reviews verified addresses, unique session, final roots; sets
readiness booleans true only for completed checks and status to
REVIEWED_FOR_OPERATOR_RUN. Save without changing source identity or introducing
time gates. No value is inferred from elapsed preparation time. Close editor.

Create the explicit approved operator authorization, bound to the saved config:

```powershell
python -B -c "import mp006 as m; c=m.configuration(); m.verify(c); assert c['status']=='REVIEWED_FOR_OPERATOR_RUN' and all(c[k] for k in ('addresses_verified','autostart_reviewed_disabled','operator_preflight_complete')); m.h.write(m.ROOT/'authorizations'/(c['session']+'.json'),dict(authorized=True,session=c['session'],config_sha256=m.h.digest((m.ROOT/'configs/MP006_R01.json').read_bytes()),allowed_actions=['initialize','prepare','capture','send','checkpoint','launch','_serve'])); print('APPROVED SESSION AUTHORIZATION WRITTEN')"
```

Expected: exclusive new authorization. This command is permitted only after actual
operator approval; it does not grant physical-power approval. Make a deployment
manifest of the now-reviewed files without changing the historical build manifest:

```powershell
python -B -c "import mp006 as m; m.h.inventory(m.ROOT,'DEPLOYMENT_SHA256SUMS.txt'); print('DEPLOYMENT MANIFEST WRITTEN')"
```

Expected: new manifest. The original SHA256SUMS is build provenance; config changes
after approval are expected only in the deployment manifest. Never substitute an
unreviewed changed config. Existing manifest/authorization: STOP, no overwrite.
For the commands below the approved session is MP006_R01_RUN001 and authorization
is authorizations/MP006_R01_RUN001.json. If session changes, reissue the commands.

```powershell
ssh seth@192.168.1.118 'test ! -e /home/seth/MULTI_PROVIDER_006'
```

Expected: exit 0, no output. Nonzero: STOP; never merge or remove existing work.

```powershell
scp -r 'C:\Users\holiw\esp32-main\MULTI_PROVIDER_006' seth@192.168.1.118:/home/seth/
```

Expected: entire reviewed build copied into the previously absent Dell root. No
Windows state or scored evidence may exist at this deployment stage. Any partial
copy: STOP; preserve it. Do not merge/retry. On Dell:

```bash
python3 -B -c "from pathlib import Path; import hashlib; p=Path('/home/seth/MULTI_PROVIDER_006'); rows=(p/'DEPLOYMENT_SHA256SUMS.txt').read_text().splitlines(); assert rows; assert all(hashlib.sha256((p/line.split('  ',1)[1]).read_bytes()).hexdigest()==line.split('  ',1)[0] for line in rows); print('DEPLOYMENT BYTES VERIFIED')"
```

Expected: message. Compare the manifest itself independently too, via
`Get-FileHash .\DEPLOYMENT_SHA256SUMS.txt -Algorithm SHA256` on OmniBook and
`sha256sum /home/seth/MULTI_PROVIDER_006/DEPLOYMENT_SHA256SUMS.txt` on Dell,
issued separately. Mismatch: HARNESS_ERROR, STOP. Then Dell `mp006.py inspect`
must pass before any state initialization.

## Operating shells and evidence transfer protocol

Dell: open a local terminal (external USB keyboard) and set cwd once:

```bash
cd /home/seth/MULTI_PROVIDER_006
```

OmniBook PowerShell: define each variable in its own command. Keep this shell open.

```powershell
$Case = 'C:\Users\holiw\esp32-main\MULTI_PROVIDER_006\evidence\MP006_R01_RUN001\R01'
```

```powershell
$RemoteCase = '/home/seth/MULTI_PROVIDER_006/evidence/MP006_R01_RUN001/R01'
```

```powershell
$AssociationLog = Read-Host 'Paste the exact reviewed continuous MP006 association log path'
```

Expected: known existing log outside frozen MP005 evidence. Do not guess it.

### Transfer T: Dell evidence to OmniBook, without overwrite

For each capture set `$Label` to the step's literal label (examples below), then
run the following separately, waiting for output after each. This protocol copies
into a fresh receipt directory before promoting to the canonical evidence path.

On Dell set the matching label when instructed (single command):

```bash
read -r -p 'Capture folder label to inventory: ' LABEL
```

Expected: exact instructed label, one of pre_consume, consumed, before_replay,
after_replay, before_fresh, after_fresh. No arbitrary path. Then:

```bash
python3 -B -c "import mp006 as m; m.h.inventory(m.paths(m.configuration())[1]/'$LABEL')"
```

Expected: exit 0 and new SHA256SUMS.txt. Existing manifest: STOP, do not overwrite.

On OmniBook, with the instructed `$Label` already assigned:

```powershell
New-Item -ItemType Directory -Path "$Case\receipts\$Label" -ErrorAction Stop
```

Expected: newly created receipt. Existing directory: STOP.

```powershell
scp -r "seth@192.168.1.118:${RemoteCase}/$Label" "$Case\receipts\$Label\"
```

Expected: successful copy, inside receipts/LABEL/LABEL. Any transport failure:
HARNESS_ERROR; preserve partial receipt, do not retry into it.

```powershell
python -B -c "import mp006 as m; p=m.Path(r'$Case')/'receipts'/'$Label'/'$Label'; rows=(p/'SHA256SUMS.txt').read_text().splitlines(); assert rows; assert all(m.h.digest((p/line.split('  ',1)[1]).read_bytes())==line.split('  ',1)[0] for line in rows); m.saved(p.parent,'$Label'); print('TRANSFER HASHES AND SAVED STATE VERIFIED')"
```

Expected: verification message. Any mismatch: HARNESS_ERROR; STOP, preserve both copies.

```powershell
if (Test-Path -LiteralPath "$Case\$Label") { throw 'STOP: canonical evidence already exists' } else { Move-Item -LiteralPath "$Case\receipts\$Label\$Label" -Destination "$Case\$Label" -ErrorAction Stop }
```

Expected: canonical copy appears; never overwrites. Moving the verified received
copy does not affect Dell state. Every use of T requires all these individual steps.

## Initial consumption (after STOP 1)

Dell:

```bash
python3 -B mp006.py initialize --authorization /home/seth/MULTI_PROVIDER_006/authorizations/MP006_R01_RUN001.json
```

Expected: exit 0; only new empty ledger/snapshot. Existing state: STOP. Never rerun
initialize for recovery. OmniBook:

```powershell
python -B .\mp006.py prepare --kind consume --authorization .\authorizations\MP006_R01_RUN001.json
```

Expected: new original directory containing exact request, authorization JSON,
base64 header, identity and mint logs. Error/existing directory: STOP.

Dell:

```bash
mkdir -p /home/seth/MULTI_PROVIDER_006/evidence/MP006_R01_RUN001/R01
```

Expected: case directory only; no state modifications. OmniBook:

```powershell
scp -r "$Case\original" "seth@192.168.1.118:${RemoteCase}/"
```

Expected: new Dell original copy. Compare package/header hashes on both machines
using the next command on each (Python executable is python on Windows):

```bash
python3 -B -c "import mp006 as m; p=m.paths(m.configuration())[1]/'original'; print(m.h.preserved_request(p)[0])"
```

OmniBook equivalent:

```powershell
python -B -c "import mp006 as m; p=m.paths(m.configuration())[1]/'original'; print(m.h.preserved_request(p)[0])"
```

Expected: identical full identity including package_sha256/header_sha256.
Mismatch: HARNESS_ERROR; STOP. Dell:

```bash
python3 -B mp006.py launch --tag initial --authorization /home/seth/MULTI_PROVIDER_006/authorizations/MP006_R01_RUN001.json
```

Expected: detached PID recorded. This alone proves neither listening nor execution.

```bash
cat evidence/MP006_R01_RUN001/R01/runtime/initial.log
```

Expected: frozen provider startup, no traceback/recovery anomalies. Unexpected:
STOP; preserve log before changes.

```bash
ss -ltnp 'sport = :9090'
```

Expected: intended provider listener. Check against recorded PID with:

```bash
python3 -B -c "import mp006 as m; s,c=m.paths(m.configuration()); p=m.h.read(c/'runtime/initial.pid.json')['pid']; print(m.h.process_identity(p,m.REF/'provider_a/provider_a.py',s/m.FILES[1],m.ROOT/'mp006.py','provider_a'))"
```

Expected: correct PID, runtime/hash, state path, boot ID and command. Then set PID:

```bash
PROVIDER_PID=$(python3 -B -c "import mp006 as m; print(m.h.read(m.paths(m.configuration())[1]/'runtime/initial.pid.json')['pid'])")
```

Expected: PID loaded from actual launch record. Dell:

```bash
python3 -B mp006.py capture --label pre_consume --pid "$PROVIDER_PID" --authorization /home/seth/MULTI_PROVIDER_006/authorizations/MP006_R01_RUN001.json
```

Expected: fresh-state evidence. OmniBook:

```powershell
$Label = 'pre_consume'
```

Run transfer T. Then OmniBook:

```powershell
python -B .\mp006.py send --kind consume --log "$AssociationLog" --authorization .\authorizations\MP006_R01_RUN001.json
```

Expected: send_consume evidence with signed START/COMPLETE, not merely HTTP 204.
Transport/recorder failure: STOP; do not resend. Dell:

```bash
python3 -B mp006.py capture --label consumed --pid "$PROVIDER_PID" --authorization /home/seth/MULTI_PROVIDER_006/authorizations/MP006_R01_RUN001.json
```

OmniBook:

```powershell
$Label = 'consumed'
```

Run T. Then:

```powershell
python -B .\mp006.py checkpoint --log "$AssociationLog" --authorization .\authorizations\MP006_R01_RUN001.json
```

Expected: exit 0 and AWAITING_EXPLICIT_POWER_APPROVAL checkpoint; initial one-entry
ledger advance, one execution and signed START/COMPLETE established. Any failure:
STOP; no power interruption. Dell:

```bash
python3 -B mp006.py marker --tag initial
```

Expected: actual UTC/boot ID and READY FOR POWER LOSS. Informational only.

OmniBook, separate PowerShell terminal at final workspace:

```powershell
.\Watch-MP006Reachability.ps1 -Target 192.168.1.118 -OutputPath .\evidence\MP006_R01_RUN001\R01\reachability.jsonl
```

Expected: continuous flushed JSONL output to file (no console heartbeat). In main shell:

```powershell
Get-Content -LiteralPath "$Case\reachability.jsonl" -Tail 3
```

Expected: Success before disconnection. ProbeError or no log: STOP.

## STOP 2 — immediately before physical power disconnection

Operator explicitly confirms all: original bytes independently preserved on
OmniBook; initial durable ledger/snapshot/execution transferred and verified;
signed START/COMPLETE verified by checkpoint; initial execution exactly once;
provider idle with no requests in flight; current boot ID recorded; relay/recorder
remain running; witness actively records pre-loss Success; unrelated Dell work/data
protected. Initial evidence is already off Dell. Hash-inventory the original and
send_consume directories on OmniBook using existing h.inventory before approval.
No script grants physical approval. Obtain an explicit human approval now.

Before asking for that approval, OmniBook must inventory the original authority:

```powershell
python -B -c "import mp006 as m; m.h.preserved_request(m.paths(m.configuration())[1]/'original'); m.h.inventory(m.paths(m.configuration())[1]/'original'); print('ORIGINAL AUTHORITY INVENTORIED')"
```

And its initial signed/send evidence, in a separate command:

```powershell
python -B -c "import mp006 as m; m.h.inventory(m.paths(m.configuration())[1]/'send_consume'); print('INITIAL SEND EVIDENCE INVENTORIED')"
```

Expected: exclusive inventories. Initial ledger/snapshot/execution inventories
have already been independently verified by T. Inspect current Dell connections:

```bash
ss -tnp 'sport = :9090'
```

Expected: no active requests; operator confirms no concurrent test sender/work.
An empty connection list alone is not proof of idle execution; combine it with
the verified correlated COMPLETE, completed local record and controlled senders.

Operator then disconnects external Dell power, documents unplug/reconnect observations,
and reconnects power after a documented interval. No minimum duration. Do not stop
the relay, association recorder, or witness. Video optional.

## Recovery: preserve first

After boot on Dell: do not launch Provider A, open a provider startup terminal, run
bootstrap, or modify its state. Open a plain terminal and set cwd as above. FIRST:

```bash
python3 -B mp006.py recover-capture
```

Expected: raw copies plus inventory in recovered_before_start; stopped-provider
check, new boot record and source checks succeed. It reads persistent state only.
Even on failure raw evidence may already exist. Preserve it; never delete/retry
over this folder. Unexpected provider/listener: PRECONDITION_NOT_MET, STOP. A process
that started and exited before inspection may escape this check; review boot/service
journals and startup logs, not just current listeners. Do not claim pristine capture
if unexpected startup cannot be excluded by the reviewed launch mechanisms.

```bash
journalctl -b --no-pager
```

Expected: review startup history for discovered launch mechanisms and anomalies.
This is corroboration; absence of a keyword is not proof no program ever ran.

OmniBook:

```powershell
New-Item -ItemType Directory -Path "$Case\receipts\recovery" -ErrorAction Stop
```

```powershell
scp -r "seth@192.168.1.118:${RemoteCase}/recovered_before_start" "seth@192.168.1.118:${RemoteCase}/recovery_capture_check.json" "$Case\receipts\recovery\"
```

Expected: raw directory and capture check copied. Any missing check: preserve raw,
STOP. Verify received raw manifest before provider start:

```powershell
python -B -c "import mp006 as m; p=m.Path(r'$Case')/'receipts/recovery/recovered_before_start'; rows=(p/'SHA256SUMS.txt').read_text().splitlines(); assert rows; assert all(m.h.digest((p/line.split('  ',1)[1]).read_bytes())==line.split('  ',1)[0] for line in rows); print('RAW RECOVERY TRANSFER VERIFIED')"
```

Expected: message. Then promote each only if absent:

```powershell
if (Test-Path -LiteralPath "$Case\recovered_before_start") { throw 'STOP: existing raw evidence' } else { Move-Item -LiteralPath "$Case\receipts\recovery\recovered_before_start" -Destination "$Case\recovered_before_start" -ErrorAction Stop }
```

```powershell
if (Test-Path -LiteralPath "$Case\recovery_capture_check.json") { throw 'STOP: existing capture record' } else { Move-Item -LiteralPath "$Case\receipts\recovery\recovery_capture_check.json" -Destination "$Case\recovery_capture_check.json" -ErrorAction Stop }
```

Dell, only after verified off-machine preservation:

```bash
python3 -B mp006.py validate-recovered
```

Expected: PASS receipt after validation of copied bytes and equality to pre-loss
history. Unexpected state: STOP and preserve. Do not repair to proceed.

```bash
python3 -B mp006.py launch --tag recovered --authorization /home/seth/MULTI_PROVIDER_006/authorizations/MP006_R01_RUN001.json
```

Expected: detached launch against same persistent paths and same current capture
boot. Check recovered.log, listener and process identity as for initial launch,
using runtime/recovered.pid.json instead of initial.pid.json.

```bash
cat evidence/MP006_R01_RUN001/R01/runtime/recovered.log
```

```bash
ss -ltnp 'sport = :9090'
```

Expected: intended recovered listener. Verify actual process identity:

```bash
python3 -B -c "import mp006 as m; s,c=m.paths(m.configuration()); p=m.h.read(c/'runtime/recovered.pid.json')['pid']; print(m.h.process_identity(p,m.REF/'provider_a/provider_a.py',s/m.FILES[1],m.ROOT/'mp006.py','provider_a'))"
```

Expected: frozen runtime hash, correct persistent path and new boot ID. Any
unexpected reconciliation event in recovered.log: preserve and STOP for review.

```bash
PROVIDER_PID=$(python3 -B -c "import mp006 as m; print(m.h.read(m.paths(m.configuration())[1]/'runtime/recovered.pid.json')['pid'])")
```

```bash
python3 -B mp006.py marker --tag recovered
```

Expected: new boot ID and RECOVERED. Then:

```bash
python3 -B mp006.py capture --label before_replay --pid "$PROVIDER_PID" --authorization /home/seth/MULTI_PROVIDER_006/authorizations/MP006_R01_RUN001.json
```

OmniBook:

```powershell
$Label = 'before_replay'
```

Run T. Then exact replay on OmniBook:

```powershell
python -B .\mp006.py send --kind replay --log "$AssociationLog" --authorization .\authorizations\MP006_R01_RUN001.json
```

Expected: signed DENY auth_spent. START/COMPLETE, new consumption/execution or spent
authority disappearing: preserve as potential FAIL; no fresh send until reviewed.
Dell:

```bash
python3 -B mp006.py capture --label after_replay --pid "$PROVIDER_PID" --authorization /home/seth/MULTI_PROVIDER_006/authorizations/MP006_R01_RUN001.json
```

OmniBook:

```powershell
$Label = 'after_replay'
```

Run T. Then:

```powershell
python -B .\mp006.py prepare --kind fresh --authorization .\authorizations\MP006_R01_RUN001.json
```

```powershell
scp -r "$Case\fresh" "seth@192.168.1.118:${RemoteCase}/"
```

Expected: distinct fresh identity, new Dell fresh folder. Independently run the
following identity command on Dell:

```bash
python3 -B -c "import mp006 as m; p=m.paths(m.configuration())[1]/'fresh'; print(m.h.preserved_request(p)[0])"
```

And on OmniBook:

```powershell
python -B -c "import mp006 as m; p=m.paths(m.configuration())[1]/'fresh'; print(m.h.preserved_request(p)[0])"
```

Expected: matching fresh identities, distinct from original. Compare their full
output before capture/send. Mismatch: HARNESS_ERROR; STOP. Dell:

```bash
python3 -B mp006.py capture --label before_fresh --pid "$PROVIDER_PID" --authorization /home/seth/MULTI_PROVIDER_006/authorizations/MP006_R01_RUN001.json
```

OmniBook:

```powershell
$Label = 'before_fresh'
```

Run T. Then:

```powershell
python -B .\mp006.py send --kind fresh --log "$AssociationLog" --authorization .\authorizations\MP006_R01_RUN001.json
```

Expected: signed START/COMPLETE from recovered A. Dell:

```bash
python3 -B mp006.py capture --label after_fresh --pid "$PROVIDER_PID" --authorization /home/seth/MULTI_PROVIDER_006/authorizations/MP006_R01_RUN001.json
```

OmniBook:

```powershell
$Label = 'after_fresh'
```

Run T. Missing fresh completion means overall completion is not PASS, even if replay
safety is established. Never mint a replacement authority to conceal a failure.

## Final preservation and scoring (OmniBook)

Verify witness has Success after outage; stop only witness with Ctrl+C in its shell.
Keep recorder running until all signed events and final late-event checks complete.
Preserve a final copy of the continuous recorder log under the case directory:

```powershell
if (Test-Path -LiteralPath "$Case\association_preserved.jsonl") { throw 'STOP: existing log copy' } else { Copy-Item -LiteralPath "$AssociationLog" -Destination "$Case\association_preserved.jsonl" -ErrorAction Stop }
```

Expected: copy. Verify source and copy while no requests are being sent:

```powershell
Get-FileHash -LiteralPath $AssociationLog,"$Case\association_preserved.jsonl" -Algorithm SHA256
```

Expected: equal hashes. If it changes during copy, preserve both versions and
review; do not silently overwrite. Dell runtime evidence inventory:

```bash
python3 -B -c "import mp006 as m; m.h.inventory(m.paths(m.configuration())[1]/'runtime')"
```

Expected: new inventory, after all sends have completed. OmniBook:

```powershell
New-Item -ItemType Directory -Path "$Case\receipts\runtime" -ErrorAction Stop
```

```powershell
scp -r "seth@192.168.1.118:${RemoteCase}/runtime" "$Case\receipts\runtime\"
```

```powershell
python -B -c "import mp006 as m; p=m.Path(r'$Case')/'receipts/runtime/runtime'; rows=(p/'SHA256SUMS.txt').read_text().splitlines(); assert rows; assert all(m.h.digest((p/line.split('  ',1)[1]).read_bytes())==line.split('  ',1)[0] for line in rows); print('RUNTIME TRANSFER VERIFIED')"
```

```powershell
if (Test-Path -LiteralPath "$Case\runtime") { throw 'STOP: existing runtime evidence' } else { Move-Item -LiteralPath "$Case\receipts\runtime\runtime" -Destination "$Case\runtime" -ErrorAction Stop }
```

Expected: verified runtime logs and PID records retained on OmniBook. Mismatch or
existing output: STOP, preserve receipt. Do not replace OmniBook evidence.

Record truthful operator observations with this single interactive command:

```powershell
python -B -c "import mp006 as m; p=m.paths(m.configuration())[1]; d={k:input(k+': ') for k in ('operator','disconnected_utc','reconnected_utc')}; d.update({k:input(k+' (yes/no): ').strip().lower()=='yes' for k in ('physical_disconnect','power_loss_approved','idle_confirmed','initial_evidence_preserved_on_omnibook','recovered_raw_preserved_on_omnibook')}); m.h.write(p/'power_procedure.json',d)"
```

Expected: original power procedure record; actual observations only. No fabricated
timestamps, retrospective assumed approvals or edited evidence to obtain PASS.

```powershell
python -B .\mp006.py score --log "$Case\association_preserved.jsonl"
```

Expected: explicit classification/checks/safety result, then case SHA256SUMS.txt.
PASS requires all evidence. No automatic retry over existing case_results/inventory.
Use the preserved final log, containing all relevant events, for final scoring.
After scoring verify the final inventory independently:

```powershell
python -B -c "import mp006 as m; p=m.paths(m.configuration())[1]; rows=(p/'SHA256SUMS.txt').read_text().splitlines(); assert rows; assert all(m.h.digest((p/line.split('  ',1)[1]).read_bytes())==line.split('  ',1)[0] for line in rows); print('FINAL EVIDENCE INVENTORY VERIFIED')"
```

Expected: message; mismatch is HARNESS_ERROR and requires preserved review.

## Classification and failure handling

| Observation | Classification/action |
|---|---|
| Confirmed exact replay executes or consumes again under verified conditions | FAIL, authority safety failure; preserve signed and local evidence |
| Pre-loss and raw recovered durable history differ | Preserve as potential persistence FAIL; STOP before provider startup; review media/collection causes before attributing it |
| Ledger/state invalid after power loss | Preserve as potential persistence FAIL; no repair; distinguish actual raw corruption from transfer mismatch |
| Fresh authority validly denied by recovered provider | FAIL for required functionality; record replay safety separately |
| Fresh request cannot be sent/observed due to relay/recorder trouble | HARNESS_ERROR or INCOMPLETE; not proof of restored authority |
| Bad signature, changed bytes, failed transfer, truncated/replaced recorder prefix | HARNESS_ERROR; no safety conclusion from invalid evidence |
| Wrong machine/hash/path, same boot, unexpected autostart/process, initial consumption not established | PRECONDITION_NOT_MET; STOP |
| Missing artifacts, no observed unreachable interval, missing physical procedure | INCOMPLETE; never substitute a successful reboot for evidence |
| HTTP success but signed completion missing | STOP; preserve as INCOMPLETE unless a concrete transport/recorder defect establishes HARNESS_ERROR |
| Existing output path | STOP; preserve prior/partial attempt, do not delete/reuse |
| Recovery cannot boot | INCOMPLETE unless preserved evidence establishes an implementation failure; preserve disk before repair |

CLI diagnostics are observations, not a substitute for review of cause. In
particular MP005 wait_events can emit PRECONDITION_NOT_MET on timeout; that does
not establish SUT safety failure. The incident report must separate the diagnostic
from the adjudicated experiment classification and retain original output.

PASS supports only: this tested Provider A retained consumed authority across the
documented physical power-loss/reboot, rejected exact replay without execution,
and accepted separate fresh authority. It does not cover mid-write interruption,
complete-history rollback, concurrency, or other hardware/implementations.
