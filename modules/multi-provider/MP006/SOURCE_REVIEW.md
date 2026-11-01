# MP006 source review

Inspection covers mp006.py and the frozen helpers it imports. It is not live
verification. Linux environment, actual relay routing, recorder placement and
autostart configuration remain uninspected.

## Confirmed call paths

- `recover-capture` calls `raw_capture` before provider import, source verification,
  or state validation. That function uses source `Path.read_bytes()` only, creates
  an exclusive evidence folder, writes raw evidence/metadata/inventory there and
  never opens persistent state for writing. Missing files are recorded. Reading
  may update filesystem access times; this is not a forensic disk image. An I/O
  failure can leave partial evidence; it is not removed or overwritten.
- `stopped` inspects the listener and /proc after the raw copy. It refuses a current
  provider/listener and does not kill or repair it. It cannot prove a provider
  never started and exited earlier, or provide an atomic machine-wide process
  freeze. Reviewed absence of autostart and operator-controlled launch remain
  necessary. Do not overstate this check.
- `_serve` imports the frozen provider only on explicit launch. Only HOST, PORT,
  ASSOCIATION_URL and three persistent file paths change. No provider method is
  replaced. The provider's own load_spent_state may reconcile snapshots on start;
  this is why raw preservation and off-machine verification come first.
- Launch uses nohup, DEVNULL stdin, unbuffered/no-bytecode Python, separate exclusive
  log files and detached session, matching R3 detached behavior. It prints a PID
  acknowledgment, not success of the service or of an execution.
- `boundaries` passes saved signed envelopes through MP005 validate_boundary_records;
  replay additionally runs MP005 correlate over the final continuous log cursor.
  That code checks actual Ed25519 signatures and binding/nonce/key identities.
  `advance_checks` requires signed START/COMPLETE ledger-head identity and exactly
  one durable consumption/execution advance. `saved` revalidates actual raw ledger,
  snapshot and execution bytes. No HTTP acknowledgment is an execution assertion.
- Send calls unchanged send_preserved -> preserved_request: hash checks preserved
  request/package/header, checks header decodes to exact package, then submits
  original bytes. The corrected scorer calls preserved_request again and compares
  all recorded sends' body/header/context/identity/relay URL with those files.
- Fresh send is gated by the MP005 replay checks. Its authority ID must differ,
  be previously unspent and advance the ledger/execution once. The corrected
  scorer requires fresh before/after captures to identify the same recovered
  process (host, boot, PID/start ticks, executable, runtime hash/path, state,
  command and cwd). No ticks are compared across boots.
- MP005 source and harness hashes are verified. Adapter writes resolve under
  MP006 state/evidence/configuration paths; no code writes the historical MP005
  workspace or its evidence. Dependencies are byte-identical copies. Do not run
  the historical simulation scripts or use historical deployment launchers here.

## Concrete corrections in this review

1. Final scoring rechecks exact preserved sends rather than assuming successful
   earlier send calls establish the final evidence package.
2. All initial/recovered phase captures are bound to their respective provider
   process and persistent path; fresh evidence cannot silently come from a
   different process/boot.
3. Missing reachability/procedure evidence is INCOMPLETE, not an attributed SUT
   FAIL. Wrong recovery identity is PRECONDITION_NOT_MET; mismatched send evidence
   is HARNESS_ERROR. Valid replay/fresh/continuity check failures remain FAIL.

## Boundaries of confirmation

PASS requires verified signed events AND local execution/ledger evidence, but
these are software observations, not independent hardware execution attestation.
The adapter trusts operator physical-disconnection/idle/off-machine-copy records.
SHA-256 inventories detect changed bytes relative to a preserved manifest; they
are not remote immutable anchors. A dishonest operator or arbitrary coordinated
rewriting of all evidence is outside this test.

Effective network routing is an operator precondition: signatures identify the
Provider A key, not a unique physical laptop. Confirm relay destination, unique
active Provider A, source/process paths and captured state on Dell before STOP 1.
No honest source review can confirm those facts without actual environment outputs.

The original seven tests used mocked boundary collection in scorer fixtures. That
tests orchestration, not live Ed25519 delivery. Signature validation is confirmed
by inspection of the unchanged MP005 verification path; actual signed observations
must be verified during the reviewed run. The additional regression check tests
the corrected final send-byte comparisons. No live test has been run.
