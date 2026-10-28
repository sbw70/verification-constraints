```markdown
# MP005 — Provider B

## Purpose

Provider B is an independently controlled authorization and execution domain in the MP005 multi-provider test environment.

It validates provider-specific authorization, enforces local policy, durably records authorization consumption, and emits signed boundary events.

Provider B does not depend on Provider A to authorize execution.

The NUVL intermediary forwards requests without acquiring authority over Provider B's decisions.

The principal MP005 objective is to determine whether previously consumed authority remains spent after termination and restart of the provider process.

## Implementation

The Provider B directory contains:

| File | Function |
|---|---|
| [provider_b.py](provider_b.py) | Provider authorization, policy enforcement, persistence, execution recording, and boundary signaling |
| [mint_authorization_b.py](mint_authorization_b.py) | Provider-specific authorization artifact generation |
| `provider_b_issuance_private.pem` | Laboratory authorization signing key |
| `provider_b_issuance_public.pem` | Authorization signature verification key |
| `provider_b_private.pem` | Laboratory boundary-event signing key |
| `provider_b_public.pem` | Boundary-event signature verification key |

The implementation uses Ed25519 signatures and SHA-256.

The included private keys are laboratory fixtures published for reproducibility. They are not production credentials and must not be trusted for production authorization.

## Authorization Boundary

Provider B accepts forwarded artifacts through HTTP POST `/ingest`.

Each artifact contains:

- Request representation.
- Verification context.
- Deterministic request binding.
- Provider-specific authorization artifact.

Provider B independently evaluates the submitted material.

Authorization validation includes:

1. Recomputing the request binding.
2. Checking that an authorization artifact is present and correctly structured.
3. Verifying that the authorization identifies `PROVIDER_B`.
4. Recomputing the authorization identifier.
5. Verifying the Ed25519 authorization signature.
6. Checking the authorized request representation.
7. Checking the authorized verification context.
8. Applying Provider B's local policy constraint.
9. Determining whether the authorization has already been consumed.

Successful forwarding does not establish permission to execute.

Provider B must independently accept the authorization and satisfy its own policy and consumption constraints.

## Independent Provider Policy

Provider B includes an additional policy-denial condition:

`POLICY_DENY_CONTEXT = "CTX_MP002_DIVERGE"`

When the verification context matches this value, Provider B emits a signed `DENY` event with reason:

`policy_denied`

The check occurs after authorization validation and before consumption.

Therefore, this policy-denied request does not consume its authorization or produce an execution record.

This condition demonstrates that providers can apply different local authorization policies while receiving requests through the same intermediary.

Provider A does not contain this specific policy-denial rule.

The intermediary does not interpret, override, or reconcile these provider decisions.

## Authorization Issuance

[mint_authorization_b.py](mint_authorization_b.py) generates Provider B-specific signed authorization artifacts.

The authorization binds:

- Provider identity.
- Request representation.
- Verification context.
- Random nonce.
- Derived authorization identifier.

The issuer signs the authorization using Provider B's laboratory issuance private key.

It produces a JSON authorization package and a Base64URL-encoded representation suitable for transmission.

Provider B's issuance keys are separate from Provider A's keys.

An authorization issued for Provider A does not become valid Provider B authority merely because it passes through the intermediary.

## Durable Consumption

Provider B maintains three distinct records:

| Record | Purpose |
|---|---|
| `provider_b_consume_ledger.jsonl` | Authoritative append-only authorization consumption history |
| `provider_b_spent_state.json` | Materialized spent-authority snapshot |
| `provider_b_execution.jsonl` | Recorded execution consequences |

The consumption ledger contains linked entries identifying:

- Provider identity.
- Authorization identifier.
- Authorization nonce.
- Operation identifier.
- Ledger sequence.
- Previous entry hash.
- Current entry hash.

Ledger entries use canonical JSON and a SHA-256 hash chain.

On startup, Provider B validates the ledger and reconstructs the consumed-authority set from its recorded history.

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

Execution is not admitted before the required consumption and snapshot persistence steps succeed.

If ledger persistence fails, the request is denied.

If the ledger advances durably but snapshot persistence fails, the authorization remains consumed and execution is not admitted.

This ordering prioritizes prevention of duplicate execution over guaranteed execution of every consumed authorization.

## Restart and State Reconciliation

Provider B treats its validated consumption ledger as the authoritative local consumption history.

The materialized spent-state snapshot is reconciled against that history during startup.

The implementation distinguishes:

- Exact agreement between snapshot and ledger.
- A snapshot representing a valid earlier ledger prefix.
- A snapshot ahead of the ledger.
- A divergent snapshot.
- Missing or malformed snapshot data.
- Missing or invalid ledger data.

Exact agreement is accepted.

A validated earlier prefix may be advanced to match the ledger.

Missing or syntactically malformed snapshots have defined recovery behavior. Malformed snapshot bytes are preserved before replacement.

Invalid or divergent parseable snapshots are not silently replaced.

A missing or invalid consumption ledger prevents normal startup.

These behaviors are supported by the implementation and applicable simulation or offline evidence.

They must not all be interpreted as separately completed physical-host scored experiments.

## Signed Boundary Events

Provider B emits signed boundary events for:

- `START` — authorization accepted and consumption recorded.
- `COMPLETE` — execution recorded.
- `DENY` — authorization or policy rejection.

Boundary events contain the provider identity, operation, request binding, authorization information when available, and the relevant stage.

They also include the current consumption-ledger sequence and head.

Events are signed using Provider B's boundary private key.

The independent association recorder verifies the signatures using Provider B's registered public key.

Association recording does not grant execution authority.

Provider B remains responsible for its own authorization and execution decisions.

## Physical Deployment

The MP005 scored deployment used:

| Component | Recorded configuration |
|---|---|
| Machine | HP laptop running Linux Mint |
| Hostname | `Xer0trust2` |
| Provider address | `192.168.1.107` |
| Provider port | `9090` |
| Ingest endpoint | `/ingest` |
| Association endpoint | `192.168.1.102:9191/boundary` |

The scored provider runtime was launched through:

[launch_provider.py](../harness/launch_provider.py)

The authoritative deployment configuration is retained in:

[MP005_RUN_MANIFEST.json](../configs/MP005_RUN_MANIFEST.json)

The scored R3 state directory was:

`/home/seth/MULTI_PROVIDER_005/live_state/scored/MP005_SCORED_20261026_R3/provider_b`

These addresses and paths describe the recorded laboratory environment, not a portable default deployment.

## Scored Test — R02

**Session:** `MP005_SCORED_20261026_R3`

**Case:** `R02_PROVIDER_B_RESTART_DURABILITY`

**Result: PASS**

The case examined whether previously consumed authority remained spent after an operator-controlled idle process termination and subsequent restart.

The test established:

1. A valid Provider B authorization was consumed.
2. Provider B recorded one execution.
3. The consumption ledger contained the corresponding linked entry.
4. The original provider process was terminated after the required idle checkpoint.
5. A different process instance restarted on the same host and operating-system boot.
6. The restarted provider retained the same durable state and execution history.
7. Exact replay of the consumed authorization was denied with `auth_spent`.
8. Replay produced no additional execution, consumption entry, or signed `START`/`COMPLETE`.
9. A separate fresh Provider B authorization was accepted, consumed, and executed once.
10. The fresh consumption extended the validated ledger history.

The case results explicitly report that process-local execution sequence continuity was not a scored requirement.

### Evidence

- [R02 scored evidence](../evidence/scored/MP005_SCORED_20261026_R3/R02/)
- [R02 case results](../evidence/scored/MP005_SCORED_20261026_R3/R02/case_results.json)
- [R02 SHA-256 inventory](../evidence/scored/MP005_SCORED_20261026_R3/R02/SHA256SUMS.txt)
- [R3 association records](../evidence/scored/MP005_SCORED_20261026_R3/association/)
- [R3 provider state](../live_state/scored/MP005_SCORED_20261026_R3/provider_b/)

The original 67-entry R02 SHA-256 inventory was verified during publication preparation.

## Previous Scored Campaign — R2

The earlier campaign, `MP005_SCORED_20261025_R2`, is retained as an unsuccessful result.

Provider A's R01 case did not satisfy the complete scored requirements because fresh authorization consumption was not followed by the required execution and signed completion.

The R2 campaign
```
