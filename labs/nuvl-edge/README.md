# NUVL Edge Lab

NUVL Edge Lab is a physical validation environment for testing NUVL and related provider-controlled verification constraint architectures under real-world edge conditions.

The lab is designed to evolve. Endpoint types, execution targets, network conditions, enabled modules, and test methods may change without altering the purpose of the environment.

## Purpose

The lab evaluates whether architectural authority constraints remain intact when implemented across distributed and resource-constrained systems.

Testing focuses on conditions such as:

- constrained and embedded endpoints
- heterogeneous distributed systems
- intermittent or unavailable connectivity
- shared infrastructure failures
- endpoint isolation and recovery
- overlapping and repeated requests
- bounded provider-established authority
- persistent enforcement
- physical execution interfaces
- load and fault conditions
- degraded operating environments

The objective is not simply to demonstrate successful operation.

The objective is to determine whether the defined authority boundaries remain intact when the surrounding system becomes more complex, unreliable, distributed, or adversarial.

## NUVL Core

NUVL is a stateless intermediary designed to preserve a structural separation between distributed system components and provider-controlled execution authority.

NUVL does not independently:

- establish authorization policy
- originate provider authority
- hold provider signing authority
- enlarge or reinterpret authority
- convert observation into authorization
- acquire execution authority through proximity to execution

The governing invariant is:

> **Execution authority remains scoped to the provider-controlled boundary.**

A request, representation, observation, or result passing through an intermediary does not grant that intermediary independent authority to determine execution meaning.

## Enabled Capabilities

The lab also validates optional architectural modules and integrations that may operate alongside NUVL.

These may introduce additional functions such as:

- request-bound artifact exchange
- disconnected or air-gapped operation
- provider-established bounded authority
- persistent usage-state enforcement
- replay and temporal constraints
- constrained endpoint participation
- multi-domain or multi-provider operation
- downstream execution binding
- physical effectors

These capabilities are not the NUVL core.

An integrated implementation may become stateful, persistent, or execution-aware because a particular capability requires those properties while NUVL itself remains stateless.

The relevant architectural question is whether the added capability preserves the original authority boundary.

## Edge Validation

The edge lab provides a controlled environment for moving constraint architectures beyond abstract or software-only examples.

Tests may combine real endpoints, intermediaries, execution boundaries, network faults, provider unavailability, physical consequences, and intentionally adverse behavior.

This allows individual properties to be exercised independently before they are combined into more representative operational conditions.

Where appropriate, tests distinguish between:

- core architecture validation
- optional capability integration
- implementation behavior
- architecture changes

An architecture change occurs when authority placement, trust relationships, architectural invariants, or component responsibilities change.

Adding a new endpoint, execution interface, fault condition, or optional capability does not by itself constitute an architecture change.

## Validation Principles

A passing test supports only the property exercised by that test.

The lab maintains a distinction between:

- expected behavior
- observed behavior
- software-reported behavior
- physical observation
- test-harness behavior
- architectural inference

Failures and unresolved anomalies are retained when they materially affect interpretation of a result.

Observed behavior is not generalized beyond the tested configuration without additional evidence.

## Claim Discipline

The lab does not treat implementation proximity as proof of authority.

For example:

- an endpoint reporting successful execution does not independently prove physical execution
- a stored representation does not become authority merely because it can be verified
- successful operation under one failure condition does not establish behavior under all failure conditions
- coordinated activity does not necessarily demonstrate parallel execution
- replay rejection in one state model does not establish persistence under another
- recovery from a tested interruption does not establish recovery from every possible interruption point

Broader claims require separate validation.

## Scope

NUVL Edge Lab is an engineering validation environment.

It is used to test how provider-controlled verification constraints behave as they are applied to increasingly realistic distributed systems and operating conditions.

Individual experiments document their own implementation details, test procedures, evidence, limitations, and supported conclusions.

The lab itself remains centered on one question:

> **Can distributed systems gain additional capability without allowing execution authority to migrate to components that were never intended to possess it?**
