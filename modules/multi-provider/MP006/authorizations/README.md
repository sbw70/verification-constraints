# MP006 — Operator Authorizations

## Purpose

This directory preserves the explicit operator authorization used for the MP006-R01 physical power-loss experiment.

Operator authorization controls which MP006 orchestration actions may proceed under a reviewed configuration.

It does not grant authority to execute provider-controlled operations.

## Directory Contents

| File | Purpose |
|---|---|
| [MP006_R01_RUN001.json](MP006_R01_RUN001.json) | Operator authorization for the completed R01 session |

## Recorded Authorization

**Session:** `MP006_R01_RUN001`

**Authorized:** `true`

**Configuration SHA-256:**

`d7b4be8a0b42fed64f7ca2a17fc412280a84d7ea20d2421c0c786873756a63ea`

The authorization permits these seven actions:

| Action | Purpose |
|---|---|
| `initialize` | Initialize session-specific persistent state |
| `prepare` | Generate provider authorization artifacts |
| `capture` | Preserve provider state and process evidence |
| `send` | Submit preserved requests |
| `checkpoint` | Verify initial consumption before power interruption |
| `launch` | Start the reviewed provider runtime |
| `_serve` | Run the detached provider process |

Other diagnostic, validation, and scoring actions have separate handling in `mp006.py`.

## Authorization Enforcement

The MP006 adapter checks:

1. The configuration status is `REVIEWED_FOR_OPERATOR_RUN`.
2. Required operator-readiness flags are enabled.
3. The authorization explicitly contains `authorized: true`.
4. The session identifiers match.
5. The requested action is permitted.
6. The configuration's current SHA-256 matches the authorized hash.

A failed check prevents the gated action from proceeding.

The authorization is supplied explicitly through the `--authorization` argument.

The reviewed configuration is preserved in:

[../configs/MP006_R01.json](../configs/MP006_R01.json)

## Authority Separation

This file authorizes the local MP006 test procedure.

It is not:

- A Provider A execution authorization.
- An Ed25519-signed provider artifact.
- A replacement for provider-side verification.
- Permission for the intermediary to issue or enlarge authority.

Provider execution remains subject to the frozen MP005 Provider A implementation.

The operator authorization does not contain provider signing keys.

### Security Boundary

The configuration hash binds the authorization to specific configuration bytes.

The authorization file itself is not cryptographically signed.

Its effectiveness therefore depends on control of the local file and execution environment.

It should not be treated as protection against an attacker who can arbitrarily modify the authorization, configuration, and local implementation.

## Historical Preservation

This authorization belongs to the completed session:

`MP006_R01_RUN001`

It should remain unchanged.

Do not:

- Reuse it for another session.
- Add actions retroactively.
- Change the authorized configuration hash.
- Rewrite it to match altered configuration files.
- Treat it as continuing approval for new experiments.

A subsequent experiment requires its own reviewed configuration and explicit operator authorization.

## Evidence Boundary

This directory documents authorization of the experimental procedure.

It does not independently establish successful execution, physical power interruption, persistent-state recovery, or replay rejection.

Those outcomes are recorded in:

[MP006-R01 Evidence](../evidence/MP006_R01_RUN001/)

**Recorded result:** `PASS`

**Safety result:** `REPLAY_REJECTED_WITHOUT_ADDITIONAL_CONSUMPTION_OR_EXECUTION`

The authorization remains part of the historical record of the completed experiment.
