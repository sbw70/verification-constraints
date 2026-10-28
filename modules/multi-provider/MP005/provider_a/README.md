# MP005 — Provider A

## Purpose

Provider A is an independently controlled authorization and execution domain in the MP005 multi-provider test environment.

It validates provider-specific authorization, durably records consumption, enforces single-use constraints, and emits signed boundary events.

Provider A does not delegate execution authority to the NUVL intermediary, association recorder, or Provider B.

The principal MP005 objective is to determine whether previously consumed authority remains spent after termination and restart of the provider process.

## Implementation

The Provider A directory contains:

| File | Function |
|---|---|
| [provider_a.py](provider_a.py) | Provider authorization, persistence, execution recording, and boundary signaling |
| [mint_authorization_a.py](mint_authorization_a.py) | Provider-specific authorization artifact generation |
| `provider_a_issuance_private.pem` | Laboratory authorization signing key |
| `provider_a_issuance_public.pem` | Authorization signature verification key |
| `provider_a_private.pem` | Laboratory boundary-event signing key |
| `provider_a_public.pem` | Boundary-event signature verification key |

The implementation uses Ed25519 signatures and SHA-256.

The included private keys are laboratory fixtures published for reproducibility. They are not production credentials and must not be trusted for production authorization.

## Authorization Boundary

Provider A accepts forwarded artifacts through HTTP POST `/ingest`.

Each artifact contains:

- Request representation.
- Verification context.
- Deterministic request binding.
- Provider-specific authorization artifact.

Provider A independently evaluates the submitted material.

Authorization validation includes:

1. Recomputing the request binding.
2. Checking that an authorization artifact is present and correctly structured.
3. Verifying that the authorization identifies `PROVIDER_A`.
4. Recomputing the authorization identifier.
5. Verifying the Ed25519 authorization signature.
6. Checking the authorized request representation.
7. Checking the authorized verification context.
8. Determining whether the authorization has already been consumed.

A valid forwarding request does not independently establish authorization.

Provider A must accept the authorization under its own validation and consumption rules before execution can proceed.

## Authorization Issuance

[mint_authorization_a.py](mint_authorization_a.py) generates provider-specific signed authorization artifacts.

The authorization binds:

- Provider identity.
- Request representation.
- Verification context.
- Random nonce.
- Derived authorization identifier.

The issuer signs the authorization using Provider A's laboratory issuance private key.

It produces a JSON authorization package and a Base64URL-encoded representation suitable for transmission.

The intermediary does not mint these artifacts.

## Durable Consumption

Provider A maintains three distinct records:

| Record | Purpose |
|---|---|
| `provider_a_consume_ledger.jsonl` | Authoritative append-only authorization consumption history |
| `provider_a_spent_state.json` | Materialized spent-authority snapshot |
| `provider_a_execution.jsonl` | Recorded execution consequences |

The consumption ledger contains linked entries identifying the consumed authorization, nonce, operation, sequence, and preceding ledger hash.

Each entry includes its own calculated SHA-256 hash.

Provider A validates the ledger during startup and reconstructs the consumed-authority set from that history.

### Commit-before-execution ordering

For an accepted authorization, the implementation:

1. Confirms the authorization has not already been consumed.
2. Appends the next consumption record.
3. Flushes and calls `fsync` on the consumption ledger.
4. Updates the in-memory consumed-authority state.
5. Persists the materialized spent-state snapshot.
6. Emits a signed `START` boundary event.
7. Records execution.
8. Emits a signed `COMPLETE` boundary event.

Execution is not admitted before the consumption record and snapshot persistence steps succeed.

If consumption persistence fails, the request is denied.

If the ledger has been durably advanced but snapshot persistence fails, the authorization remains consumed and execution is not admitted.

This ordering deliberately favors preventing duplicate execution over guaranteeing that every consumed authorization produces an execution consequence.

## Restart and State Reconciliation

On startup, Provider A validates its consumption ledger and reconciles the spent-state snapshot.

The implementation distinguishes:

- Exact agreement between snapshot and ledger.
- A snapshot representing a valid earlier prefix of the ledger.
- A snapshot ahead of the ledger.
- A divergent snapshot.
- Missing or malformed snapshot data.
- Missing or invalid ledger data.

An exact snapshot match is accepted.

A validated earlier snapshot prefix can be advanced to the authoritative ledger state.

Missing or syntactically malformed snapshots have defined recovery behavior. Malformed bytes are preserved before recovery.

Invalid or divergent parseable snapshots are not silently replaced.

Missing or invalid consumption ledgers prevent normal startup.

These behaviors are supported by the implementation and corresponding simulation or offline checks. They must not all be interpreted as independently completed physical-host scored experiments.

