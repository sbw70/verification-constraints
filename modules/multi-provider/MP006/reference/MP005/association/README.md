# MP005 — Association and Boundary Evidence Recorder

## Purpose

The association component independently records provider-originated boundary events during MP005 testing.

It receives signed observations from Provider A and Provider B, verifies their signatures, and preserves them in a hash-linked evidence log.

The association recorder is not an authorization authority, execution coordinator, or provider policy engine.

Neither provider depends on the association recorder to authorize execution.

## Implementation

The association component contains:

- [association_recorder.py](association_recorder.py) — HTTP evidence recorder and signature verifier.
- [provider_registry.json](provider_registry.json) — Registered provider identities and public-key references.
- [trust/](trust/) — Provider public keys used to verify signed boundary events.

The recorder uses Python's HTTP server implementation and the `cryptography` library for Ed25519 signature verification.

### Endpoints

| Endpoint | Method | Function |
|---|---|---|
| `/boundary` | POST | Receive, inspect, and record a boundary submission |
| `/health` | GET | Return recorder health and session identity |

The configured MP005 live association endpoint is:

`http://192.168.1.102:9191/boundary`

The address is specific to the recorded laboratory deployment.

## Boundary Verification

Each submitted boundary envelope contains a provider-originated event and signature.

The recorder:

1. Parses the submitted JSON envelope.
2. Extracts the claimed provider identity, operation, stage, authorization identifiers, and binding.
3. Locates the provider's registered public key.
4. Checks that the claimed key identifier matches the registered key.
5. Verifies the Ed25519 signature over the canonical event representation.
6. Records the verification outcome.

The signature domain is:

`NUVL-MP-BOUNDARY-v1|`

The recorder distinguishes valid submissions from malformed envelopes, unknown providers, mismatched keys, invalid signatures, and other verification errors.

Invalid submissions are preserved as evidence rather than silently discarded.

A valid signature establishes that the submitted event verifies against the registered public key. It does not independently establish that the provider executed an operation.

## Evidence Recording

Each recorded submission includes:

- Session identifier.
- Receipt sequence number.
- UTC and monotonic receipt timestamps.
- Source network address and port.
- SHA-256 digest of the received body.
- Base64 representation of the original submitted bytes.
- Claimed provider, operation, and boundary stage.
- Signature verification result.
- Duplicate-event observation, when applicable.

Records are written as JSON Lines (`.jsonl`).

Each record includes a sequence number, previous-record hash, and current-record hash.

The recorder flushes and calls `fsync` after appending each record.

The hash chain begins with a zero-valued genesis hash.

These records support subsequent integrity checks and event correlation.

## Session Identification

At startup, the recorder writes a `SESSION_START` record containing:

- Session identifier.
- Recorder source SHA-256.
- Provider registry SHA-256.
- Run manifest SHA-256.
- Contract SHA-256.
- Registered provider identities.

The recorder refuses to overwrite an existing log file.

An orderly keyboard-interrupt shutdown also writes a `SESSION_END` record. Abrupt termination does not guarantee that record.

The configuration hashes allow an independent reviewer to associate captured evidence with the configuration used during the test.

## Duplicate Observations

The recorder identifies repeated signed event envelopes using their canonical event and signature representation.

A previously observed signed event can be marked with `duplicate_of_seq`.

Duplicate tracking is maintained in process memory for the active recorder session.

This is an evidentiary function, not an authorization replay-prevention mechanism.

Provider-local enforcement remains responsible for preventing repeated execution of consumed authority.

## Independence and Authority Boundaries

The recorder does not:

- Issue provider authorization artifacts.
- Hold provider private signing keys.
- Approve or reject provider execution.
- Modify provider consumption ledgers.
- Coordinate execution between providers.
- Grant Provider A authority over Provider B.
- Treat event receipt as proof of completed execution.

Provider A and Provider B independently evaluate and enforce their own authorization constraints.

The association component observes their signed boundary events without becoming an additional source of execution authority.

## MP005 Evidence

Captured association records are preserved with their original test sessions.

Relevant locations include:

- [Rehearsal association evidence](../evidence/preflight/MP005_REHEARSAL_20261024_R1/association/)
- [R2 scored association evidence](../evidence/scored/MP005_SCORED_20261025_R2/association/)
- [R3 scored association evidence](../evidence/scored/MP005_SCORED_20261026_R3/association/)

The R2 scored campaign remains classified as unsuccessful.

The R3 scored campaign records successful R01 and R02 restart-durability cases within the defined test scope.

The recorder's signed boundary observations are evaluated alongside provider-local consumption ledgers, execution logs, state snapshots, and process identity evidence.

See the [MP005 test contract](../configs/MP005_CONTRACT.md) for the scored requirements and exclusions.

## Limitations

The recorder provides evidence collection and signature verification, not independent execution attestation.

Receipt timestamps establish recorder observations, not a globally authoritative ordering of events across provider machines.

The hash chain supports detection of inconsistent record modification when a trusted reference is retained. It does not, by itself, prevent an attacker with control of the complete evidence history from replacing that history.

The recorder does not implement an externally anchored freshness authority, guaranteed event delivery, or a consensus mechanism.

HTTP `204 No Content` from `/boundary` acknowledges recorder processing. It does not authorize provider execution or prove a provider completed an operation.

These limitations do not alter the provider-exclusive execution authority model evaluated in MP005.
```

