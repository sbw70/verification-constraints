```markdown
# MP005 — NUVL Intermediary

## Purpose

The intermediary provides mechanical request forwarding between a requester and two independently controlled providers.

It does not authenticate requesters, verify provider authorization artifacts, evaluate provider policy, or authorize execution.

Provider A and Provider B independently determine whether a forwarded request is permitted to produce an execution consequence.

## Implementation

**Source:** [nuvl_multi_relay.py](nuvl_multi_relay.py)

The intermediary accepts HTTP POST requests at `/nuvl`.

For each request, it:

1. Computes a SHA-256 representation of the request body.
2. Combines that representation with the supplied verification context to calculate a deterministic binding.
3. Extracts the separately supplied Provider A and Provider B authorization artifacts.
4. Constructs a provider-specific forwarding artifact containing the request representation, verification context, binding, and corresponding authorization.
5. Dispatches asynchronous HTTP POST requests to both configured providers.
6. Returns HTTP `204 No Content` to the requester.

Provider forwarding is independent. Neither provider's authorization decision controls forwarding to the other.

## Authority Boundary

The intermediary does not possess provider signing keys and does not validate or originate provider authority.

It cannot independently authorize provider execution.

The provider remains responsible for validating its authorization artifact, enforcing consumption constraints, and determining whether execution is permitted.

A relay compromise can disrupt, suppress, duplicate, or alter forwarded material. Provider authorization and execution constraints must remain effective without trusting the intermediary.

## Deployment

The source contains default network settings, including a historical Provider B address.

The MP005 live harness overrides these defaults using the deployment configuration in [MP005_RUN_MANIFEST.json](../configs/MP005_RUN_MANIFEST.json).

The intermediary is launched through [launch_service.py](../harness/launch_service.py), which performs the applicable source and configuration checks.

The relay does not maintain a durable authorization ledger or persistent execution state.

## Receipt Semantics

HTTP `204 No Content` is a relay response.

It does not establish that either provider received the request, accepted its authorization, executed an operation, or completed processing.

Forwarding errors are not returned to the requester by this implementation.

Execution and authorization outcomes must be established through provider-local state and independently captured boundary evidence.

## Evidence

The MP005 scored evidence is preserved under [evidence/scored/](../evidence/scored/).

The intermediary's role is request delivery, not authorization or execution.

The scored restart-durability results are evaluated against provider-local consumption, execution, process identity, and signed boundary records.

## Scope and Limitations

This implementation uses asynchronous HTTP forwarding without a durable delivery queue or guaranteed delivery acknowledgement.

It does not provide transport-layer encryption or mutual authentication itself.

The intermediary is intentionally excluded from provider authorization decisions.

MP005 evaluates whether provider-enforced authority constraints remain effective across the specifically tested conditions. It does not establish that the intermediary is trustworthy or that request delivery is guaranteed.
```