## Signed Boundary Events

Provider A creates signed boundary events for:

- `START` — authorization accepted and consumption recorded.
- `COMPLETE` — execution recorded.
- `DENY` — request rejected.

Boundary events bind the provider identity, operation, request binding, authorization identity when available, and relevant execution stage.

They also include the current consumption-ledger sequence and head.

Events are signed using Provider A's boundary private key and sent to the independent association recorder.

The association recorder can verify the signatures using the registered Provider A public key.

Association delivery does not grant authorization or control Provider A's execution decision.

## Physical Deployment

The MP005 scored deployment used:

| Component | Recorded configuration |
|---|---|
| Machine | Dell Latitude E5450 |
| Hostname | `Xer0trust-3` |
| Provider address | `192.168.1.118` |
| Provider port | `9090` |
| Ingest endpoint | `/ingest` |
| Association endpoint | `192.168.1.102:9191/boundary` |

The scored provider runtime was launched through:

[launch_provider.py](../harness/launch_provider.py)

The authoritative deployment paths and configuration are retained in:

[MP005_RUN_MANIFEST.json](../configs/MP005_RUN_MANIFEST.json)

The scored R3 state directory was:

`/home/seth/MULTI_PROVIDER_005/live_state/scored/MP005_SCORED_20261026_R3/provider_a`

These addresses and paths describe the recorded laboratory environment, not a portable default deployment.

## Scored Test — R01

**Session:** `MP005_SCORED_20261026_R3`

**Case:** `R01_PROVIDER_A_RESTART_DURABILITY`

**Result: PASS**

The case examined whether previously consumed authority remained spent after an operator-controlled idle process termination and subsequent restart.

The test established:

1. A valid authorization was consumed.
2. The provider recorded one execution.
3. The consumption ledger contained the corresponding linked entry.
4. The original provider process was terminated after the required idle checkpoint.
5. A different process instance restarted on the same host and operating-system boot.
6. The restarted provider retained the same durable state and execution history.
7. Exact replay of the consumed authorization was denied with `auth_spent`.
8. Replay produced no additional execution, consumption entry, or signed `START`/`COMPLETE`.
9. A separate fresh authorization was accepted, consumed, and executed once.
10. The fresh consumption extended the validated ledger history.

The case results explicitly report that process-local execution sequence continuity was not a scored requirement.

### Evidence

- [R01 scored evidence](../evidence/scored/MP005_SCORED_20261026_R3/R01/)
- [R01 case results](../evidence/scored/MP005_SCORED_20261026_R3/R01/case_results.json)
- [R01 SHA-256 inventory](../evidence/scored/MP005_SCORED_20261026_R3/R01/SHA256SUMS.txt)
- [R3 association records](../evidence/scored/MP005_SCORED_20261026_R3/association/)
- [R3 provider state](../live_state/scored/MP005_SCORED_20261026_R3/provider_a/)

The original 67-entry R01 SHA-256 inventory was verified during publication preparation.

## Previous Scored Campaign — R2

The earlier campaign, `MP005_SCORED_20261025_R2`, is retained as an unsuccessful result.

Provider A demonstrated restart durability and rejection of previously consumed authority.

However, its fresh-authorization requirement was not satisfied.

The fresh authorization was consumed, but the expected execution record and signed `COMPLETE` event were absent.

The campaign remains classified as `NON_PASS`.

Disconnected SSH output pipes were identified as a suspected contributing condition, but the exact causal failure was not established.

The original authorization was not retried.

The subsequent R3 campaign used an independently detached provider-launch procedure and separate state directories.

The R2 evidence remains unchanged.

See:

[R2 Provider A incident](../evidence/scored/MP005_SCORED_20261025_R2/R01/R01_FRESH_EXECUTION_INCIDENT.json)

## Scope and Limitations

The scored R01 result establishes single-use authority preservation across the specific idle forced-process restart tested.

It does not establish:

- Protection against rollback of both the consumption ledger and snapshot to an older mutually consistent history.
- Persistence across physical power loss.
- Durability across a host reboot.
- Crash-window behavior during an incomplete consumption transaction.
- Resistance to concurrent consumption attempts.
- Independent operating-system execution attestation.
- Physical actuator behavior.

Execution in this laboratory implementation is represented by the provider's recorded execution event.

The test does not establish that the HTTP `204 No Content` response proves authorization or execution.

The provider retains authority over its own execution decisions. The intermediary and association recorder remain outside that authority boundary.

## Related Documentation

- [Provider B](../provider_b/)
- [NUVL intermediary](../intermediary/)
- [Association recorder](../association/)
- [Test configuration](../configs/)
- [Evidence](../evidence/)
- [MP005 root](../)
```
