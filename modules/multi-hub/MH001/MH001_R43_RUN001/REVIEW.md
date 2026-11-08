# MULTI_HUB_001 R4.3 deployment review

LOCAL BUILD ONLY. STOP 1 ACTIVE. No deployment or live readiness is asserted.

This directory is separate from the original R4.3 workspace. `frozen_R43/` is a
byte-identical copy of all 39 original files: runtime source, provider/mint source,
loopback configuration freeze, prior validation records and original SHA256SUMS.
The three additional live-review files are also copied without alteration.
`BASELINE.json` records all those identities and the two added frozen MP005
observer helper identities. Original MH001 and historical MP005/MP006 material
are never written by this package.

## Contents and reuse

| Artifact | Role |
|---|---|
| frozen_R43/hub.py, routes.py, wire.py, requester.py | Unchanged R4.3 routing, framing, requester allowlist and one-send behavior |
| frozen_R43/live_review_R43/ | Exact three verified deployment-review configurations |
| frozen_R43/providers/ | Unchanged provider A/B and their unchanged mint tools; no keys or state |
| frozen_R43/provider_support/ledger_evidence.py | Unchanged ledger validation/bootstrap helper; bootstrap is not called locally |
| observer_support/association_recorder.py | Unchanged MP005 independent Ed25519 recorder, SHA-256 fad60dfc8df53337d2e41288c2c4973442258cae4240945ebbd0aa8920550bfc |
| observer_support/common.py | Unchanged MP005 signed-envelope, correlation, snapshot and replay helpers |
| deployment.py | Frozen identities, isolated paths, approved new public trust and future STOP 1 approval checks |
| provider_launcher.py | MH001-only provider configuration and gated startup; inspect does not import a provider |
| observer.py | Full-session/cursor freshness, direct source and identity/ledger correlation using frozen verification functions |
| observer_launcher.py | Inspection, future recorder startup, checkpoint and verify interfaces |
| configs/ | Proposed provider/observer configurations and deliberately unusable trust/approval templates |
| test_deployment.py, validate_review.py | New offline integration/signature-fixture tests and separate validation records |

The new observer calls unchanged `common.correlate`, `validate_boundary_records`,
`validate_snapshot`, `replay_assertions`, and unchanged ledger `validate_saved`,
`advance_checks`, `replay_checks`. It does not implement another Ed25519 verifier
or provider authorization mechanism. The recorder receives provider-signed
outcomes at the observer directly; hubs handle only opaque request transport.

## Reviewed endpoints and frozen routing

| Role | Listen | Proposed isolated run root |
|---|---|---|
| Hub A / Pi | 192.168.1.100:18080 | Operator-selected new MH001 installation |
| Hub B / Pavilion | 192.168.1.106:18081 | Operator-selected new MH001 installation |
| Provider A / Dell | 192.168.1.118:18090 | /home/seth/MULTI_HUB_001/MH001_R43_RUN001 |
| Provider B / HP | 192.168.1.107:18091 | /home/seth/MULTI_HUB_001/MH001_R43_RUN001 |
| Observer / OmniBook | 192.168.1.102:9191 | C:/Users/holiw/esp32-main/MULTI_HUB_001/MH001_R43_RUN001 |

These roots are explicit proposed targets, not directories created by this build
or claims about host accounts/permissions. Review them at STOP 1. Each machine has
its own filesystem; matching A/B run-root strings do not imply shared authority.
Provider paths also differ by role. On each provider the exact structure is:

```text
<run-root>/
  deployment.py, provider_launcher.py, observer.py, observer_launcher.py
  BASELINE.json, REVIEW.md, configs/, frozen_R43/, observer_support/
  providers/<role>/<role>.py
  providers/<role>/mint_authorization_<a-or-b>.py
  providers/<role>/<role>_issuance_private.pem   [future, provider-controlled]
  providers/<role>/<role>_issuance_public.pem    [future]
  providers/<role>/<role>_private.pem            [future, provider-controlled]
  providers/<role>/<role>_public.pem             [future]
  state/<role>/<role>_consume_ledger.jsonl       [future sanctioned initialization]
  state/<role>/<role>_spent_state.json           [future sanctioned initialization]
  state/<role>/<role>_execution.jsonl            [created by provider execution]
  trust/provider_keys.json                     [future approved public fingerprints]
  evidence/                                    [future exclusive outputs]
```

