param(
    [Parameter(Mandatory=$true)]
    [ValidateSet('provider_a','provider_b')]
    [string]$Provider,

    [Parameter(Mandatory=$true)]
    [ValidatePattern('^[A-Za-z0-9_-]+$')]
    [string]$Session,

    [ValidateSet('initial','restart')]
    [string]$StartTag = 'initial'
)

$ErrorActionPreference = 'Stop'

$Root = 'C:\Users\holiw\esp32-main\MULTI_PROVIDER_005'
$RemoteRoot = '/home/seth/MULTI_PROVIDER_005'

if ($Session -eq 'MP005_SCORED_20261025_R2') {
    throw 'STOP: PRESERVED SCORED SESSION CANNOT BE REUSED'
}

$IP = if ($Provider -eq 'provider_a') {
    '192.168.1.118'
} else {
    '192.168.1.107'
}

$Hostname = if ($Provider -eq 'provider_a') {
    'Xer0trust-3'
} else {
    'Xer0trust2'
}

$AuthFile = "$Root\OPERATOR_HANDOFF\authorizations\$Session.scored.json"
$LockFile = "$Root\configs\MP005_LOCK_SHA256SUMS.txt"
$ManifestFile = "$Root\configs\MP005_RUN_MANIFEST.json"

foreach ($Path in @($AuthFile, $LockFile, $ManifestFile)) {
    if (!(Test-Path -LiteralPath $Path -PathType Leaf)) {
        throw "STOP: REQUIRED FILE MISSING: $Path"
    }
}

$Auth = Get-Content $AuthFile -Raw | ConvertFrom-Json
$Manifest = Get-Content $ManifestFile -Raw | ConvertFrom-Json

$AuthHash = (Get-FileHash $AuthFile -Algorithm SHA256).Hash.ToLowerInvariant()
$LockHash = (Get-FileHash $LockFile -Algorithm SHA256).Hash.ToLowerInvariant()

$State = "$RemoteRoot/live_state/scored/$Session/$Provider"

if (
    $Auth.authorized -ne $true -or
    $Auth.phase -ne 'scored' -or
    $Auth.session_id -ne $Session -or
    $Auth.canonical_lock_sha256 -ne $LockHash -or
    $Manifest.deployments.($Provider).host -ne $IP -or
    $Manifest.deployments.($Provider).state_dir -ne $State
) {
    throw 'STOP: AUTHORIZATION OR DEPLOYMENT MISMATCH'
}

$AssociationURL = $Manifest.association_url

if ($AssociationURL -ne 'http://192.168.1.102:9191/boundary') {
    throw 'STOP: ASSOCIATION DESTINATION MISMATCH'
}

$RemoteScript = @(
    'set -euo pipefail'
    'PROVIDER="$1"'
    'SESSION="$2"'
    'TAG="$3"'
    'AUTH_HASH="$4"'
    'LOCK_HASH="$5"'
    'EXPECTED_HOST="$6"'
    'ROOT=/home/seth/MULTI_PROVIDER_005'
    'STATE="$ROOT/live_state/scored/$SESSION/$PROVIDER"'
    'AUTH_FILE="$ROOT/$SESSION.scored.json"'
    'LOG_DIR="$ROOT/evidence/scored/$SESSION/runtime"'
    'LOG="$LOG_DIR/${PROVIDER}_${TAG}.log"'
    'PID_FILE="$LOG_DIR/${PROVIDER}_${TAG}.pid"'
    'cd /home/seth'
    'if [ "$(hostname)" != "$EXPECTED_HOST" ]; then echo "STOP: WRONG HOST"; exit 1; fi'
    'test -d "$STATE"'
    'test -f "$STATE/${PROVIDER}_spent_state.json"'
    'test -f "$STATE/${PROVIDER}_consume_ledger.jsonl"'
    'test -f "$AUTH_FILE"'
    'printf "%s  %s\n" "$AUTH_HASH" "$AUTH_FILE" | sha256sum -c -'
    'printf "%s  %s\n" "$LOCK_HASH" "$ROOT/configs/MP005_LOCK_SHA256SUMS.txt" | sha256sum -c -'
    'if ss -Hltpn | grep -q ":9090 "; then echo "STOP: PROVIDER PORT ALREADY ACTIVE"; exit 1; fi'
    'test ! -e "$LOG"'
    'test ! -e "$PID_FILE"'
    'mkdir -p "$LOG_DIR"'
    'nohup python3 -u -B "$ROOT/harness/launch_provider.py" --mode live --root "$ROOT" --provider "$PROVIDER" --state-dir "$STATE" --host 0.0.0.0 --port 9090 --association-url http://192.168.1.102:9191/boundary --phase scored --operator-authorization "$AUTH_FILE" </dev/null >"$LOG" 2>&1 &'
    'NEW_PID=$!'
    'printf "%s\n" "$NEW_PID" > "$PID_FILE"'
    'sleep 2'
    'if ! kill -0 "$NEW_PID" 2>/dev/null; then echo "STOP: PROVIDER EXITED"; cat "$LOG"; exit 1; fi'
    'if ! ss -Hltpn | grep -q ":9090 "; then echo "STOP: PROVIDER NOT LISTENING"; cat "$LOG"; exit 1; fi'
    'echo "DETACHED PROVIDER RUNNING"'
    'echo "PID: $NEW_PID"'
    'echo "LOG: $LOG"'
    'echo "STATE: $STATE"'
)

Write-Host "CHECKED AUTHORIZED SESSION: $Session"
Write-Host "TARGET: $Provider at $IP"
Write-Host "LAUNCH TYPE: $StartTag"

$RemoteScript |
    ssh -T "seth@$IP" "tr -d '\015' | bash -s -- $Provider $Session $StartTag $AuthHash $LockHash $Hostname"

if ($LASTEXITCODE -ne 0) {
    throw 'STOP: DETACHED LAUNCH FAILED'
}

Write-Host 'PROVIDER STARTED WITH INDEPENDENT LOGGING'