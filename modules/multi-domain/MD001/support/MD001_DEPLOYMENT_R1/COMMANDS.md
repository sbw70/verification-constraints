# Proposed commands — review only, STOP before deployment

These are commands to run only after explicit deployment approval. Usernames, local
interface names, approved remote install directories and HP management path remain
operator inputs. Do not execute placeholder values. No network reconfiguration is
included. Preserve existing MP005/MH001 services and paths.

## Copy reviewed application-only bundle after approval

From OmniBook PowerShell, replace SSH usernames first. Inspect the transfer digest
against DEPLOY_BUNDLE_SHA256.txt, then copy to the approved account's home directory:

```powershell
Get-FileHash -Algorithm SHA256 .\MD001_DEPLOYMENT_R1\MD001_APPLICATION_R1.tar.gz
scp .\MD001_DEPLOYMENT_R1\MD001_APPLICATION_R1.tar.gz DELL_USER@10.10.10.10:~/
scp .\MD001_DEPLOYMENT_R1\MD001_APPLICATION_R1.tar.gz PI_USER@30.30.30.30:~/
scp .\MD001_DEPLOYMENT_R1\MD001_APPLICATION_R1.tar.gz HP_USER@40.40.40.40:~/
```

Direct controller SSH to HP has not been established by the handoff. Resolve an
approved transfer/management path before the last command; do not broaden rules
merely to run it. On each host, verify sha256sum against the supplied bundle digest,
check ~/MD001_APPLICATION_R1 does not already exist, then extract once:

```sh
test ! -e "$HOME/MD001_APPLICATION_R1" || exit 1
tar -xzf "$HOME/MD001_APPLICATION_R1.tar.gz" -C "$HOME"
cd "$HOME/MD001_APPLICATION_R1"
sha256sum -c APP_SHA256SUMS.txt
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
```

Python3 with venv and cryptography49.0.0 is required. Pi3B+ OS architecture/Python and
wheel availability have not been validated. If installation cannot satisfy this pin,
stop and report it; do not silently substitute versions. Use an approved pre-provided
wheelhouse if the isolated hosts have no package-download access. Do not change
routing to install dependencies. Capture actual Python/cryptography versions.

## Test-key and trust provisioning

On Dell, once, using a new lab-only directory:

```sh
cd "$HOME/MD001_APPLICATION_R1"
umask 077
.venv/bin/python -B md001.py keygen --out lab-key
cat lab-key/provisioning.json
sha256sum lab-key/trust.json
```

Through the approved controller file-transfer channel, copy only lab-key/trust.json
to HP as trust.json. Compare SHA-256 and the producer key fingerprint out of band.
Retain provisioning.json and transfer record as evidence. Preserve Dell's disposable
private key for reproducibility under the operator's existing test-key convention;
do not give it to relay or verifier. Validation keys in the desktop preparation tree
are excluded from the deployment archive.

## Start required application services for approved preflight

Use separate foreground terminals. Select a fresh unique directory label for every
launch; the examples must not be reused after they have created output. Parent
evidence directory is created by the application. Retain terminal output in addition
to service-created files. Do not enable unattended restart or boot services.

On HP, verifier terminal:

```sh
cd "$HOME/MD001_APPLICATION_R1"
.venv/bin/python -B md001.py serve --config configs/verifier.json --trust trust.json --out evidence/PREFLIGHT_verifier_01
```

On HP, separate ingress terminal:

```sh
cd "$HOME/MD001_APPLICATION_R1"
.venv/bin/python -B md001.py serve --config configs/ingress.json --out evidence/PREFLIGHT_ingress_01
```

On Pi, relay terminal:

```sh
cd "$HOME/MD001_APPLICATION_R1"
.venv/bin/python -B md001.py serve --config configs/relay.json --out evidence/PREFLIGHT_relay_01
```

Only these sockets are intended: Pi 30.30.30.30:18081; HP 40.40.40.40:18443;
HP 127.0.0.1:18444. Pi also has a launcher-created ephemeral loopback-only denial
listener for unused route PROVIDER_A. No listener is required on Dell.
Port18443 is plaintext HTTP in this lab, not TLS. No firewall decrypts the artifact.

## Network and application preflight (after deployment approval)

