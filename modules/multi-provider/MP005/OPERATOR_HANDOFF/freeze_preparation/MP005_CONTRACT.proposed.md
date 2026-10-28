# Proposed narrow live contract — R3 validated, NOT FINAL/LOCKED

Primary scored claim: Across an idle forced process restart of the same hardened provider runtime using the same durable consumption ledger and materialized snapshot, consumed authorization remains spent. Exact replay is denied auth_spent without another consumption entry or execution. Different fresh authority remains usable, appends exactly one valid linked ledger entry and executes once.

Only R01_PROVIDER_A_RESTART_DURABILITY and R02_PROVIDER_B_RESTART_DURABILITY are live scored cases. Local R3 safe-forward/ahead/divergence results are supporting characterization, not additional scored live rollback cases. Provider-exclusive authority is unchanged; association/verifier remain evidentiary. Signed boundaries bind current ledger_seq/head.

R3 independently validates exact/same-state restart, valid genesis-prefix recovery, missing/malformed ledger fail-closed behavior, ahead snapshot refusal and equal-seq head/spent divergence refusal. Full source semantics additionally define missing cache recovery, malformed bytes preserved before recovery, older non-prefix/invalid parseable/unreadable snapshot refusal; these are code/offline supported rather than additional R3 runtime experiments.

Final criteria require proven consume before IDLE/manual termination, genuinely new process instance on same host/boot/runtime/paths/command, exact replay bytes, independently verified signed auth_spent, no replay ledger/state/execution changes or START/COMPLETE, one linked fresh consume/execute, late-event checks and immutable evidence preservation. No HTTP 204 completion inference. Process-local EXECUTION_SEQ continuity is not scored.

Rollback of BOTH ledger and snapshot to an older mutually consistent history remains outside established protection. No automatic remote-head authority or freshness enforcement. No concurrency, power-loss, crash-window, reboot or physical-actuation claim.

Final verified machine map, roots/URLs/state/ledger/log/transfer paths and candidate manifests must be resolved before locking. No current live IP/path is invented here. No rehearsal/scored phase is authorized by this proposal. Final locked material must include classifications/stop rules, current identities, chosen transport and phase/session gating from the reviewed operator packet.