Bracketed descriptions are not filenames. Actual key/state/provider installation
directories have not been created here. The source and mint files are copied from
their matching frozen role only after approval; no key or state is copied with them.

Hub A routes A directly to Dell and B through Hub B. Hub B routes A directly to
Dell and B directly to HP Provider B. Timeouts remain 15 and 10 seconds. No retry,
alternate routing, failover or shared provider authority is added. Requester remote
approval remains exactly the two reviewed hub endpoints. Existing Pi 8080 and HP
Provider B 9090 processes remain outside MH001 and must stay untouched.

## Provider preparation review — future actions only

1. Obtain explicit STOP 1/operator authorization before any host changes, copying,
   key creation, state initialization, startup, rehearsal or transaction. Recheck
   account/root ownership, Python 3.9+ and cryptography, filesystem persistence,
   port ownership and actual installed hashes. No installation is implicit.
2. Inspect and follow Dell's MP006 indirect autostart chain. It remains unresolved;
   prior flags or lack of a conflicting listener are not proof it is cleared.
   Stop for review if isolation requires changing existing processes/services.
3. Create an exclusive MH001 run root on each approved provider host. Install
   this verified package and copy only that host's frozen provider/mint files into
   providers/<role>/. Verify their exact hashes in SHA256SUMS and the source pins.
   Install no historical key, state, registry or evidence. Do not overwrite a run.
4. Under separately authorized provider-controlled preparation, establish fresh
   Ed25519 issuance and boundary pairs on each corresponding host. No commands
   to generate them have been run here. Private keys stay on their host, owned by
   the provider account and mode 0600 or stricter. Do not transfer private keys to
   hubs/requester/observer. Failed preparation preserves partial files for review.
5. Compute public key IDs using SHA-256 of the raw Ed25519 public key bytes.
   Review all four fingerprints as distinct and new. Publish only these IDs and
   boundary public keys. Complete a new trust/provider_keys.json from the template
   with status APPROVED_PROVIDER_HOST_KEYS. Historical MP005/MP006 fixture key IDs
   are explicitly refused by the launchers. Templates are intentionally not valid
   trust or startup authorization.
6. Authorize new durable state separately, then use only the existing
   frozen_R43/provider_support/ledger_evidence.py bootstrap on that host and the
   specific new state/<role> path. Never call it on recovery/existing history.
   The launcher has no initialize/reset/repair action and requires ledger and
   snapshot to exist. A previously absent execution log is allowed before first
   execution; its parent is the same isolated state directory.
7. Review new source/config/trust hashes and create a separate startup approval
   per configuration from configs/STOP1_APPROVAL.template.json. It binds the
   session, exact config bytes, approved trust bytes and the 11 required runtime
   source dependencies enumerated in deployment.require_approval. No expiration
   field or preparation-duration gate exists. Any change needs renewed review.
8. Only after all approvals may run be invoked on its own provider host:
   `python3 -B provider_launcher.py run --config configs/provider_a.json --approval <approved-A-file>`
   (provider_b config and its approval on HP). These are review templates, not
   current executable approvals. Preserve stdout/stderr, PID/start/boot identity,
   source/config hashes and state paths. Configure no autostart or restart service.

Provider import occurs only after Linux/root/source/mint/trust/key/path/permissions
and existing-state checks. Its original imports load the new keys beside its
source. The only overrides are HOST, PORT, ASSOCIATION_URL, CONSUME_LEDGER_PATH,
SPENT_STATE_PATH and EXECUTION_LOG_PATH. Key paths and all verification, ledger,
snapshot reconciliation, signing and execution functions remain unchanged.
Frozen provider startup may reconcile a snapshot under its original policy; stop
for review and preserve raw state if anything unexpected occurs. Do not add repair.

## Observer preparation review — no startup performed

On OmniBook, create only a newly approved MH001 observer run after STOP 1. Place
the new boundary public keys at association/trust/provider_a_public.pem and
provider_b_public.pem. Complete association/provider_registry.json from the public
registry template; each key ID must equal the newly approved trust manifest.
The registry accepts only those two exact relative public paths. Do not import a
historical registry. No signing private key belongs on the observer.

