# Minimal later discovery — NOT RUN during R3 review

Current blocker: verified live physical-role/hostname/IP/path/transport map. Do not scan the network or try historical addresses. No service contact, provider start, live preflight, rehearsal or scoring is authorized by this document. Obtain separate operator authorization for identity collection first.

## Collect on physically identified machines, one command at a time

Start with Dell Provider A, then separate HP/Mint Provider B, then Pi3 relay. Human opens each known local console or independently verified session. Label it by physical role, not an assumed IP. Give ONE command and wait for output before the next:

1. `hostname`
2. `ip -4 -brief address`
3. `cat /etc/os-release`
4. `python3 --version`
5. `pwd`

Do not treat pwd as a deployed project path. Ask the operator for its actual MP005 deployment/staging root or record NOT_DEPLOYED. Only after that absolute path is confirmed, bind MP_ROOT, then separately run `findmnt -T "$MP_ROOT" -o TARGET,FSTYPE,OPTIONS`. Only after its exact role runtime path is confirmed, bind MP_RUNTIME and run `sha256sum "$MP_RUNTIME"`. If undeployed, record intended destination as a proposal, never a verified existing runtime. No deployment or state initialization in discovery.

OmniBook — MAIN PowerShell, separately:

1. `hostname`
2. `Get-NetIPAddress -AddressFamily IPv4`
3. `Get-CimInstance Win32_OperatingSystem | Select-Object Caption,Version`
4. `python --version`
5. `Get-Location`
6. `Get-Volume`

Ask where association will actually run (Windows OmniBook, Linux environment or another explicitly identified placement); verify that environment separately before choosing command syntax. Do not query the association service or assume its current path/platform. Hash its exact confirmed recorder path later with `Get-FileHash -Algorithm SHA256 -LiteralPath $RecorderPath` if Windows, or the Linux equivalent only in verified Linux.

## Return the smallest sufficient map

Fill MACHINE_MAP_TEMPLATE.md with role, physical machine, hostname/current selected IPv4, OS/Python/filesystem, actual runtime path/hash or NOT_DEPLOYED, provider state directory, ledger/snapshot/execution paths, and verification outputs. Explicitly exclude Pavilion from live roles.

Also obtain: intended provider ports and ingest URLs; relay root/port/destinations; association root/port/log/registry/trust paths; controller root/evidence destination; role usernames/connection aliases (no passwords/SSH private keys); provider runtime+inspection window labels; exact source/destination paths and transfer method for case authority/snapshots; how association log remains continuously readable/prefix-preserving at controller. A one-time stale log copy is insufficient. Do not invent missing transport details.

Then STOP and reconcile candidate configuration deliberately before freeze. No health/network probes, duplicate-process inspection, bootstrap, provider execution or rehearsal are included here; those belong only to a later separately authorized live preflight. Changing/reusing state or existing evidence to make a map fit is forbidden.

Exact first operator command, only once this later collection is authorized, at the physically identified Dell console:

```sh
hostname
```
