# MD001 — Multi-Domain Stateless Verification

**Project:** Xer0trust / Verification Constraints  
**Experiment:** MD001  
**Scope:** Signed assertion transport and independent verification across separated domains

## Overview

MD001 examines whether a domain can produce a signed assertion about a completed local operation, convey that assertion through a mechanical intermediary, and have another domain independently verify it.

The intermediary does not receive the producer's private signing key, determine the asserted operation's outcome, or acquire authority to execute the operation.

The experiment separates three functions:

1. Local operation and assertion production.
2. Mechanical transport across domain boundaries.
3. Independent cryptographic verification.

MD001 tests assertion verification. It does not implement a shared authorization service or grant execution authority to the receiving domain.

## Physical test architecture

The published physical deployment uses three principal hosts:

| Role | Host | Laboratory address |
|---|---|---|
| Domain A producer | Dell laptop | `10.10.10.10` |
| Mechanical relay | Raspberry Pi | `30.30.30.30` |
| Domain B verifier | HP laptop | `40.40.40.40` |

The request path is:

```text
Domain A — Dell
Local operation
Ed25519 signed assertion
        |
        v
Raspberry Pi
Mechanical forwarding
No assertion verification authority
        |
        v
Domain B — HP
Ingress adapter
Independent verifier
Public-key trust configuration
```

The HP ingress and verifier are separate application components.

The physical test also uses network segmentation, routing controls, application observations, and packet-capture evidence.

These are distinct controls. Application-level forwarding alone does not prove network isolation.

## Scored physical cases

Three scored case directories are published.

### B01 — Valid signed assertion

Directory:

`B01_SCORED_20261119_223940/`

Domain A performs the local `LOCAL_SORT_V1` operation and produces an Ed25519-signed assertion.

The assertion travels through the Raspberry Pi relay to Domain B.

The verification objective is to establish that Domain B can evaluate the signed assertion independently, using its provisioned public trust configuration.

The evidence includes application observations and packet-capture material for examining artifact transport.

### N01 — Downstream mutation

Directory:

`N01_SCORED_20261119_224654/`

A valid signed assertion is transported through the relay.

After relay forwarding, the HP ingress deliberately changes the signed `event.outcome` value without replacing the signature.

The verifier is expected to reject the altered assertion with `invalid_signature`.

The negative case distinguishes transport of the original assertion from verification of the downstream-modified assertion.

### B02 — Independent re-verification

Directory:

`B02_SCORED_20261119_225126/`

The original signed B01 assertion is retained independently of its producer.

The test evaluates whether a fresh verifier can verify the retained assertion without obtaining a new assertion or contacting the original producer.

This is verification of historical signed evidence.

It is not a new authorization decision and does not cause the original operation to execute again.

## Evidence interpretation

The physical scored directories contain case-specific evidence.

Relevant material includes:

- Producer and verifier records.
- Original and modified artifacts.
- Application ingress and egress observations.
- Packet-capture files and extracted streams.
- Artifact byte comparisons.
- Process and configuration information.
- Cryptographic verification decisions.

Evidence should be evaluated from the applicable case directory.

A relay egress diagnostic records forwarding behavior; it is not, by itself, proof that a complete request arrived on the downstream wire.

Packet capture and stream reconstruction provide separate observations and must be interpreted within their capture and reconstruction limits.

The existence of a scored directory is not a substitute for checking its individual result records and evidence.

## Original desktop baseline

Directory:

[`MULTI_DOMAIN_001/`](MULTI_DOMAIN_001/)

MD001 began as a local desktop implementation.

Its final selected offline validation was:

`20261112T025926Z_4d05fe22`

Recorded result:

**21 PASS — 0 FAIL**

Status:

`MD001_LOCAL_BUILD_VALIDATED_NOT_DEPLOYED`

The desktop baseline exercised B01, N01, and B02 using local processes and loopback transport.

It did not establish physical network separation, physical producer power loss, or independent packet-capture reconstruction.

The original desktop evidence and source references remain retained separately.

## Physical adapter validation

Directory:

[`validation/`](validation/)

Before deployment, the physical application adapter underwent local integration validation.

Recorded final results:

