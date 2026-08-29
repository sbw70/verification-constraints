# WP2-T2 — Persistent State Startup Integrity

## Status

PASS — defect discovered, hardened, and regression-tested.

## Classification

Category 1 — NUVL core, no architecture change.

## Area

WP2 persistent bounded authority → startup and recovery integrity.

## Purpose

WP2-T2 tests whether damage, loss, or inaccessibility of persistent spent-authority state can silently recreate previously consumed authority during boundary startup.

The property under test is:

```text
persistent authority history cannot be trusted
        ->
boundary must not silently replace it
with an empty history
        ->
service must fail closed
```

The test specifically covers five startup-state conditions:

```text
Case 5 — truncated state
Case 6 — malformed JSON
Case 7 — zero-byte state
Case 8 — missing previously established state
Case 9 — unreadable state
```

The test was performed on an isolated boundary copy, isolated state path, and non-production port so that canonical replay state and normal fleet operation were not deliberately corrupted during fault injection. :contentReference[oaicite:0]{index=0}

## Authority Property Under Test

Persistent spent state is part of enforcement of bounded authority.

If a single-use authority has already been consumed, loss of the record of that consumption must not be interpreted as evidence that the authority was never consumed.

The required invariant is:

```text
known persistent state
        ->
state becomes damaged, inaccessible, or unexpectedly absent
        ->
startup cannot establish trustworthy authority history
        ->
boundary does not open for service
```

The dangerous behavior is:

```text
state unavailable
        ->
assume {}
        ->
start normally
        ->
previously consumed authority may appear unused
```

WP2-T2 was designed specifically to detect that failure mode.

## Test Isolation

The startup-integrity cluster was run separately from the normal boundary.

Test configuration included:

```text
isolated boundary port: 18091
isolated state path:    /home/seth/WP2_T2_spent_state.json
```

The normal boundary and canonical persistent-state evidence were not used as corruption targets.

## Original Implementation

The original isolated test boundary was:

```text
wp2_t2_startup_integrity_boundary.py
```

Its startup behavior was tested against all five fault conditions.

Initial result:

```text
Case 5 — PASS
Case 6 — PASS
Case 7 — PASS
Case 8 — FAIL
Case 9 — PASS

Original implementation: 4/5 PASS
```

The failure was substantive rather than an instrumentation failure.

## Case 5 — Truncated State

A deliberately truncated persistent-state document was installed before startup.

Observed:

```text
process exited with code 1
port 18091 never opened
JSONDecodeError raised
no service became available
no fallback to empty spent state
```

Result:

```text
PASS
```

Recorded hashes:

```text
truncated fixture:
7b37bdf247c214e19cd11f634dfdfb3bdc172284c3c15b61f3b4cd5e88b2a3d2

original startup log:
5a95f1d970980859f498e101ce025c91de6251e59425efd4d271b2ef879b032e
```

The malformed persistent history prevented the authority boundary from opening.

## Case 6 — Malformed JSON

A complete file containing syntactically invalid JSON was installed as persistent state.

Observed:

```text
process exited with code 1
port 18091 never opened
JSONDecodeError raised
no fallback to empty spent state
```

Result:

```text
PASS
```

Recorded hashes:

```text
malformed fixture:
6293b461d50873445c6a452ff43fa413dc6ab5db05f02a9d49b5cb3535e472ec

original startup log:
1b8c93ba306ce47070fc91f2114d399995be81b692e418c00d1ba62f22b75041
```

## Case 7 — Zero-Byte State

An existing zero-byte state file was installed.

Observed:

```text
process exited with code 1
port 18091 never opened
JSONDecodeError at column 1
no fallback to empty spent state
```

Result:

```text
PASS
```

Recorded hashes:

```text
zero-byte fixture:
e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855

original startup log:
21cfb8729c388ca48ddc9943f370144c6c402454ed7b02389bc6d415bc82102e
```

## Case 8 — Missing Previously Established State

Case 8 distinguishes an unexpectedly missing persistent-state file from legitimate first initialization.

A known persistent state was established and preserved.

The active state file was then removed before boundary startup.

### Original Behavior

The original implementation started successfully.

Observed:

```text
process remained running
port 18091 opened
Persistent replay entries loaded: 0
/health returned status=ok
spent_count=0
```

Result:

```text
FAIL
```

