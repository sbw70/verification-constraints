# MP005 — Frozen Simulation Reference

## Purpose

This directory preserves the MP005 R3 local simulation and independent-review implementation.

The simulation characterizes provider authorization persistence, replay enforcement, and snapshot reconciliation under controlled Linux conditions.

The files are retained as frozen reference dependencies for MP006.

They are not MP006 test scripts and must not be executed against the completed MP006 experiment.

## Directory Contents

| File | Purpose |
|---|---|
| [run.py](run.py) | Linux-only simulation entry point |
| [engine.py](engine.py) | Scenario orchestration, provider restart, state manipulation, and evidence collection |
| [launch_relay.py](launch_relay.py) | Loopback-only relay launcher for isolated simulation |
| [review_r3.py](review_r3.py) | Independent validation of previously captured R3 simulation evidence |

## Simulation Architecture

The simulation uses the frozen MP005 components:

- Provider A and Provider B implementations.
- NUVL intermediary.
- Shared verification harness.
- Provider-local consumption ledgers.
- Materialized spent-state snapshots.
- Software execution logs.
- Signed provider boundary events.

Network communication is restricted to loopback addresses.

Each scenario uses isolated state and evidence directories.

The simulation recorder is a local test component, not the live association recorder.

Its observations do not constitute a separate live deployment.

## R3 Test Matrix

The simulation defines six scenarios for each provider.

| Case | Tested condition | Expected behavior |
|---|---|---|
| S00 | Normal provider restart | Consumed authority remains spent; replay denied |
| S01 | Missing consumption ledger | Provider startup fails closed |
| S02 | Malformed consumption ledger | Provider startup fails closed without repairing the ledger |
| S03 | Valid snapshot rollback to genesis while ledger remains advanced | Provider recovers spent state from the validated ledger |
| S04 | Snapshot ahead of consumption ledger | Provider startup fails closed |
| S05 | Equal-sequence snapshot divergence | Provider refuses mismatched ledger head or spent state |

S05 contains separate head-divergence and spent-divergence checks.

The R3 implementation evaluates both providers independently.

### Recorded Historical Result

The frozen MP005 run manifest records:

**12 of 12 provider/scenario combinations: PASS**

These are historical local-simulation results.

They are not additional MP006 test results.

The recorded review applies only to the tested implementation and scenarios.

## Execution and State Verification

For restart scenarios, the engine:

1. Initializes isolated provider-local state.
2. Prepares provider-issued authorization.
3. Records initial consumption and execution.
4. Terminates the local provider process.
5. Restarts the provider against the existing state.
6. Replays the original authorization.
7. Checks for a signed denial without additional execution.
8. Submits separate fresh authority.
9. Verifies the expected ledger and execution advancement.

The harness checks signed boundary events, preserved requests, process identities, and persistent-state evidence.

An HTTP `204` response is not accepted as proof of execution.

## Reconciliation Characterization

The simulation distinguishes recoverable snapshot conditions from inconsistent persistent histories.

A snapshot representing a valid prefix of the consumption ledger may be advanced to the verified ledger state.

An ahead snapshot or an equal-sequence divergent snapshot must not be silently reconciled.

Missing or malformed consumption ledgers must not become usable authorization state through automatic repair.

These behaviors are evaluated through the specific scenarios defined in `engine.py`.

The experiment does not establish resistance to rollback of both the ledger and snapshot to an older mutually consistent history.

## Independent Review

[review_r3.py](review_r3.py) validates previously preserved simulation evidence.

Its checks include:

- Source and harness identities.
- SHA-256 inventories.
- Consumption-ledger hash chains.
- Snapshot consistency.
- Authorization and operation binding.
- Signed boundary events.
- Restart process identities.
- Replay and fresh-execution results.
- Preservation of earlier R1 and R2 evidence.

The reviewer recomputes evidence properties rather than accepting recorded PASS labels alone.

It does not launch provider or relay processes.

However, it writes review findings and source-difference artifacts outside the simulation evidence directory.

It is therefore not a strictly read-only filesystem operation.

## Frozen Dependency Constraints

The simulation files are part of the original MP006 reference inventory.

Their source identities must remain unchanged.

Do not:

- Modify simulation logic to accommodate MP006.
- Execute historical simulation scripts inside the frozen reference tree.
- Recreate or overwrite historical R3 evidence.
- Substitute MP006 persistent state for simulation state.
- Change provider signing or verification functions.
- Relax fail-closed behavior to obtain PASS.
- Treat local simulation results as physical power-loss evidence.

The copied MP005 reference does not contain the complete historical simulation evidence tree required by these scripts.

It must not be treated as a standalone reproduction environment.

## Integrity Verification

The original MP006 build manifest records these SHA-256 identities:

| File | SHA-256 |
|---|---|
| `engine.py` | `9c5b00c947eadf2cc36ca307651a41a72e3739f8679f0f6dbe91152da1436b` |
| `launch_relay.py` | `a09ec87e1ff9aeaae8a38ee145c371939e0beec4f5b837b63c7c53e699f38c2e` |
| `review_r3.py` | `3d1ac8fc870c37d806edc0dce6399f561727312cb6f2fb66e1c920b5f267791d` |
| `run.py` | `5301e81753dd350abc36eaf45999b8816ed3d62f657b89aac9fa4c984d2577cc` |

The archived inventory is preserved at:

[MP006 original build inventory](../../../manifests/original/SHA256SUMS.txt)

This README is additional documentation and is not included in the historical source inventory.

## Evidence Boundary

The MP005 simulation demonstrates specific software-level restart and reconciliation properties under controlled local conditions.

It does not independently establish:

- Physical power-loss persistence.
- Host reboot durability.
- Crash-window correctness.
- Concurrent double-spend resistance.
- Independent hardware execution.
- Full-history rollback resistance.

MP006 separately evaluates physical power interruption and recovered authorization state using its own evidence.

The two experimental scopes must remain distinguishable.

## Related Documentation

- [Frozen MP005 reference](../)
- [MP005 test harness](../harness/)
- [Provider A](../provider_a/)
- [Provider B](../provider_b/)
- [MP005 configuration](../configs/)
- [MP006-R01 evidence](../../../evidence/MP006_R01_RUN001/)
