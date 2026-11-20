# MD001 — Desktop Baseline Source

This directory contains the original MD001 desktop-baseline implementation.

The baseline evaluates signed verification assertions across separately launched local processes, using loopback network transport.

It is distinct from the later physical deployment implementation in the outer MD001 directory.

## Source files

| File | Purpose |
|---|---|
| `artifact.py` | Signed assertion creation, canonical encoding, public-key trust binding, and verification |
| `service.py` | Desktop producer, verifier, relay, observation tap, and mutation adapter |

## Signed assertion implementation

`artifact.py` defines the MD001 version 1 artifact.

The envelope contains exactly two fields:

- `event`: the signed assertion.
- `signature`: the Ed25519 signature.

The event contains exactly six fields:

- `version`
- `producer_id`
- `key_id`
- `artifact_id`
- `event_id`
- `outcome`

The signed message consists of the domain-separation prefix:

```text
NUVL-MD001-ARTIFACT-v1|
```

followed immediately by canonical UTF-8 JSON of the event.

The verifier checks the envelope, field constraints, canonical encoding, locally provisioned producer/public-key binding, Ed25519 signature, and local event criteria.

The published acceptance criteria require `LOCAL_SORT_V1` and `SUCCESS`.

The verifier does not consult previous artifact IDs, cached decisions, producer databases, network services, or an authorization-consumption ledger.

See [`../ARTIFACT_CONTRACT.md`](../ARTIFACT_CONTRACT.md) for the complete contract.

## Desktop service adapters

`service.py` provides separate process roles:

| Role | Behavior |
|---|---|
| `producer` | Executes the local sort fixture, records completion, and creates a signed artifact |
| `verifier` | Evaluates received artifacts against locally provisioned public-key trust |
| `relay` | Launches the frozen MH001 mechanical forwarding implementation |
| `tap` | Observes and forwards received artifact bytes |
| `tamper` | Changes the signed outcome field without replacing the signature |

The producer sorts `[9, 1, 4, 2]` and checks the result against `[1, 2, 4, 9]` before recording `LOCAL_SORT_V1` completion.

The service adapters use loopback HTTP for the desktop baseline.

The relay imports the frozen MH001 hub implementation from the retained reference directory. It does not implement a separate authorization or verification decision.

The mutation adapter changes the assertion's `outcome` to `FAILURE`, while retaining the original signature.

This permits a negative test of signature integrity.

## Baseline test cases

The desktop harness in [`../tests/run_offline.py`](../tests/run_offline.py) orchestrates three baseline scenarios.

### B01 — Valid assertion

The producer completes the local operation, creates a signed artifact, and sends it through the simulated request path.

The verifier evaluates the assertion using its locally provisioned public key and acceptance criteria.

### N01 — Modified assertion

A valid signed artifact is modified downstream of the relay without replacing its signature.

The verifier is expected to reject the modified assertion.

### B02 — Independent re-verification

The original producer process is terminated and the original verifier process is replaced.

A new verifier process evaluates the retained B01 artifact.

This tests whether verification depends on the original producer remaining available or on the previous verifier's process state.

The baseline does not establish physical power-loss behavior.

## Evidence and limitations

The desktop harness preserves operation records, signed artifacts, transport observations, decisions, process identities, configuration information, and run-specific evidence.

These records support inspection of the simulated test path.

However, the desktop baseline uses processes and loopback transport under a single operating environment.

It does not independently establish:

- Physical network separation.
- Independent host or power domains.
- Physical disconnection of the producer.
- Hardware execution enforcement.
- Authorization consumption or replay prevention.

The later physical experiment must be evaluated using its own recorded evidence.

## Source provenance

The baseline reuses selected established implementation patterns and the frozen MH001 relay.

The source-reuse analysis is documented in [`../SOURCE_REUSE.md`](../SOURCE_REUSE.md).

Historical reference snapshots are retained under [`../reference/`](../reference/) for inspection and provenance.

Those snapshots must not be confused with additional executable dependencies of the assertion verifier.

## Reproduction

From the outer MD001 directory, with the documented Python dependency installed:

```sh
python -B MULTI_DOMAIN_001/tests/run_offline.py
```

For the original manifest verification:

```sh
python -B MULTI_DOMAIN_001/manifest.py --check
```

The offline harness requires loopback socket access and creates a new evidence directory for each run.

Consult [`../README.md`](../README.md) and [`../COMPLETION.md`](../COMPLETION.md) for the baseline's recorded validation status, evidence locations, and limitations.

## Verification boundary

A valid signed assertion establishes that the artifact was signed by a key bound to a locally trusted producer identity and that its contents satisfy the verifier's criteria.

It does not independently prove the underlying event occurred, and it does not authorize execution or re-execution.

The producer controls the asserted operation outcome. The verifier controls its own acceptance decision. The intermediary transports the artifact without acquiring either responsibility.
