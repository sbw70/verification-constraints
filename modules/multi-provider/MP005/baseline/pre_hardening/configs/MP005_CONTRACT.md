# MP005 — Provider Restart Durability

Status: DRAFT CANDIDATE. Simulation review pending. No live lock, rehearsal or scored result.

## Primary claim

"In the tested implementation, when the same durable provider state is preserved across a forced process restart performed while idle, previously consumed provider authorization remains spent: exact replay is denied without another execution, while fresh valid provider authorization remains usable after restart."

The supporting source statement is that each frozen provider loads its durable spent-state file before constructing its request server. Source ordering alone is not durability proof.

## Baseline and topology

Use byte-identical MP003 at fa541618b1a3bc58700a81b29129b17b35b1e0fc. Implementation manifest records exact sources/keys; harness code is separately inventoried. Corrected registry SHA256 is 59d739588427d87313e3434982d943a9c82bad26c3fe3deb7d5488efadb6088d; only the handoff transcription was corrected.

Eventual live topology remains requester/operator -> relay -> independent A/B -> association. During each restart the relay, recorder and non-target provider remain running. Only the target provider is forcibly terminated while idle. Live machine addresses and deployed paths must be reverified during later authorized preflight; none were contacted during this build.

## Only two scored cases

R01_PROVIDER_A_RESTART_DURABILITY and R02_PROVIDER_B_RESTART_DURABILITY each contain: (1) deterministic request/context with fresh provider-specific issued authorization; (2) normal consume through relay, verified signed START/COMPLETE and local execution/spent evidence; (3) pre-restart process/state/platform snapshot while idle; (4) mandatory operator checkpoint, forced termination by the operator, and manual restart of the same runtime against the same state directory; (5) objective restart proof; (6) exact replay and signed DENY auth_spent with unchanged state/log; (7) fresh request/context/authority executing successfully. Incidental non-target auth_missing fan-out denial is not a property failure. No independent baseline/final-health scored cases.

## Identity, restart and replay assertions

Capture hostname, OS/Python/executable, PID, process command/start time/start ticks/boot identity, cwd, runtime resolved path/hash, state resolved path, filesystem/mount, raw spent/log files and their hashes/lengths/counts/authority membership. Restart must be a different process instance with a later process start on the same host/boot, same runtime path/hash and state path. Failure to establish these prerequisites yields PRECONDITION_NOT_MET, not a scored property result. Command/cwd consistency is also checked by the candidate harness.

Replay reads original preserved request bytes, context and exact encoded/decoded authorization; it never remints an equivalent token. Byte/hash checks bind these files before each send. Correlate only records after a preserved recorder-log cursor, using provider + authorization ID + operation ID, binding, nonce, signature and key. Earlier START/COMPLETE for the original operation must not be mistaken for replay events. Relay HTTP 204 is receipt only. Wait boundedly for explicit correlated evidence; a timeout prevents progression to restart.

Across replay require target ID still present; spent SHA/byte length/count unchanged; execution SHA/byte length/line count/matching authority count and log presence unchanged; exactly the target signed DENY auth_spent; no target START/COMPLETE or new execution. Record telemetry sequence reuse but do not score continuity. Fresh health must have a distinct authorization, signed START/COMPLETE, one new spent entry and one new execution. Verify snapshot JSON against preserved raw files before final scoring. Per-assertion output is case_results.json.

## Scoring and checkpoints

States: PASS, FAIL, HARNESS_ERROR, PRECONDITION_NOT_MET, NOT_RUN. Second execution from exact replay is FAIL. Wrong file/changed preserved bytes or malformed evidence is HARNESS_ERROR. Unconsumed initial authority, unproven restart, mismatched deployed runtime or missing completion evidence is PRECONDITION_NOT_MET. No ambiguity is PASS. No live code contains an automatic kill/restart operation; checkpoint output is instructions only. The operator establishes the exact forced-termination command during authorized preflight, independently confirms idle, kills the target, and manually repeats its captured launch command. Capture process/state evidence after restart before replay.

## Local characterization and gates

S00 normal forced idle restart/replay/fresh; S01 missing state; S02 structurally invalid spent container; S03 deliberate valid-old-state substitution. All run for each provider sequentially on approved LOCAL Linux, exclusively with numeric loopback URLs and disposable state under evidence/simulated_smoke/. Entry point refuses non-Linux before importing/starting a provider or creating a run. Unchanged source is imported by a configuration-only wrapper overriding association URL, listen address/port and state/log paths; no persistence shim, monkeypatch or fsync substitution. A loopback-only relay route and simulation-only raw recorder exercise asynchronous delivery without the laboratory hosts. Every simulation case has separate artifacts and inventories. S03 reports actual behavior, including any regained authority; it is not a failure of MP005's same-state restart claim and does not establish rollback resistance. Stop for review afterward.

Phase 1 builds tools and drafts only. S00-S03 NOT_RUN in this Windows build. Linux execution still requires a later approved local environment. Live rehearsal needs later explicit instruction after simulation review. Scoring needs a separate later instruction after rehearsal review. Publication needs review of scored results. No automatic phase advancement and no final live lock now.

## Limits

No rollback, deletion, corruption, hostile-filesystem, crash-window, kill-during-consume, power-loss, host-reboot, cross-provider atomicity, global chronology, physical-consequence, boundary-key-compromise or implementation-diversity claim. Filesystem behavior is scoped to the actually tested platform. Laboratory keys remain intentional reproducibility material. Hash inventories are integrity records, not independent trust anchors. The association is evidentiary and does not authorize execution.
