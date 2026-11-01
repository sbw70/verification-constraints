# MP006 — Configuration

## Purpose

This directory contains the reviewed configuration for the MP006-R01 physical power-loss authority-persistence experiment.

The configuration identifies the participating systems, frozen provider implementation, session, persistent-state locations, and operator-readiness conditions.

It does not grant execution authority independently.

## Directory Contents

| File | Purpose |
|---|---|
| [MP006_R01.json](MP006_R01.json) | Reviewed configuration for session `MP006_R01_RUN001` |

## Recorded Configuration

**Session:** `MP006_R01_RUN001`

**Status:** `REVIEWED_FOR_OPERATOR_RUN`

**Baseline:** `MP005_SCORED_20261026_R3`

| Component | Recorded address |
|---|---|
| Provider A — Dell | `192.168.1.118:9090` |
| NUVL relay — Raspberry Pi | `192.168.1.100:8080/nuvl` |
| Association recorder — OmniBook | `192.168.1.102:9191/boundary` |

### Installation Paths

**Windows root:**

`C:\Users\holiw\esp32-main\MULTI_PROVIDER_006`

**Linux root:**

`/home/seth/MULTI_PROVIDER_006`

The MP006 adapter derives session-specific state and evidence paths from the configured Linux root and session identifier.

## Frozen Provider Identity

**Reference commit:**

`73713f6e9ed9c95251cc69ec88ef816cab771ac0`

**Provider A SHA-256:**

`79e4994c955ca842af04a8fd650a33d49de040bab95b821ded9e63e16866f2b6`

The adapter verifies the frozen MP005 source and harness dependencies.

It also checks Provider A's source hash against the value recorded in this configuration.

A source mismatch prevents normal operation.

## Operator-Readiness Conditions

The configuration records three readiness flags:

| Field | Recorded value |
|---|---|
| `addresses_verified` | `true` |
| `autostart_reviewed_disabled` | `true` |
| `operator_preflight_complete` | `true` |

The MP006 authorization gate requires these flags, the reviewed status, and a matching operator authorization before permitted actions can proceed.

These flags document completed operator reviews. Their values alone do not independently prove the underlying environmental conditions.

## Configuration Binding

The reviewed configuration has SHA-256:

`d7b4be8a0b42fed64f7ca2a17fc412280a84d7ea20d2421c0c786873756a63ea`

This value matches `config_sha256` in:

[MP006_R01_RUN001.json](../authorizations/MP006_R01_RUN001.json)

Before an authorized action, `mp006.py` checks:

1. The configuration has reviewed status and required readiness flags.
2. The authorization permits the requested action.
3. The authorization identifies the configured session.
4. The authorization's configuration hash matches the current configuration bytes.

Changing the configuration invalidates that hash match unless a new authorization explicitly binds the changed configuration.

The operator authorization is a local execution control, not a provider-issued authorization artifact.

## Preservation Rules

- Preserve the reviewed configuration used for the scored run.
- Do not change addresses, paths, source hashes, or readiness flags retroactively.
- Do not regenerate historical manifests to accommodate documentation changes.
- Do not reuse this configuration for a different session without separate review.
- Do not confuse configuration approval with provider authorization.

The archived deployment manifest preserves the original configuration hash:

[Deployment inventory](../manifests/original/DEPLOYMENT_SHA256SUMS.txt)

## Evidence Boundary

This directory establishes the configuration against which MP006-R01 was authorized and scored.

It does not establish that the provider executed successfully, survived power loss, or denied replay.

Those observations are documented in the completed experiment:

[MP006-R01 evidence](../evidence/MP006_R01_RUN001/)

**Scored result:** `PASS`

**Safety result:** `REPLAY_REJECTED_WITHOUT_ADDITIONAL_CONSUMPTION_OR_EXECUTION`

The recorded configuration remains historical evidence of the tested environment.
