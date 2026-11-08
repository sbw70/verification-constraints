# Remaining live prerequisites and frozen scoring

Status: local build only. No lab-host action is authorized by these instructions.

## Before STOP 1

- Obtain authorization for the read-only host preflight. Inventory actual
  addresses, Python versions and existing dependencies on the Pi, Pavilion,
  Dell, HP 14, and controller/observer as relevant. Inspect processes, listener
  ownership, system and user startup services, enabled units, cron/login and
  desktop autostart launch chains. Follow indirect launchers. In particular,
  identify any MP006 Dell provider/restart/autostart service and its port/state
  ownership. Historical `autostart_reviewed_disabled: true` is not current proof.
  Do not stop, disable, reconfigure, or repair an existing service.
- Select nonconflicting MH001 listen endpoints, provider endpoints, isolated
  paths, and observer endpoint. Confirm existing network reachability/permissions
  only under authorized preflight. No network changes are included. If isolation
  would require a live-service change or dependency installation, STOP for direction.
- Review the provider-host setup/launcher, new trust registry, and sanctioned
  state initialization described in `PROVIDER_PREPARATION.md`. Actual keys stay
  on their respective provider-controlled hosts. Preserve all MP005/MP006 data.
- Confirm actual installed provider source hashes against the frozen local and
  recorded published identities. Confirm that X-MH-Destination is ignored and
  Host is not in actual provider binding. STOP on any discrepancy.
- Replace the local loopback configuration endpoints only in new reviewed
  deployment configuration files. Each hub has its own static route file;
  validate both together and review source/timeout/topology. Host identifiers
  use numeric literals and exact endpoint identities to avoid aliases/DNS routing.
  Listen addresses are explicit unicast interfaces, not wildcard addresses.
  The new code needs Python 3.9+; check actual versions without installing anything.
- Review the requester source and separate `configs/approved_hubs.json` (currently
  empty). After authorized address verification, approve only exact literal hub
  IP/port entries, hash that list, and use `send --approved-hubs <reviewed-file>`.
  Without that option only loopback is allowed. No code change or blanket remote
  bypass is needed. Hub route files are never read by the requester. Preserve
  complete request bytes, one send, exclusive receipts, and no signing authority.
- Establish passive requester/provider-ingress capture using already available,
  reviewed facilities; no provider security-path hooks or new dependencies.
  Confirm capture can reconstruct each complete HTTP request, raw body hash,
  preserved header-value hashes, and fresh ingress instance, including Provider
  B T03. Hub logs alone are insufficient. Keep full authority out of hub logs;
  provider/requester evidence is controlled separately.
- Establish a dedicated observer session using the new public trust. Reuse
  established independent signature/ledger verification, adapting session and
  evidence collection only. Review this adaptation before any rehearsal/run.
  Freeze the exact replay outcome for **both providers** as `DENY / auth_spent`.
- Hash all new source/configuration/observer artifacts. Preserve a reviewed
  inventory and **both configuration hashes** before requesting STOP 1 approval.
  `SHA256SUMS.txt` freezes this local package, not future live addresses. Any
  later source/configuration/timeout change requires new hashes and renewed
  STOP 1 approval; no mid-run changes are allowed.

**STOP 1:** explicit operator approval before live deployment, rehearsal, or
execution. Host setup/key generation also needs the separate authorization
described above. No live-machine action has been taken by the local build.

During a separately authorized rehearsal, measure full provider response
latency, including the Dell durable ledger/snapshot/execution writes and observer
delivery waits. Hub B downstream timeout is fixed at 10 seconds, Hub A at 15.
If responses approach or exceed 8 seconds, STOP and reassess before any scored
run. A timeout or lost reply never proves execution or nonexecution; do not retry.

## Frozen T01–T04 and decisive evidence

Start only with reviewed frozen route/source identities, new approved trust/state,
provider/observer readiness, complete capture facilities, and known execution and
consumption baselines. Submit operations sequentially. Never infer execution
from HTTP status or a hub result record.

| Test | Action | Required provider evidence per provider |
|---|---|---|
| T01 | Two distinct provider-scoped issued authorizations through Hub A; A direct, B through Hub B | Fresh ingress, matching immutable body/header evidence, signed START/COMPLETE verified independently, exactly one execution/consumption advance, authority SPENT |
| T02 | Stop only the designated MH001 Hub A process after STOP 2 approval | Hub A process and listener absent, Hub B available, both provider histories/consumption states unchanged |
| T03 | Send the exact preserved T01 requests directly through Hub B | Fresh provider ingress; freshly observed signed `DENY / auth_spent`, authority/nonce/binding/operation/provider key and ledger head match; zero new execution/consumption |
| T04 | Reconfirm Hub A process/listener remain absent; send separately issued fresh authority through Hub B | Fresh ingress, independently verified signed START/COMPLETE, exactly one new execution/consumption each |

**STOP 2:** obtain explicit approval immediately before terminating the designated
Hub A process in T02. Record its PID/start identity and source/config/log identity
before stopping. Confirm no supervisor restarts it. Stop no other process or host.
The mock suite's teardown of its own temporary hub subprocesses is unrelated to
this scored control.

For T03, before each submission preserve the continuous observer-log cursor and
verify that **no matching denial already exists anywhere in the preserved session**.
Missing/incomplete prehistory cannot prove absence. After submission require a new
record beyond that cursor, independently verify its Ed25519 signature using the
approved provider public key, and match authorization ID, nonce, provider/key ID,
operation ID, binding and expected `auth_spent` reason. Verify its ledger sequence/
head against captured provider state and verify unchanged ledger/execution history.
Correlate the new request with fresh provider ingress; Provider B's old T01 ingress
or a previously saved denial cannot satisfy T03. Its local ingress/capture identity,
observer cursor, and Hub B sequence distinguish an exact replay without changing
the authority bytes. Do not require synchronized clocks; timestamps only support
the ordering established by captures/cursors and sequential orchestration.

For each route, compare requester raw body hash, each hub's ingress/egress hashes,
and provider-ingress hash. Provider B's chained path requires six body observations,
including both hubs separately. Preserve corresponding opaque-header hashes and
method/path/query evidence at requester/provider boundaries. Check no duplicate
delivery or extra execution and no hub execution-state retention. A hub transport
failure leaves provider outcome unknown until independently resolved by evidence.

PASS requires all routes, immutable bytes, fresh ingress, exact verified decisions,
and expected execution/consumption deltas. FAIL means verified unauthorized
execution, accepted replay, duplicate execution, or altered authority. INCOMPLETE
means missing decisive evidence, unexpected denial reason, ambiguous delivery,
changed configuration, or unmet preconditions. Generic denial, `policy_denied`,
`auth_bad_sig`, `auth_ledger_error`, or `auth_snapshot_error_consumed` is not T03 PASS.
Preserve failures and stop; never reset/repair state or rewrite evidence.

Provider-signed decisions travel independently to the observer. Provider-outcome
relay through hubs is excluded from MH001 scoring and remains MH002.
