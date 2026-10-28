# MP005 execution handoff — R3 validated, live BLOCKED

Read START_HERE.md, READINESS.json and STOP_CONDITIONS.md first. Give ONE terminal command per turn, name the exact verified machine/window, and wait for pasted output. No live phase is authorized by R3 passing.

## Definition and implementation

There is no final locked live claim yet. Proposed narrow R01/R02 claim: Across an idle forced process restart of the same hardened provider runtime against the same durable ledger and snapshot, consumed authorization stays spent; exact replay is denied auth_spent without another consume or execution, while different fresh authority adds one valid linked ledger entry and executes once. Snapshot-prefix recovery/ahead/divergence results are supporting LOCAL R3 characterization, not extra scored live cases.

R3-validated A SHA-256: 79e4994c955ca842af04a8fd650a33d49de040bab95b821ded9e63e16866f2b6
R3-validated B SHA-256: 618ec76ef5dd3bfa3ba7b1ad3941ed0516a7511b72957d7efb82ec565905b605
Prior R2 identities, MP003 baseline identities, exact R2-to-R3 diffs and candidate config hashes: CANDIDATE_IDENTITIES.json and simulation_review/R3_SUMMARY.json. Only load_spent_state changed and classify_snapshot, preserve_malformed_snapshot, reject_json_constant were added in each provider; other function/module ASTs match R2. Relay/association/consume/signature logic unchanged. Final contract/run-manifest hashes remain absent.

Provider alone validates and consumes its own authority and decides execution. Relay forwards; association verifies/preserves signed evidence, does not grant execution authority. Every signed boundary includes current ledger_seq/head; signature covers those fields. Ledger is domain-separated SHA256-linked canonical JSONL, provider-specific, contiguous 1..N, unique authority IDs. Consumption append/flush/fsync precedes in-memory update, atomic snapshot persistence, START and execution. Append uncertainty latches auth_ledger_error; durable append with snapshot error denies auth_snapshot_error_consumed without undoing consumption.

## Completed local review

All 12 A/B S00–S05 cases independently PASS, including S05 head-only and spent-only variants. Raw hashes/inventories, 28 snapshots, full ledger chains, signatures, exact replay bytes and distinct/newer process identities checked. S00/S03 replay = 0 ledger entries/0 execution and no START/COMPLETE; fresh = +1/+1. S04 snapshot seq1 versus valid ledger seq0 failed snapshot_ahead_of_ledger, preserving both. S05 seq1 head divergence or spent divergence separately failed snapshot_equal_seq_divergent, preserving both. S03 recovered valid genesis prefix, logged valid_prefix_behind, kept original authority spent. R1/R2/R3 unchanged. No scored evidence under local evidence tree.

Exact state match accepted. Only a verified prefix safe-forwards. Missing cache rebuilds from valid ledger. Malformed JSON is durably archived verbatim before documented recovery; parseable invalid schema/history and unreadable files fail closed. Missing/malformed cache persistence paths and older non-prefix refusal are code/offline supported, not additional R3 Linux startup cases. Do not present them as runtime observations. No full-history rollback freshness guarantee: replacing BOTH ledger and snapshot with an older mutually consistent pair remains outside established protection. Process-local EXECUTION_SEQ can repeat and is not scored. No concurrency/power-loss/crash-window/reboot/physical-actuation claim.

## Machine facts and paths

Provider A = Dell Linux. Provider B = separate HP/Mint. Relay = Pi3. Association/operator = OmniBook, actual service placement/platform to verify. Pavilion/xer0trust-4 is simulation-only, excluded from every live role. Current live hostnames/IPs and paths are UNVERIFIED. DISCOVERY_NEXT.md is a later authorized host-local collection sequence; never infer old IPs. No live preflight/discovery was performed during this review.

Record actual root on each machine, runtime path/hash, provider state/ledger/execution paths, relay ingest routing, association registry/trust/log, and continuous prefix-preserving association-to-controller log transport. Provider filenames: provider_a_consume_ledger.jsonl / provider_a_spent_state.json / provider_a_execution.jsonl, and provider_b equivalents. No parent directory is known yet. Association convention is <verified association root>/evidence/<preflight-or-scored>/<SESSION>/association.jsonl; actual placement is a preflight fact, not invented.

Evidence templates: evidence/preflight/MP005_PREFLIGHT_YYYYMMDD_R1/R01 or R02; evidence/scored/MP005_SCORED_YYYYMMDD_R1/R01 or R02. Actual dates only. Never reuse output/state directories; no resetting rehearsal history into scored state. New session authorization records phase/session; scoring additionally references accepted rehearsal. Locked manifest status later may be LOCKED_LIVE_DEFINITION; canonical configs/MP005_LOCK_SHA256SUMS.txt binds final files. No lock or authorization is supplied now.

## R01/R02 and scoring

R01 targets A; R02 B. Prepare original request/context/authority once. Capture pre-consume, signed START/COMPLETE, raw consumed ledger/state/log and process-before. Check one valid ledger consume/execute before permitting IDLE checkpoint. Human independently confirms no in-flight request, manually SIGKILLs exact provider, and manually restarts exact runtime/argv/cwd/state/ledger. Relay, association and non-target remain running. New process must share host/boot/paths/hash/argv/cwd, have different PID/start tuple and later start ticks.

Replay exact preserved bytes only after that proof. Require one signed DENY auth_spent, no START/COMPLETE, unchanged ledger bytes/hash/lines/count/seq/head, unchanged snapshot/execution and spent membership. Then different fresh authority must preserve ledger prefix, append one valid next entry linked to prior head and execute once, with signed expected head. Correlate provider_id + authorization_id + operation_id, binding/nonce/key, and independently verify signature. HTTP 204 is transport receipt only. Recheck late events in continuous association log and original execution count through final fresh capture.

PASS requires every locked condition. A valid property contradiction is FAIL; unmet machine/path/process/consume prerequisites are PRECONDITION_NOT_MET; tooling/copy/correlation ambiguity is HARNESS_ERROR. Preserve all misfires and partial evidence, stop on non-PASS, never clean or silently retry inside a scored campaign. Human performs every connection, terminal action, copy, IDLE confirmation and termination/restart. R01_PROVIDER_A_RUNBOOK.md / R02_PROVIDER_B_RUNBOOK.md and LIVE_COMMAND_TEMPLATES.md remain gated preparation templates until final verified lock. POST_RUN_AUDIT.md is read-only preservation/audit guidance.
