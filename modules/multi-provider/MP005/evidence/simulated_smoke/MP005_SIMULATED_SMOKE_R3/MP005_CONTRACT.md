# MP005 hardened draft contract

Status: DRAFT — R2 reviewed for its earlier implementation; R3 NOT_RUN for the patched reconciliation candidate. No live freeze.

## Proposed claim, subject to Linux R2 verification

In the tested implementation, provider authorization consumption is recorded in a durable hash-linked provider-local ledger before execution. Across an idle forced process restart, previously consumed authority remains spent. Rolling back the materialized spent-state snapshot alone does not resurrect consumed authority because provider state is reconstructed from the validated consumption ledger.

Provider-signed boundary events commit to the provider's current consumption-ledger sequence and head for audit correlation.

## Scope and identities

The MP003 baseline at fa541618b1a3bc58700a81b29129b17b35b1e0fc is preserved under baseline/pre_hardening. MP005 provider A/B intentionally differ. Relay, association, minting tools, registry and keys remain unchanged. SOURCE and IMPLEMENTATION manifests record both identities.

R1 remains characterization evidence. Its S03 PASS means the characterization completed, including a second execution after snapshot rollback; it is not a rollback-resistance pass. Do not reinterpret or overwrite R1.

## Authoritative history and signed commitments

Each provider requires its existing canonical JSONL consume ledger. Validate the entire ledger before binding the HTTP server. Missing or invalid ledger aborts startup without initialization or repair. Derive SPENT and ledger_seq/head from validated entries. Snapshot version 1 contains spent, ledger_seq, ledger_head and is a cache only. Exact snapshot agreement is accepted. Only a snapshot whose sequence/head/spent map exactly matches a validated ledger prefix may safe-forward, with reason valid_prefix_behind. A missing snapshot is rebuilt with reason missing_snapshot. Malformed JSON bytes must first be durably preserved under a content-addressed .malformed.<sha256>.bin filename; preservation errors abort startup. Parseable invalid structures, ahead snapshots, equal-sequence divergence and older non-prefix state fail closed without changing ledger or snapshot. Unreadable snapshot fails closed. Safe recovery writes remain atomic and file/directory-fsynced before serving.

Fresh consume is serialized with STATE_LOCK: check spent, append one hash-linked entry, flush/fsync ledger, update in-memory history, atomically persist the matching snapshot, then permit START and execution. Append uncertainty latches auth_ledger_error for the process; no truncation or automatic repair. Durable append followed by snapshot error denies with auth_snapshot_error_consumed; authority remains spent and retry denies auth_spent. No START/execution is permitted for either failure.

Every signed START, COMPLETE and DENY carries the current ledger_seq/head. In sequential R3, START/COMPLETE must equal the consumed entry's sequence/hash. Association verifies the full canonical event and retains raw bytes; extra fields do not enlarge execution authority.

## Local Linux R3 requirements

Run MP005_SIMULATED_SMOKE_R3 once into a new directory, with numeric loopback only. Never overwrite or modify R1, R2, or existing R3 evidence. Provider force-termination is allowed only while idle, after signed COMPLETE and captured execution/ledger evidence. Prove a later process instance on the same boot, runtime, paths and command.

- S00: empty ledger/snapshot bootstrap; consume; idle forced stop and restart; exact replay denies auth_spent with no START/COMPLETE and unchanged ledger, snapshot and execution bytes; fresh authority adds exactly one valid linked entry and executes once.
- S01: ledger absent, snapshot present; startup fails, no server or implicit ledger.
- S02: malformed ledger; startup fails, no server or repair. Offline checks separately cover hash/chain/provider/version/sequence/duplicate defects.
- S04: valid snapshot ahead of shorter valid ledger fails startup; both inputs preserved.
- S05: equal-sequence divergent head and divergent spent map separately fail startup; both inputs preserved.
- S03: consume X to L1/S1; preserve L1 and restore only old S0; idle restart reconstructs X from L1 and logs snapshot recovery before serving; exact replay denies, changes no ledger/execution, fresh authority advances once.

Require raw snapshots, ledger hashes/lengths/line counts/entry counts, independently validated chains, authorization membership, snapshot/head agreement, exact request/authority bytes, process identities and independently verified signed boundary events. Relay 204 is transport receipt only. The simulation recorder is a loopback raw collector, not the published association runtime; recorder compatibility is checked separately offline against unchanged association code.

## Limitations and gates

MP005 does not establish resistance to rollback of the entire local provider history, including both the consumption ledger and its materialized snapshot. Externally preserved signed ledger-head evidence provides a comparison point but is not used in this test as a remote execution-authority check.

Only one provider process per state directory. No host reboot, power loss, concurrent-consume, crash-window, physical-actuation or remote-witness-enforcement claim. Execution sequence remains process-local telemetry and may repeat after restart.

Windows execution refuses before provider import/start. No persistence shim. Linux environment/access limitations are not provider failures. No live contact, rehearsal, scored run, GitHub mutation, or final live lock is authorized. Mandatory STOP for operator review after R3. R2 does not validate the patched provider identities.
