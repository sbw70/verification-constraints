# Reviewed command interfaces — NOT EXECUTABLE UNTIL INPUTS/LOCK/GATES RESOLVED

All variables below are session facts to be bound explicitly, one assignment at a time, after physical-role discovery. An unset/unknown value is a STOP, never a reason to invent a path/address. These are command templates, not permission to start live work.

Windows controller: `$MpRoot` is its verified project root, `$Phase` is rehearsal/scored, `$AuthFile` is the explicit session authorization, `$SessionId` actual-date ID, `$Case` R01/R02, `$AssociationLog` a continuously current local log. Build ONE argument-array assignment after those facts are verified:

```powershell
$LiveArgs = @('--root',$MpRoot,'--phase',$Phase,'--operator-authorization',$AuthFile,'--session-id',$SessionId,'--case',$Case)
```

Every controller case action uses this exact reviewed interface (choose one action per command; see case runbook):

```powershell
python "$MpRoot\harness\live_case.py" prepare @LiveArgs
```

Linux provider inspection shell: MP_ROOT, MP_PHASE, MP_AUTH, MP_SESSION, MP_CASE, MP_STATE, MP_PID and MP_PROVIDER are independently verified local facts; MP_PROVIDER is provider_a on Dell or provider_b on separate HP/Mint. Build one array:

```sh
MP_ARGS=(--root "$MP_ROOT" --phase "$MP_PHASE" --operator-authorization "$MP_AUTH" --session-id "$MP_SESSION" --case "$MP_CASE")
```

Explicit bootstrap for a NEW reviewed state directory, ONLY during later authorized setup, never replacing history:

```sh
python3 "$MP_ROOT/harness/live_case.py" initialize-state "${MP_ARGS[@]}" --state-dir "$MP_STATE"
```

Provider runtime terminal, foreground manual launch after authorization and bootstrap. MP_PORT and MP_ASSOCIATION_URL must match the locked verified map. Human must preserve this exact command and cwd for restart:

```sh
python3 -u -B "$MP_ROOT/harness/launch_provider.py" --mode live --root "$MP_ROOT" --provider "$MP_PROVIDER" --state-dir "$MP_STATE" --host 0.0.0.0 --port "$MP_PORT" --association-url "$MP_ASSOCIATION_URL" --phase "$MP_PHASE" --operator-authorization "$MP_AUTH"
```

Association on verified Windows host, foreground in OmniBook — Association, `$AssociationLogOut` an absent output file:

```powershell
python -u -B "$MpRoot\harness\launch_service.py" --root $MpRoot --role association --phase $Phase --operator-authorization $AuthFile --session-id $SessionId --log $AssociationLogOut
```

If association is actually Linux, use the same launch_service.py interface with verified Linux variables in its correctly labeled terminal, not this Windows command. Actual placement must be resolved before readiness.

Relay — SSH, foreground, once for the session; do not restart between cases:

```sh
python3 -u -B "$MP_ROOT/harness/launch_service.py" --root "$MP_ROOT" --role intermediary --phase "$MP_PHASE" --operator-authorization "$MP_AUTH" --session-id "$MP_SESSION"
```

Evidence copy templates use current verified `$Target` (`user@verified-host`), `$RemoteCase` and `$LocalCase` (absolute case directories) on OmniBook — MAIN PowerShell. Paths must have no unresolved tokens; verify source and absence of the destination artifact BEFORE each copy. Copy initial prepared authority once from controller to target case parent; do not re-mint on target:

```powershell
scp -r "$LocalCase" "${Target}:${RemoteCaseParent}/"
```

For each NEW provider snapshot directory, bind `$CaptureLabel` to the just-completed label and copy it back once:

```powershell
scp -r "${Target}:${RemoteCase}/$CaptureLabel" "$LocalCase/"
```

For each NEW process JSON, bind `$ProcessFile` to pre_restart_process.json or post_restart_process.json and copy once:

```powershell
scp "${Target}:${RemoteCase}/$ProcessFile" "$LocalCase/"
```

After controller prepare-fresh, transfer its exact fresh directory once:

```powershell
scp -r "$LocalCase/fresh" "${Target}:${RemoteCase}/"
```

Use the host-local shell for provider process/state capture; a Windows controller cannot read Linux /proc. Transfer raw ledger/state/execution and metadata together. SCP does not validate semantic identity: validate raw hashes and authority/path metadata before using the copy. Never overwrite an existing destination to resolve confusion. No copying passwords or private SSH access keys into this packet.
