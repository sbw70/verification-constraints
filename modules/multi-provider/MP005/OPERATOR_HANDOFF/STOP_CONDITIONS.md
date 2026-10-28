# HARD STOP — preserve, classify, do not silently repair

- R2 not run/copied/independently reviewed; absent final lock; no explicit phase/session authorization; scored lacks accepted rehearsal.
- Wrong physical machine/hostname, unverified or conflicting IPv4, Pavilion selected as live provider.
- Deployed source/helper/key/registry/trust hash mismatch; wrong root, runtime, cwd, ledger/state/log path or relay destination.
- Missing/invalid ledger, unexplained snapshot/ledger mismatch, duplicate provider process, unknown PID, non-Linux provider persistence filesystem.
- Any evidence/session/destination collision, attempted overwrite, missing raw evidence, stale/truncated/replaced association stream, copy/correlation ambiguity.
- Target consume not objectively proven, no signed COMPLETE, unknown in-flight request, IDLE not confirmed: DO NOT TERMINATE.
- Restart identity not objectively new/later on same host/boot/command/runtime/path; accidental non-target/relay/association restart.
- Replay bytes/context/authority differ, unexpected ledger advancement or execution, missing signed auth_spent, unexpected START/COMPLETE.
- Fresh authority is reused, advances more/less than one entry, breaks prior hash link, executes incorrectly or has mismatched signed head.
- Any source/config/contract/manifest change proposed after scored start; unexplained result; silent retry/cleanup.

Classify property FAIL only when valid evidence contradicts the locked property after prerequisites were established. PRECONDITION_NOT_MET for unmet prerequisites; HARNESS_ERROR for tooling/evidence ambiguity. Preserve operator mistakes, misfires, console output and partial results. Do not turn failed/ambiguous cases into NOT_RUN to hide them. A genuine failure stops the campaign unless its final locked contract explicitly defines another behavior. A failed Linux environment is not a provider property failure.
