# MD001 — Frozen Runtime Components

This directory contains the four runtime modules used by the MD001 physical application.

The modules provide signed-artifact verification, mechanical request forwarding, static route validation, and bounded HTTP transport handling.

They are imported by [`../md001.py`](../md001.py). The deployment adapter verifies their SHA-256 hashes against [`../RUNTIME_LOCK.json`](../RUNTIME_LOCK.json) before executing its commands.

## File inventory

| File | Responsibility |
|---|---|
| `artifact.py` | Canonical signed assertions, Ed25519 signatures, public-key trust binding, and verification |
| `hub.py` | Mechanical request forwarding and transport observations |
| `routes.py` | Strict static routing configuration and topology validation |
| `wire.py` | HTTP/1 request and response framing, header handling, and socket transport |

## Artifact verification

`artifact.py` defines the MD001 signed-assertion format.

A signed event contains:

- `version`
- `producer_id`
- `key_id`
- `artifact_id`
- `event_id`
- `outcome`

The producer signs a domain-separated canonical JSON representation of the event using Ed25519.

The verifier checks the envelope structure, canonical encoding, producer-to-public-key binding, signature, and local acceptance criteria.

For the published test, the accepted event criteria are:

- `event_id` equals `LOCAL_SORT_V1`.
- `outcome` equals `SUCCESS`.

Verification returns an explicit acceptance result and reason.

This module does not perform the underlying operation, access the network, consult an artifact-history ledger, or grant execution authority.

A valid signature establishes that the signed assertion matches the trusted signing key. It does not independently prove that the asserted physical event occurred.

## Mechanical relay

`hub.py` contains the frozen MH001 forwarding implementation used by the deployment adapter.

It selects a configured downstream route using the `X-MH-Destination` request header.

Its behavior includes:

- Static destination selection.
- Preservation of the request body.
- One downstream send attempt without automatic retry.
- Forwarding of the downstream response.
- JSON-lines observations of ingress and transport outcomes.

The relay records body hashes and transport status. Its egress hash is a forwarding observation, not independent proof that the downstream host received the bytes.

The relay does not verify the MD001 artifact signature or determine whether the assertion should be accepted.

## Static routing

`routes.py` validates the frozen MH001 routing structure.

It requires numeric endpoint addresses, expected hub identities, defined destination mappings, fixed timeout values, and non-looping routes.

The module does not perform DNS resolution or contact network hosts when loading a configuration.

MD001's deployment adapter constructs an effective `HUB_B` configuration for the physical relay. The unused `PROVIDER_A` route terminates at a local denial responder; the selected `PROVIDER_B` route points to the HP ingress.

This arrangement reuses the frozen forwarding implementation without giving the relay artifact-verification authority.

## HTTP transport

`wire.py` implements bounded HTTP/1 transport parsing and forwarding.

It enforces request framing and size constraints, rejects unsupported transfer modes, and handles hop-by-hop headers separately from preserved headers.

The request body limit is 65,536 bytes.

Outbound connections use configured numeric IP addresses. The implementation does not introduce DNS discovery, redirect following, automatic failover, or retries.

The transport implementation is experimental infrastructure, not a general-purpose HTTP proxy.

## Runtime integrity

The four source files are listed in [`../RUNTIME_LOCK.json`](../RUNTIME_LOCK.json).

The deployment adapter checks each runtime file's SHA-256 digest before executing a command.

To inspect the recorded values:

```sh
cat RUNTIME_LOCK.json
```

Run this command from the MD001 experiment root.

The lock protects against unintended changes to these runtime files. It does not establish the integrity of the operating system, Python interpreter, installed dependencies, or physical network.

Do not edit or replace these source files when reproducing the published experiment. A changed source file requires a separately identified implementation baseline and new integrity evidence.

## Dependency

The published root requirements file specifies:

```text
cryptography==49.0.0
```

The Python standard library supplies the other imported functionality in these four modules.

## Experimental boundaries

The runtime separates mechanical transport from artifact verification.

The relay can forward an assertion without possessing the producer's private signing key or making the verifier's acceptance decision.

The verifier evaluates the signed assertion against its own provisioned public-key trust and local criteria.

Neither function should be confused with authorization to initiate or repeat the underlying operation.

For the experiment's scored procedures, physical observations, and limitations, consult the parent MD001 documentation and retained evidence directories.