| Validation category | PASS | FAIL |
|---|---:|---:|
| Adapter integration | 12 | 0 |
| HTTP extraction | 6 | 0 |
| Total | 18 | 0 |

These checks preceded the physical campaign and must not be counted as additional physical scored cases.

Earlier unsuccessful attempts remain preserved.

## Implementation

The outer MD001 directory contains the physical deployment adapter and supporting utilities.

| Path | Purpose |
|---|---|
| `md001.py` | Application adapter and service entry point |
| `observe.py` | HTTP artifact extraction from supplied stream bytes |
| `runtime/` | Retained assertion and mechanical forwarding modules |
| `configs/` | Laboratory application configurations |
| `test_local.py` | Local adapter integration tests |
| `test_observe.py` | HTTP extraction tests |
| `requirements.txt` | Python dependency declaration |
| `RUNTIME_LOCK.json` | Runtime source identity |
| `ORIGINAL_PROJECT_LOCK.json` | Original desktop-project preservation inventory |

The runtime uses Ed25519 signature verification through the Python `cryptography` package.

The verifier evaluates assertions using a public trust configuration.

It does not need the producer's private signing key.

## Trust and authority boundaries

MD001 distinguishes:

**Assertion:** A signed statement about an operation or event.

**Verification:** A local decision that the assertion satisfies signature, schema, key-binding, and other configured acceptance checks.

**Authorization:** Permission to initiate an operation.

**Execution:** The actual performance of an operation.

A valid signed assertion is not automatically authorization for another operation.

The relay cannot make a modified assertion valid merely by forwarding it.

The verifier cannot infer physical execution solely from a valid signature; it verifies the producer's signed claim.

## What MD001 does not establish

MD001 does not, by itself, establish:

- Single-use authorization consumption.
- Durable SPENT-state enforcement.
- Replay prevention for execution authority.
- Authorization issuance by the relay.
- Hardware actuation isolation.
- Protection against a compromised producer signing key.
- Truthfulness of assertions issued by a compromised or dishonest producer.
- Confidentiality of plaintext transport.

Those are separate security properties requiring separate controls and evidence.

## Documentation

Start with the following files for the specific part of the experiment being reviewed.

| Document | Purpose |
|---|---|
| [`TEST_PLAN.md`](TEST_PLAN.md) | Physical case requirements and observation plan |
| [`COMMANDS.md`](COMMANDS.md) | Recorded operator command procedures |
| [`VALIDATION.md`](VALIDATION.md) | Predeployment adapter validation |
| [`X01.md`](X01.md) | Artifact and transport disclosure inventory |
| [`configs/README.md`](configs/README.md) | Physical application configuration |
| [`runtime/README.md`](runtime/README.md) | Runtime source boundaries |
| [`validation/README.md`](validation/README.md) | Local validation evidence |
| [`MULTI_DOMAIN_001/README.md`](MULTI_DOMAIN_001/README.md) | Original desktop baseline |
| [`MULTI_DOMAIN_001/PROVENANCE.md`](MULTI_DOMAIN_001/PROVENANCE.md) | Original source provenance |
| [`MULTI_DOMAIN_001/SOURCE_REUSE.md`](MULTI_DOMAIN_001/SOURCE_REUSE.md) | Historical source reuse |

Some planning documents retain their original predeployment language. Their historical status must not be silently rewritten to imply that a later physical run had already occurred.

## Reproduction and integrity

The repository retains source identities, configuration files, evidence, and SHA-256 inventories.

Use the published commands and case-specific records to understand the tested configuration.

Do not execute deployment commands merely to inspect the repository.

SHA-256 manifests establish recorded file identities. They do not independently authenticate the experiment operator or prove that an observed event occurred.

Historical evidence directories, manifests, original source snapshots, and test keys must remain unchanged.

New reproduction attempts should use separate evidence directories and new run identities.

## Conclusion

MD001 investigates the separation of assertion production, mechanical transport, and independent verification.

Its central boundary is that conveying verification material does not transfer the producer's signing authority or the receiving verifier's decision authority to the intermediary.

The scope of each demonstrated property is limited to the corresponding implementation, configuration, and retained evidence.
