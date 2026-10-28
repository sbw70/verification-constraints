# MP005 Live Contract - Locked Definition

Primary scored claim: Across an idle forced process restart of the same hardened provider runtime using the same durable consumption ledger and materialized snapshot, consumed authorization remains spent. Exact replay is denied auth_spent without another consumption entry or execution. Different fresh authority remains usable, appends exactly one valid linked ledger entry and executes once.

Only R01_PROVIDER_A_RESTART_DURABILITY and R02_PROVIDER_B_RESTART_DURABILITY are live scored cases. Local R3 safe-forward/ahead/divergence results are supporting characterization, not additional scored live rollback cases. Provider-exclusive authority is unchanged; association/verifier remain evidentiary. Signed boundaries bind current ledger_seq/head.

Independent review of the local Linux R3 simulation validates exact/same-state restart, valid genesis-prefix recovery, missing/malformed ledger fail-closed behavior, ahead snapshot refusal and equal-seq head/spent divergence refusal. Full source semantics additionally define missing cache recovery, malformed bytes preserved before recovery, older non-prefix/invalid parseable/unreadable snapshot refusal; these are code/offline supported rather than additional R3 runtime experiments.

Final criteria require proven consume before IDLE/manual termination, genuinely new process instance on same host/boot/runtime/paths/command, exact replay bytes, independently verified signed auth_spent, no replay ledger/state/execution changes or START/COMPLETE, one linked fresh consume/execute, late-event checks and preserved, SHA-256-inventoried evidence. No HTTP 204 completion inference. Process-local EXECUTION_SEQ continuity is not scored.

Rollback of BOTH ledger and snapshot to an older mutually consistent history remains outside established protection. No automatic remote-head authority or freshness enforcement. No concurrency, power-loss, crash-window, reboot or physical-actuation claim.

Final verified machine map, roots/URLs/state/ledger/log/transfer paths and candidate manifests must be resolved before locking. No current live IP/path is invented here. No rehearsal/scored phase is authorized by this proposal. Final locked material must include classifications/stop rules, current identities, chosen transport and phase/session gating from the reviewed operator packet.

## Verified deployment topology

Provider A: Dell Xer0trust-3, 192.168.1.118, TCP 9090.
Provider B: HP Mint Xer0trust2, 192.168.1.107, TCP 9090.
Relay: Raspberry Pi nuvl-relay, 192.168.1.100, TCP 8080.
Association and controller: OmniBook Xer0trust, 192.168.1.102, TCP 9191.
Pavilion xer0trust-4 is excluded from live execution.

Relay endpoint: http://192.168.1.100:8080/nuvl
Provider A ingest: http://192.168.1.118:9090/ingest
Provider B ingest: http://192.168.1.107:9090/ingest
Association endpoint: http://192.168.1.102:9191/boundary

These are the locked intended endpoints. Service-to-service
reachability and runtime compatibility remain preflight requirements.

## Rehearsal state and evidence

Session: MP005_PREFLIGHT_20261022_R1

Provider A state:
/home/seth/MULTI_PROVIDER_005/live_state/rehearsal/provider_a

Provider B state:
/home/seth/MULTI_PROVIDER_005/live_state/rehearsal/provider_b

Controller evidence:
evidence/preflight/MP005_PREFLIGHT_20261022_R1

Association log:
evidence/preflight/MP005_PREFLIGHT_20261022_R1/association/recorder.jsonl

The association recorder creates the log. It must not exist before
recorder startup. Controller correlation uses the continuously
accessible local file.

Provider evidence is transferred by operator-controlled SCP.
Raw evidence and SHA-256 identities must be verified after transfer.
Existing destinations must never be silently overwritten.

Scored execution requires separate authorization, session identity,
state histories and evidence paths following rehearsal review.

## Authorization and stop conditions

This locked definition does not authorize service startup, state initialization,
live preflight, rehearsal or scoring.

Final manifests, contract and canonical lock must be reviewed and
verified on the relevant machines before live execution.

Any identity, configuration, state, transport or evidence mismatch
requires stopping and preserving the observed results.

## MP005 scored-session deployment correction (superseding lock)

This revision supersedes the previous canonical lock ONLY for a future, separately
approved scored session. The original canonical lock (SHA-256
08039d757d20ad9f111427779a8ec9276f5ecbf90f313f7b2b18c6b975c52b36)
remains the reference for the completed physical rehearsals. The earlier
"Rehearsal state and evidence" section records preflight/rehearsal deployment
and must not be treated as the location of scored state.

The accepted physical rehearsal was session MP005_REHEARSAL_20261024_R1.
The evidence and its operator-acceptance record remain at their original paths
and are NOT revised, replaced, or relabeled by this addendum. Historical
NOT_RUN markers in the original manifest are planning-time placeholders;
rehearsal outcomes are determined from preserved case_results.json and the
separate operator-acceptance record, not by retroactively rewriting history.

For THIS revision, `deployments.provider_a` and `deployments.provider_b`
in MP005_RUN_MANIFEST.json designate SCORED execution, not rehearsal:

- Provider A (Dell 192.168.1.118):
  `/home/seth/MULTI_PROVIDER_005/live_state/scored/provider_a`
- Provider B (HP 192.168.1.107):
  `/home/seth/MULTI_PROVIDER_005/live_state/scored/provider_b`

The corresponding `<provider>_consume_ledger.jsonl`,
`<provider>_spent_state.json`, and `<provider>_execution.jsonl` reside
inside each scored directory. Those directories MUST be absent before
explicit new-state bootstrap and must be distinct from existing rehearsal
state directories. The scored controller evidence is
`evidence/scored/<authorized-new-session-id>`, with a NEW association log at
`evidence/scored/<authorized-new-session-id>/association/recorder.jsonl`.
No historical evidence may be renamed, reset, copied forward as fresh scored
state, or overwritten. No scored HTTP request is authorized by this addendum.

The frozen provider implementations and harness, authority boundary, ledger
algorithm, signature rules, R01/R02 case behavior, operator-only forced kill,
classification/stop rules, and exclusions/limitations remain unchanged.
Before use: validate this amended canonical lock and matching on-host copies;
record a current scored readiness reconciliation rather than rewriting stale
pre-lock readiness records; confirm new-state destinations do not exist;
confirm the old rehearsal services are deliberately and cleanly stopped;
verify exact original source/key/registry/trust identities on all roles;
and obtain a NEW explicit scored session authorization referencing accepted
rehearsal and THIS revision's canonical lock. The previously recorded
MP005_SCORED_20261025_R1 authorization bound to the old lock is superseded
and MUST NOT be used. Human remains responsible for manual restart and kill.

No scored campaign is reported as run or passed by this correction.