The original implementation interpreted the missing state file as an empty replay history.

That behavior violated the bounded-authority invariant.

A previously established authority history becoming unavailable is not equivalent to proof that no authority has ever been consumed.

This exposed a real persistence gap:

```text
previous state existed
        ->
state disappeared
        ->
boundary silently assumed empty history
        ->
service opened
```

## Defect

The startup implementation could not distinguish:

```text
legitimate initialization
```

from:

```text
loss of previously established persistent authority history
```

Treating both cases as an empty spent set creates an availability-first failure mode.

Under bounded authority, absence of established enforcement state cannot silently enlarge authority.

## Hardening

A hardened derivative was created:

```text
wp2_t2_startup_integrity_boundary_hardened.py
```

The missing-state startup behavior was changed to fail closed.

The hardened path raises:

```text
RuntimeError: replay_state_missing
```

rather than returning an empty spent set.

The recorded hardening diff hash is:

```text
6659967a856d74d976cec6157b942d29550ada1e55612e4770a4409f712033a1
```

## Case 8 Hardened Retest

The missing-state condition was repeated against the hardened derivative.

Observed:

```text
process exited with code 1
port 18091 never opened
startup stopped on RuntimeError: replay_state_missing
no empty spent-set fallback occurred
```

Result:

```text
PASS
```

The discovered Case 8 defect was therefore reproduced, corrected, and directly retested.

## Case 9 — Unreadable State

A known-good state file was restored and then made unreadable before startup.

Observed:

```text
process exited with code 1
port 18091 never opened
PermissionError: [Errno 13]
no fallback to empty spent state
```

Result:

```text
PASS
```

The original implementation already failed closed when the state path existed but could not be read.

## Hardened Regression

After correcting Case 8, the hardened derivative was rerun against the other four startup faults.

This verified that the missing-state correction had not weakened existing fail-closed behavior.

### Hardened Case 5 — Truncated

Observed:

```text
process exited
port did not open
JSONDecodeError
no empty-state fallback
```

Result:

```text
PASS
```

Hardened startup-log hash:

```text
a692cf1c569d3a38f0256c49beb13649a791a0d27139a18638e845070241ebf5
```

### Hardened Case 6 — Malformed JSON

Observed:

```text
process exited
port did not open
JSONDecodeError
no empty-state fallback
```

Result:

```text
PASS
```

Hardened startup-log hash:

```text
56e1136343d5d3e4a91533fa41fbb39217eb4224d1a6438c3d88c680c7786008
```

### Hardened Case 7 — Zero Byte

Observed:

```text
process exited
port did not open
JSONDecodeError
no empty-state fallback
```

Result:

```text
PASS
```

Hardened startup-log hash:

```text
a112adfb7f6e6929833f0f430a9db59d29683c9e50a9876f2a8a205501f19189
```

### Hardened Case 8 — Missing Established State

Observed:

```text
process exited
port did not open
RuntimeError: replay_state_missing
no empty-state fallback
```

Result:

```text
PASS
```

### Hardened Case 9 — Unreadable

Observed:

```text
process exited
port did not open
PermissionError
no empty-state fallback
```

Result:

```text
PASS
```

Final hardened cluster:

```text
Case 5 — PASS
Case 6 — PASS
Case 7 — PASS
Case 8 — PASS
Case 9 — PASS

Hardened implementation: 5/5 PASS
```

## Known-Good Controls

Fail-closed startup behavior alone is insufficient.

The hardened implementation must also demonstrate that valid persistent state continues to load normally.

A known-good state containing one sentinel spent entry was therefore tested before and after the hardened corruption regression.

Observed:

```text
boundary started normally
port 18091 opened
public key loaded
replay_state_persistent=true
spent_count=1
status=ok
```

The pre-regression and post-regression hardened good-state startup logs were byte-for-byte identical.

Recorded hash:

```text
857896b8ef96e404076bcdfcf33725e37b24744eedfa6f5f12349e4ebc6c6e9f
```

This provides a control showing that the hardening did not convert valid persistent state into a startup failure.

## Canonical Boundary Validation

After isolated testing, the hardening was applied to the canonical persistent boundary and normal startup behavior was checked.

The canonical boundary started on:

```text
port 8089
```

with the expected public trust anchor and no provider private key on the Pi.

