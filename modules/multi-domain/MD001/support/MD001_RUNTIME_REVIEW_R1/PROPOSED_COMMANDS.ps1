# REVIEW ONLY. This file is not executed by Desktop. Stage/Validate must be invoked explicitly.
[CmdletBinding()]
param(
    [Parameter(Mandatory)][ValidateSet('dell','pi','hp')][string]$Profile,
    [Parameter(Mandatory)][ValidatePattern('^[a-z_][a-z0-9_-]*$')][string]$RemoteUser,
    [Parameter(Mandatory)][ValidateSet('Stage','Validate')][string]$Action
)
$ErrorActionPreference = 'Stop'
$addresses = @{dell='10.10.10.10'; pi='30.30.30.30'; hp='40.40.40.40'}
$target = $RemoteUser + '@' + $addresses[$Profile]
$appArchive = Join-Path (Split-Path $PSScriptRoot -Parent) 'MD001_DEPLOYMENT_R1\MD001_APPLICATION_R1.tar.gz'
$reviewArchive = Join-Path $PSScriptRoot 'MD001_RUNTIME_REVIEW_R1.tar.gz'
$expectedApp = '496e8ccde848599868aee923dff292f2ed9d1994bd06f7a95e8e6233a50987d5'
if ((Get-FileHash -LiteralPath $appArchive -Algorithm SHA256).Hash.ToLowerInvariant() -ne $expectedApp) { throw 'Original archive hash mismatch' }
function Invoke-RemoteScript([string]$Body, [string]$ArgsText) {
    # Strip Windows line endings before bash parses the transmitted review script.
    $Body | & ssh $target "tr -d '\r' | bash -s -- $ArgsText"
    if ($LASTEXITCODE -ne 0) { throw 'Remote command failed; preserve output and stop' }
}
if ($Action -eq 'Stage') {
    $reviewHash = (Get-FileHash -LiteralPath $reviewArchive -Algorithm SHA256).Hash.ToLowerInvariant()
    $expectedReview = (Get-Content -LiteralPath (Join-Path $PSScriptRoot 'REVIEW_BUNDLE_SHA256.txt') -Raw).Split(' ')[0].Trim()
    if ($reviewHash -ne $expectedReview) { throw 'Review archive hash mismatch' }
    if ($Profile -ne 'dell') {
        Invoke-RemoteScript 'set -eu; test ! -e "$HOME/MD001_APPLICATION_R1.tar.gz"; test ! -e "$HOME/MD001_APPLICATION_R1"' ''
        & scp $appArchive "${target}:MD001_APPLICATION_R1.tar.gz"
        if ($LASTEXITCODE -ne 0) { throw 'Application transfer failed' }
    }
    Invoke-RemoteScript 'set -eu; test ! -e "$HOME/MD001_RUNTIME_REVIEW_R1.tar.gz"; test ! -e "$HOME/MD001_RUNTIME_REVIEW_R1"' ''
    & scp $reviewArchive "${target}:MD001_RUNTIME_REVIEW_R1.tar.gz"
    if ($LASTEXITCODE -ne 0) { throw 'Review transfer failed' }
    $stage = @'
set -eu
profile="$1"
review_hash="$2"
cd "$HOME"
printf '%s  MD001_APPLICATION_R1.tar.gz\n' '496e8ccde848599868aee923dff292f2ed9d1994bd06f7a95e8e6233a50987d5' | sha256sum -c -
if [ "$profile" = dell ]; then
    test -d MD001_APPLICATION_R1
else
    test ! -e MD001_APPLICATION_R1
    tar -xzf MD001_APPLICATION_R1.tar.gz
fi
(cd MD001_APPLICATION_R1 && sha256sum -c APP_SHA256SUMS.txt)
printf '%s  MD001_RUNTIME_REVIEW_R1.tar.gz\n' "$review_hash" | sha256sum -c -
test ! -e MD001_RUNTIME_REVIEW_R1
tar -xzf MD001_RUNTIME_REVIEW_R1.tar.gz
(cd MD001_RUNTIME_REVIEW_R1 && sha256sum -c REVIEW_FILES_SHA256SUMS.txt)
'@
    Invoke-RemoteScript $stage "$Profile $reviewHash"
} else {
    $validate = @'
set -eu
profile="$1"
cd "$HOME/MD001_RUNTIME_REVIEW_R1"
sha256sum -c REVIEW_FILES_SHA256SUMS.txt
(cd "$HOME/MD001_APPLICATION_R1" && sha256sum -c APP_SHA256SUMS.txt)
run="host_validation/$(date -u +%Y%m%dT%H%M%SZ)_${profile}_$$"
test ! -e "$run"
mkdir -p "$run"
dpkg-query -W python3 python3-cryptography > "$run/packages.txt"
dpkg-query -s python3-cryptography > "$run/package-status.txt"
uname -a > "$run/uname.txt"
dpkg --print-architecture > "$run/dpkg-architecture.txt"
cat /etc/os-release > "$run/os-release.txt"
status=0
/usr/bin/python3 -B -E -s runtime_probe.py --app "$HOME/MD001_APPLICATION_R1" --profile "$profile" --out "$run/probe" > "$run/probe.stdout.txt" 2> "$run/probe.stderr.txt" || status=$?
(cd "$run" && find . -type f ! -name HOST_SHA256SUMS.txt -print0 | sort -z | xargs -0 sha256sum > HOST_SHA256SUMS.txt)
printf 'Host validation output: %s/%s\n' "$PWD" "$run"
cat "$run/probe.stdout.txt"
if [ "$status" -ne 0 ]; then cat "$run/probe.stderr.txt"; exit "$status"; fi
'@
    Invoke-RemoteScript $validate $Profile
}
