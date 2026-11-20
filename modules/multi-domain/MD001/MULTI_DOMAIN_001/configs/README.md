# MD001 — Proposed Network Configuration

This directory contains the original proposed network configuration for the MD001 desktop-baseline project's planned physical extension.

The configuration is retained as historical design material.

It is not an executable deployment script and must not be treated as the configuration of the subsequently completed physical experiment.

## File inventory

| File | Purpose |
|---|---|
| `deployment.PROPOSED.json` | Unapproved VLAN, addressing, switch-port, and application-endpoint design |

## Original approval status

The configuration explicitly records:

```text
DESIGN_ONLY_UNAPPROVED_DO_NOT_APPLY
```

It also records that address-conflict checks and physical-interface inventory were incomplete.

These status fields describe the original design stage. They must not be retroactively changed to represent later deployment.

## Proposed network design

The original design specified three isolated laboratory domains:

| Role | Proposed address | VLAN |
|---|---|---|
| Domain A — Producer | `10.77.10.10/24` | 10 |
| Domain B — Verifier | `10.77.20.10/24` | 20 |
| Relay | `10.77.30.10/24` | 30 |

The proposal also specified an OPNsense VLAN trunk, managed-switch port assignments, and a separate management network.

These addresses and port assignments were proposed values, not observations of an installed configuration.

## Proposed request path

The intended application path was:

```text
Domain A
    |
    v
Relay — TCP 18081
    |
    v
Domain B — TCP 18443
    |
    v
Artifact verification
```

The relay was intended to forward an artifact without interpreting its signature or making the verifier's acceptance decision.

The proposal used HTTP/1.1 over an isolated laboratory network, without TLS.

Port 18443 was an application port number, not a claim of encrypted transport.

## Network restrictions

The design called for:

- Blocking direct Domain A-to-Domain B communication.
- Allowing the producer to reach the relay.
- Allowing the relay to reach the verifier domain.
- Retaining operator management access.
- Excluding unintended IPv6, wireless, VPN, or alternate network paths.
- Recording effective firewall rules and observed connection attempts.

A proposed firewall rule is not evidence that the rule was installed or enforced.

## Relationship to the physical experiment

The later MD001 physical deployment uses separate implementation files and recorded network observations.

Do not substitute this proposed configuration for:

- The physical deployment's actual addresses.
- Exported firewall rules.
- Observed switch configuration.
- Scored-run process configurations.
- Captured network traffic.

The later experiment must be evaluated against its own published configuration and evidence.

## Historical provenance

The original planning document is:

[`../DEPLOYMENT_PLAN.md`](../DEPLOYMENT_PLAN.md)

That document records the proposed network design, unresolved prerequisites, approval gates, and preflight requirements.

The proposed ESP extension is separately documented in:

[`../PHYSICAL_EXTENSION_PLAN.md`](../PHYSICAL_EXTENSION_PLAN.md)

Neither plan establishes that the proposed changes were deployed or that the planned ESP extension was executed.

## Preservation

Retain `deployment.PROPOSED.json` unchanged.

Its original content is part of the historical desktop-baseline record.

Any future deployment configuration must be identified separately rather than replacing this design artifact.

The configuration describes intended network boundaries. Actual boundary enforcement requires independent operational evidence.
