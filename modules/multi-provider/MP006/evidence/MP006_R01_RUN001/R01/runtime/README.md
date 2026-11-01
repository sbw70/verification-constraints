# MP006-R01 — Provider Runtime Evidence

## Purpose

This directory preserves Provider A's runtime output and launch records before and after the physical power interruption.

The evidence supports verification of process replacement, persistent-state recovery, authorization replay denial, and subsequent fresh execution.

## Directory Contents

| File | Purpose |
|---|---|
| [initial.log](initial.log) | Provider output before power interruption |
| [initial.pid.json](initial.pid.json) | Initial detached process launch record |
| [recovered.log](recovered.log) | Provider output after power restoration and restart |
| [recovered.pid.json](recovered.pid.json) | Recovered detached process launch record |
| [SHA256SUMS.txt](SHA256SUMS.txt) | Original four-file integrity inventory |

## Initial Provider Runtime

[initial.pid.json](initial.pid.json) records:

**PID:** `113976`

The process launched the MP006 adapter using the frozen MP005 Provider A implementation.

The initial runtime log records:

- Provider: `PROVIDER_A`
- Listening port: `9090`
- Spent entries loaded: `0`
- Original authorization: `START`
- Original authorization: `EXECUTED`
- Original authorization: `COMPLETE`

The recorded execution used process-local sequence `1`.

The corresponding [pre-consumption](../pre_consume/) and [consumed](../consumed/) evidence confirms the persistent-state transition from zero to one consumed authorization.

## Recovered Provider Runtime

[recovered.pid.json](recovered.pid.json) records:

**PID:** `1725`

The recovered runtime log records:

- Provider: `PROVIDER_A`
- Listening port: `9090`
- Spent entries loaded: `1`
- Original authorization replay: `DENY`
- Denial reason: `auth_spent`
- Fresh authorization: `START`
- Fresh authorization: `EXECUTED`
- Fresh authorization: `COMPLETE`

The recovered provider loaded the original consumed authorization from persistent state.

It subsequently denied replay and executed the separate fresh authorization.

## Process Identity

The launch records contain the process identifiers and commands used to start the provider.

The corresponding state-capture directories preserve additional process evidence.

| Property | Initial runtime | Recovered runtime |
|---|---|---|
| Hostname | `Xer0trust-3` | `Xer0trust-3` |
| PID | `113976` | `1725` |
| Boot identifier | Different | Different |
| Provider source | Frozen MP005 Provider A | Frozen MP005 Provider A |
| Persistent-state path | Same | Same |

**Provider source SHA-256:**

`79e4994c955ca842af04a8fd650a33d49de040bab95b821ded9e63e16866f2b6`

The initial and recovered process-identity captures agree on the provider source hash, launch command, hostname, and persistent-state path.

The boot identifiers and process identifiers differ.

The MP006 scorer verifies these properties using the preserved process evidence rather than PID values alone.

## Execution Sequence Interpretation

Both runtime logs record a software execution with:

`local_seq=1`

This is expected.

The execution counter belongs to the running provider process and resets when that process restarts.

The persistent consumption ledger does not reset.

Its sequence advances from `1` to `2` after the recovered provider executes the fresh authorization.

Process-local execution sequence continuity across boots is not a scored property.

## Startup Banner

Both logs begin with:

`MP001_PROVIDER_A`

This banner is retained in the frozen MP005 Provider A source.

It is an inherited startup label, not the identifier of the MP006 experiment.

The MP006 session and execution identity are established through the launch commands, configuration, state paths, and captured process metadata.

## Evidence Integrity

[SHA256SUMS.txt](SHA256SUMS.txt) inventories the four original runtime files.

From this directory:

```bash
sha256sum -c SHA256SUMS.txt
```

The README is additional documentation and is not included in the historical inventory.

Do not modify the original runtime records or regenerate their hashes.

## Evidence Boundary

The runtime logs provide supporting evidence of provider startup, state loading, authorization decisions, and software execution.

The launch records identify the detached processes but do not independently establish their execution history.

Physical power interruption is documented separately through operator confirmation and independent reachability observations.

Persistent-state continuity and replay safety are established through the corresponding state captures, signed boundary records, and scorer.

The relevant evidence is preserved in:

- [Recovered persistent state](../recovered_before_start/)
- [Replay submission](../send_replay/)
- [Post-replay state](../after_replay/)
- [Fresh execution state](../after_fresh/)
- [Official scoring result](../case_results.json)

See the [R01 evidence documentation](../README.md) for the complete experiment.
