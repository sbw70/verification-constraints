# NUVL Edge Lab

NUVL Edge Lab is a physical validation environment for testing provider-controlled bounded-authority architectures across constrained, distributed, and execution-capable systems.

The lab is intentionally extensible. Endpoint types, provider placement, enforcement components, execution targets, network conditions, enabled capabilities, trust relationships, and test methods may evolve as new configurations are evaluated.

The purpose of the lab is not tied to a single hardware topology or deployment pattern.

## Purpose

The lab evaluates whether defined authority constraints remain intact as capability is distributed across increasingly realistic systems.

Testing may include conditions such as:

- constrained and embedded endpoints
- heterogeneous distributed systems
- physically separate provider infrastructure
- intermittent, degraded, or unavailable connectivity
- shared infrastructure failures
- endpoint isolation and recovery
- overlapping and concurrent requests
- provider-established bounded authority
- disconnected authority use
- persistent usage-state enforcement
- replay and temporal constraints
- crash and recovery boundaries
- physical execution interfaces
- load and fault conditions
- unauthorized component substitution
- degraded or adversarial operating environments

The objective is not simply to demonstrate successful operation.

The objective is to determine whether authority remains bounded by the component or trust relationship intended to establish it when the surrounding system becomes more complex, unreliable, distributed, or adversarial.

## NUVL Core

NUVL is a verification and constraint architecture intended to preserve separation between distributed system components and provider-established execution authority.

NUVL does not independently:

- establish authorization policy
- originate provider authority
- enlarge provider authority
- reinterpret bounded authority into broader authority
- convert observation or representation into authorization
- acquire authority through network position or execution proximity
- require possession of provider signing authority in order to verify or enforce provider-established constraints

The governing invariant is:

> **Authority accepted for execution must remain within provider-established bounds and must not be independently originated or enlarged by intermediary or enforcement components.**

A request, artifact, representation, observation, network position, or execution result does not by itself confer authority.

## Authority Separation

A NUVL deployment may separate authority establishment, verification, enforcement, and execution across different components.

For example:

    Provider / Authority Source
    establishes bounded authority
             |
             v
    Verification / Enforcement Boundary
    authenticates and constrains
             |
             v
    Endpoint / Execution Target
    performs permitted action

These roles may be physically colocated or distributed across separate systems.

The critical property is not physical placement.

The critical property is whether each component remains limited to the authority assigned to its role.

A verification or enforcement component may recognize and enforce provider-established authority without receiving the ability to originate equivalent provider authority.

## Enabled Capabilities

The lab also validates optional modules and integrations that operate alongside the core authority model.

These may introduce functions such as:

- request-bound artifact exchange
- asymmetric provider authentication
- disconnected or air-gapped operation
- provider-established bounded-use authority
- persistent spent-state enforcement
- replay protection
- temporal constraints
- crash-consistent state handling
- constrained endpoint participation
- multi-endpoint coordination
- multi-domain or multi-provider operation
- downstream execution binding
- physical effectors
- autonomous execution schedules
- separate-provider deployment
- provider-substitution controls
- additional verification or witness components

These capabilities are not assumed to be part of the NUVL core.

An integrated implementation may become stateful, persistent, execution-aware, cryptographically specialized, or topology-dependent because a particular capability requires those properties.

The relevant architectural question is whether the additional capability preserves the governing authority invariant.

## Edge Validation

The edge lab provides a controlled environment for moving authority-constraint architectures beyond abstract or software-only demonstrations.

Tests may combine:

- real embedded endpoints
- provider services
- independent verification boundaries
- persistent state
- physical actuators
- network faults
- provider outages
- restart and crash conditions
- concurrent requests
- unauthorized substitutes
- load conditions
- execution witnesses
- intentionally adverse behavior

Individual properties can be isolated before being combined into more representative operational configurations.

Where appropriate, tests distinguish among:

- NUVL core validation
- optional capability integration
- implementation behavior
- deployment variation
- architecture change

An architecture change occurs when authority placement, trust relationships, architectural invariants, or component responsibilities materially change.

Adding a new endpoint, provider host, execution interface, fault condition, witness, transport, or optional capability does not by itself constitute an architecture change.

## Current Validation Areas

The lab has been used to evaluate properties including:

- provider-authenticated authority
- asymmetric Ed25519 provider signing
- public-key verification at an independent boundary
- provider-unavailable fail-closed behavior
- bounded disconnected single-use authority
- persistent spent-state enforcement
- concurrent double-spend handling
- commit-before-accept durability
- crash and restart behavior
- multi-endpoint operation
- physical actuator execution
- recovery without endpoint reprovisioning
- physically separate provider infrastructure
- unauthorized provider substitution

These areas represent current validation work, not a closed definition of the lab's future scope.

Additional authority models, execution environments, provider configurations, endpoint classes, and enforcement mechanisms may be incorporated where they can be tested without obscuring the authority relationships being evaluated.

## Validation Principles

A passing test supports only the property exercised by that test.

The lab maintains a distinction between:

- configured behavior
- expected behavior
- observed behavior
- software-reported behavior
- retained runtime evidence
- physical observation
- test-harness behavior
- architectural inference

Failures, anomalies, and unresolved conditions are retained when they materially affect interpretation of a result.

Observed behavior is not generalized beyond the tested configuration without additional evidence.

A later test may strengthen, narrow, supersede, or expose limits in an earlier conclusion without changing the original test record.

## Claim Discipline

The lab does not treat implementation proximity, representation, or successful communication as proof of authority.

For example:

- an endpoint reporting successful execution does not independently prove physical execution
- possession of a public verification key does not confer provider signing authority
- a stored or signed representation does not become admissible authority merely because it exists
- occupying an expected network position does not establish provider authority
- reproducing a provider identifier or artifact structure does not establish cryptographic authority
- successful operation under one failure condition does not establish behavior under all failure conditions
- coordinated activity does not necessarily demonstrate simultaneous execution
- replay rejection in one state model does not establish persistence under another
- recovery from a tested interruption does not establish recovery from every possible interruption point
- fail-closed behavior at one interface does not establish that every component or compromise condition fails closed
- verification at an intermediary does not establish verification at the endpoint

Broader claims require separate evidence.

## Evidence Model

Individual experiments are expected to distinguish among:

- test purpose and architecture
- executed conditions
- observed outcomes
- artifact provenance
- retained runtime evidence
- publication integrity
- supported claims
- claim boundaries

Where historical test artifacts and current publication artifacts differ, their identities are maintained separately.

Current repository integrity does not replace historical test provenance, and historical test identity does not substitute for integrity verification of current published bytes.

## Scope

NUVL Edge Lab is an engineering validation environment.

It is used to examine how provider-controlled bounded-authority architectures behave as they are applied to increasingly distributed, constrained, persistent, autonomous, and execution-capable systems.

Individual experiments define their own:

- architecture
- test variable
- implementation
- trust relationships
- procedures
- evidence
- limitations
- supported conclusions

The lab is not limited to the current ESP32, Raspberry Pi, Ed25519, provider-host, or actuator configurations.

Future work may introduce different endpoints, providers, cryptographic mechanisms, enforcement boundaries, execution systems, networks, state models, autonomous components, or domain-specific integrations.

The governing question remains:

> **Can a distributed system gain additional capability without allowing authority to migrate, expand, or be recreated by components that were never intended to possess it?**