The preserved pre-start state contained one spent entry.

After startup, the active state contained no spent entries.

Inspection established that the preserved entry had expired before the test date.

The resulting empty active state therefore reflected normal expiry pruning rather than loss of valid authority history.

This behavior is distinct from the Case 8 defect:

```text
Case 8 failure:
state file absent
        ->
history silently replaced with {}

Canonical validation:
state file present
        ->
state successfully parsed
        ->
expired entry deliberately pruned
        ->
valid empty state written
```

Canonical validation hashes:

```text
startup log:
0f5be9ec...d9219b8

preserved pre-start state:
c7bac069...c9d9ed7

post-start pruned state:
83ded5bc...874013
```

The abbreviated values above reflect the recorded evidence notes; the complete hashes should be taken from the final evidence ledger when constructing a checksum manifest.

## Final Result

WP2-T2 closed with the following progression:

```text
ORIGINAL IMPLEMENTATION
-----------------------
truncated state                 PASS
malformed JSON                  PASS
zero-byte state                 PASS
missing established state       FAIL
unreadable state                PASS

Result: 4/5


DEFECT
------
missing previously established state
was interpreted as empty history


HARDENING
---------
missing established state
now prevents boundary startup


HARDENED REGRESSION
-------------------
truncated state                 PASS
malformed JSON                  PASS
zero-byte state                 PASS
missing established state       PASS
unreadable state                PASS

Result: 5/5


VALID-STATE CONTROL
-------------------
known-good persistent state      PASS


CANONICAL VALIDATION
--------------------
hardened canonical startup       PASS
normal expired-entry pruning     PASS
```

## Supported Claim

Within the five tested startup-state conditions:

> The hardened persistent boundary does not silently recreate an empty authority history when previously established replay state is truncated, malformed, zero-byte, missing, or unreadable. In each tested invalid-state condition, startup failed before the boundary opened for service. Valid persistent state continued to load normally.

WP2-T2 also provides defect-discovery evidence rather than only final-state PASS evidence.

The original implementation demonstrably failed the missing-state condition.

The failure was preserved, the cause was isolated, the startup behavior was hardened, and the complete five-condition cluster was rerun successfully.

## Bounded-Authority Significance

The important security property is not simply filesystem error handling.

Persistent state participates in the authority boundary.

If the boundary forgets that an authority was consumed, the apparent authority available after restart may become larger than the authority that actually remains.

Therefore:

```text
unknown history != empty history
```

and:

```text
missing enforcement state
must not silently recreate authority
```

WP2-T2 directly tests that distinction.

## What This Test Does Not Prove

WP2-T2 does not establish:

- durability against every possible filesystem failure;
- durability against every storage-device failure;
- resistance to malicious host compromise;
- distributed-state consensus;
- multi-boundary recovery;
- arbitrary corruption recovery;
- filesystem atomicity under every power-loss condition;
- exactly-once physical execution;
- hardware fault tolerance;
- production backup or disaster-recovery behavior.

The evidence is specifically limited to startup behavior under the five defined persistent-state conditions.

## Evidence Set

The local WP2-T2 evidence set includes the original and hardened startup logs, fault fixtures, missing-state and unreadable-state records, good-state controls, original and hardened boundary copies, and canonical validation artifacts.

The finalized local ledger contains 29 hashed artifacts covering:

```text
original 4/5 startup cluster
Case 8 failure
hardening change
hardened 5/5 regression
known-good control bookends
canonical pre/post-hardening validation
```

The original Case 8 FAIL should remain in the evidence set.

It is part of the evidentiary chain showing that the tested invariant was not assumed: the failure was observed, preserved, corrected, and retested.

## Publication Notes

WP2-T2 contains persistence-boundary implementation material.

Publication of the implementation itself should follow the repository's existing boundary for persistence-sensitive source.

The externally useful evidence consists of:

- the defined startup conditions;
- original observed results;
- preserved Case 8 failure;
- hardened observed results;
- regression results;
- valid-state controls;
- canonical validation;
- cryptographic hashes.

Evidence should remain in its original tested form wherever possible so that recorded hashes continue to identify the actual test artifacts.

Generated local test keys, local addresses, artifact identifiers, nonces, and other local test values do not require modification merely because they are environment-specific.

Actual reusable network credentials or passwords should not be committed.