On HP: `ip route get 30.30.30.30` must resolve to the intended return route via
40.40.40.1 with source40.40.40.40. Also check actual address/prefix and relevant
host firewall. A Vault-originated ping does not establish this return route.
On Pi: `ip route get 40.40.40.40` should use the approved gateway30.30.30.1.
On Dell: `ip route get 30.30.30.30` should use gateway10.10.10.1.
Use `ss -lntp` on Pi/HP to confirm actual binds and associate PIDs with process.json.

```sh
# Dell: approved application listener
nc -vz -w 3 30.30.30.30 18081
# Pi: approved HP ingress listener
nc -vz -w 3 40.40.40.40 18443
# Dell: must be blocked, with matching exported firewall denial log
nc -vz -w 3 40.40.40.40 18443
```

The existing absence of an explicit allow is not the required logged-deny evidence.
Operator must review/export effective rules and arrange an explicit logged direct
A-to-B deny under existing change control; this package makes no firewall changes.
Correlate actual source/destination/port/time to the denial entry; timeout alone
cannot identify which component blocked it. Audit IPv6/alternate paths and broad
floating/group/state exceptions only as necessary for this test path.

For application preflight, on Dell run a distinctly labeled non-scored operation:

```sh
.venv/bin/python -B md001.py produce-send --key lab-key/TEST_ONLY_private.pem --host 30.30.30.30 --port 18081 --out evidence/PREFLIGHT_sender_01
```

Retain HP and relay logs and actual forwarded body observations. TCP connects alone
are insufficient. STOP after physical preflight; do not proceed to scored commands
without explicit scored-run approval.

## Scored commands — separately gated, not authorized now

For B01 start clean approved service evidence directories and capture, then on Dell:

```sh
.venv/bin/python -B md001.py produce-send --key lab-key/TEST_ONLY_private.pem --host 30.30.30.30 --port 18081 --out evidence/B01_sender_01
```

N01: leave verifier running; stop only HP ingress by Ctrl+C, record its process,
and restart it with the separate mutation config on the same approved port:

```sh
.venv/bin/python -B md001.py serve --config configs/ingress_N01.json --out evidence/N01_ingress_01
```

On Dell send the preserved original through Pi again, without resigning:

```sh
.venv/bin/python -B md001.py resubmit --artifact evidence/B01_sender_01/artifact.json --host 30.30.30.30 --port 18081 --out evidence/N01_sender_01
```

Expected response: HTTP422, reason invalid_signature. Restore pass-mode ingress by
Ctrl+C and a fresh `serve --config configs/ingress.json --out evidence/B02_ingress_01`.
No Pi config or frozen relay changes are required between cases.

B02: before powering Dell off, preserve B01 artifact in controller custody and copy
its exact bytes to Pi as B01_original.json; compare hashes out of band. Retain original
source hash. Record A power-off observation and an actual failed connection to its
known SSH endpoint (e.g. `nc -vz -w 3 10.10.10.10 22` from the controller/approved
management path). A failed probe without the power-off observation is insufficient.
Record old HP verifier PID/instance, stop it by Ctrl+C, retain evidence, and restart:

```sh
# HP verifier terminal
.venv/bin/python -B md001.py serve --config configs/verifier.json --trust trust.json --out evidence/B02_verifier_01
# Pi terminal: re-convey preserved artifact through its running application relay
.venv/bin/python -B md001.py resubmit --artifact B01_original.json --host 30.30.30.30 --port 18081 --out evidence/B02_submit_01
```

Pi's local resubmission is deliberate: A is off, and the original artifact must be
available in independent custody. The relay never creates or signs it. Confirm the
new PID/instance/start time and signature_checks=1, accepted=true, original body hash.
If Pi's local connection policy blocks its own bound listener, resolve that reviewed
local path before scoring; do not alter the code or silently bypass evidence requirements.

## Stop and rollback application deployment

Stop only these foreground processes with Ctrl+C. Preserve all newly written evidence,
configuration copies and hashes, and copy them into new operator evidence directories.
Restore pass ingress after N01 before any B02 attempt. Remove no original evidence.
No network change, boot unit, firmware or ESP state needs application rollback.
If deployment affects an existing service, stop MD001 and investigate; do not stop
unrelated services or rewrite the configured network as an application workaround.
