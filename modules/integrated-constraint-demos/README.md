# Integrated Constraint Demos

## Overview

This directory contains composed, system-level demonstrations that integrate multiple constraint modules into cohesive execution scenarios.

Each build combines NUVL with one or more extension architectures (multi-hub, multi-domain, quorum, temporal, offline relay, adaptive provider thresholds, etc.) to demonstrate composability without migrating authorization authority into intermediaries.

Across all demos:

- NUVL binds and forwards only.
- Intermediary components route, relay, or aggregate mechanically.
- Provider-controlled systems exclusively determine initiation.
- Execution authority never centralizes.

These are integration demonstrations, not standalone modules.

---

## Design Intent

These demos are intended to:

- Show how constraint modules compose without semantic collapse
- Demonstrate distributed routing without authority migration
- Exercise quorum aggregation without centralized execution control
- Validate adaptive provider thresholds under concurrency
- Simulate offline and failover scenarios while preserving boundary separation
- Demonstrate scale under multi-provider and multi-region load

They represent architectural range, not policy frameworks.

---

## Demonstration Categories

### Region Failover + Quorum

Demonstrates distributed NUVL fronts routing domain-scoped requests across regionally distributed provider authorities.

Quorum aggregation is mechanical and non-authoritative.  
Provider initiation remains independent per provider boundary.

---

### Offline Relay + Temporal Gatekeeping

Demonstrates artifact relay buffering during simulated provider blackout conditions.

NUVL binds and forwards only.  
Relay components buffer without interpreting semantics.  
Provider-controlled systems retain exclusive authority to initiate once reachable.

---

### Multi-Hub / Multi-Domain Mesh

Demonstrates multiple hubs routing opaque domain traffic across distributed providers.

Routing logic remains transport-level.  
Domain separation is mechanical.  
Authority remains provider-scoped.

---

### Distributed Provider Initiation (High Concurrency)

Demonstrates multi-provider stress behavior with adaptive provider-side thresholds and deterministic Byzantine modeling.

NUVL remains outcome-blind.  
Provider boundaries independently evaluate artifacts.

---

### Two-Region Quorum Audit

Demonstrates independent hub meshes across regions with non-authoritative quorum observation.

Aggregation logic computes summary state but does not initiate execution.  
Providers initiate exclusively within their own boundaries.

---

## Architectural Invariants

Across all integrated demonstrations:

- NUVL holds no signing keys.
- NUVL evaluates no authorization semantics.
- Hubs and relays do not initiate execution.
- Quorum mechanisms do not create centralized authority.
- Temporal buffering does not alter initiation semantics.
- Adaptive provider logic remains provider-controlled.
- Compromise of intermediary components does not grant execution capability.

Composition does not collapse boundary separation.

---

## Scope

These builds are demonstrative and intentionally minimal.

They do not:

- Provide production orchestration frameworks
- Provide identity or credential systems
- Provide distributed consensus authority
- Provide centralized policy engines
- Guarantee network delivery or liveness
- Replace provider security controls

They illustrate architectural range while preserving authority constraints.

---

## Relationship to Constraint Modules

The individual modules in `/modules` define architectural constraints in isolation.

This directory demonstrates how those constraints can be composed into:

- Multi-provider systems
- Multi-hub meshes
- Cross-domain routing topologies
- Region failover scenarios
- Temporal buffering systems
- Quorum observation layers

The structural separation between artifact conveyance and authorization control remains intact under composition.

---

## License


These integrated modules are not released under the Apache 2.0 license applied to the repository root.

Commercial licensing terms apply.

Non-commercial research evaluation may be available upon request.