The future observer `run` action requires its own approved source/config/trust
hashes and exact isolated installation root. It configures only the frozen
recorder's HOST, PORT and existing session/registry/manifest/contract/log CLI.
It retains original Ed25519 checking, raw envelopes, hash-linked session records,
exclusive log handling and orderly SESSION_END. No observer server was started.

Prior to each sequential controlled send, use observer_launcher's `checkpoint`
action with --identity (provider/authorization/nonce/operation/binding), --before
(independently captured provider snapshot folder), --mode fresh or replay and a
new --output path. It requires complete hash-verified session prehistory beginning
at SESSION_START, source/config/registry identity agreement, and a log cursor.
For both T03 cases it refuses any matching previous DENY anywhere in prehistory.
For fresh authority it refuses any previous matching signed outcome.

After the send and a new provider state capture, `verify --checkpoint ... --after
... --output ...` rechecks the continuous log prefix, actual Ed25519 signature,
provider/key/nonce/operation/binding, direct provider source address, signed ledger
sequence/head and durable state. T03 requires exactly one new DENY/auth_spent,
unchanged consumption and execution, and no START/COMPLETE for each provider.
Fresh mode requires new START/COMPLETE and exactly one ledger/execution advance.
Checkpoints and results use exclusive writes. A result says VERIFIED_PROVIDER_OUTCOME,
not scored-case PASS: independent fresh ingress evidence and the other frozen
T01–T04 operator/scorer requirements remain mandatory. Hub HTTP responses are
never used to infer execution. A source IP is corroboration, not cryptographic
identity; signature verification remains decisive for provider identity.

## Safe local inspection commands

From this deployment-review directory, issue one command and inspect output:

```powershell
python -B provider_launcher.py inspect --config configs/provider_a.json
```

```powershell
python -B provider_launcher.py inspect --config configs/provider_b.json
```

```powershell
python -B observer_launcher.py inspect --config configs/observer.json
```

These only inspect configuration/source identities. They do not import providers,
load keys, create state or bind ports. Missing future trust/state is expected.

The three original live-review hashes are recorded verbatim in HASHES.json and
verified independently by deployment.verify_baseline. The original config freeze
continues to describe the prior loopback configurations; it has not been relabeled
as a live freeze. No original R4.3 file is overwritten.

## Validation and remaining STOP requirements

The original 29 tests are rerun from copied source and recorded separately from
the new deployment tests. Original validation records remain under frozen_R43.
validation/attempt-001 preserves the Windows sandbox socket denial and initial
Windows command-line guard issue; later attempts do not overwrite that record.
Use the latest passing validation record identified in HASHES.json.

Actual live-review configs are exercised together using the unchanged Handler,
wire and requester code with in-memory endpoint transports. Those tests never
connect to their numeric lab addresses. Original transport tests use loopback
mock sockets only, including two local hub subprocesses and the 10-second timeout.
An audit guard rejects nonloopback connects/binds, provider imports and unapproved
subprocesses; child hubs are restricted to verified loopback configs. Observer
startup, provider bootstrap and Ed25519 key generation are additionally blocked.
Observer fixtures use fixed published RFC 8032 vector seeds 1/2 loaded in memory;
no new real or mock signing key is generated and no private PEM is written.
These are temporary synthetic fixtures, not provider state or run evidence.

STOP 1 remains active. Remaining live checks include actual installed source/config
identities and nonconflicting listeners; Dell autostart chain; independent ingress
capture reconstructing complete requests; sanctioned new trust/state; observer
readiness; and separately authorized rehearsal latency. Preserve Pi 8080 and HP
9090, all historical directories and failures. If isolation needs a live change,
stop for review. No SSH or host changes have been performed by this build.

STOP 2 remains explicit approval immediately before terminating only the designated
MH001 Hub A PID during T02. Confirm no supervisor restarts it, and keep Hub B,
providers and observer running. Frozen T03/T04 evidence must establish Hub A remains
absent. T03 must not reuse old Provider B ingress or an earlier signed denial.
Timeout/lost reply is incomplete execution evidence; never retry automatically.
During an authorized rehearsal, stop/reassess when responses approach/exceed the
existing 8-second review threshold before scored use. This is not a local-live
readiness claim.

The only successful local completion label is:
LOCAL_DEPLOYMENT_PACKAGE_VALIDATED_NOT_DEPLOYED.
