# MP005 hardening implementation facts

Baseline provider implementation facts are historical in baseline/pre_hardening/notes. The current providers intentionally differ from MP003.

Ledger paths: provider_a_consume_ledger.jsonl / provider_b_consume_ledger.jsonl in the selected state directory. JSONL canonical UTF-8, sort_keys=True, separators=(",", ":"), ensure_ascii=False, allow_nan=False, newline-terminated. Fields: version=1, provider_id, ledger_seq (strict integer 1..N), authorization_id, authorization_nonce, operation_id, previous_entry_hash (null at genesis), entry_hash. Hash = SHA256(b"NUVL-MP-CONSUME-LEDGER-v1|" + canonical(entry without entry_hash)). Empty ledger has seq 0 / head null. Reject duplicate JSON keys, noncanonical/truncated/blank lines, wrong provider/version/sequence/link/hash, empty identities, and duplicate authorization IDs. Validate all entries before server creation.

State source, consume ordering, recovery and failure reason codes are specified exactly in configs/MP005_CONTRACT.md and implemented identically in both provider persistence blocks. Bootstrap is an explicit Linux-only harness/ledger_evidence.py command and refuses existing ledger or snapshot. Normal startup never creates a ledger. Bootstrap directory creation is setup, not a power-loss claim.

STATE_LOCK serializes validation-to-append; append opens existing ledger O_WRONLY|O_APPEND without O_CREAT. fsync returns before in-memory state changes or snapshot writes. An uncertain append permanently latches auth_ledger_error until restart; the process refuses subsequent fresh consumption. A durable append plus failed snapshot returns auth_snapshot_error_consumed; its ID stays in SPENT and returns auth_spent on retry. A later fresh successful snapshot can materialize the entire ledger. The ledger is never truncated or repaired. Main loads authoritative history and repairs cache before ThreadingHTTPServer is created.

Boundary signatures cover current seq/head under STATE_LOCK for all stages. With concurrent requests a later current head could include other consumes; concurrency is out of scope. Sequential R2 requires exact head equality at START/COMPLETE. The unchanged association verifies the full event, exposes added fields under unknown_fields.event, and saves full raw submission bytes. Offline checks verify added fields and reject tampering for both actual candidate providers.

R1 inventory and file set are verified before and after build and before/after R2. Original code, harness, docs and manifests are preserved under baseline/pre_hardening. Source manifests distinguish baseline provenance from candidate implementation identity. No final lock exists.

MP005 does not establish resistance to rollback of the entire local provider history, including both the consumption ledger and its materialized snapshot. Externally preserved signed ledger-head evidence provides a comparison point but is not used in this test as a remote execution-authority check.
