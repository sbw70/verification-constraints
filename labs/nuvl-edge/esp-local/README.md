# ESP-LOCAL

This directory contains NUVL work focused on endpoint-local recognition, validation, enforcement, and execution on ESP-class hardware.

ESP-LOCAL explores how bounded authority can be enforced at or near a constrained endpoint while keeping authority generation external to that endpoint.

## Scope

Content in this directory may include:

- endpoint firmware,
- provider-generated authority material,
- local validation and enforcement logic,
- persistent state handling,
- actuator and execution-path implementations,
- independent witness components,
- fault-injection variants,
- test procedures,
- results,
- provenance records,
- reproducibility artifacts,
- preserved evidence.

Individual subdirectories define their own hardware, implementation, topology, procedures, evidence, limitations, and supported claims.

Not every subdirectory is expected to use the same components or test method.

## Architectural Principle

Endpoint-local enforcement does not imply endpoint-local authority.

A local endpoint may recognize, validate, consume, constrain, or enforce authority established elsewhere.

It must not independently originate, enlarge, substitute, or regenerate authority beyond the bounds established by the authority source.

The governing distinction is:

**Local capability is not local authority.**

## Fail-Closed Behavior

ESP-LOCAL implementations are expected to avoid creating executable authority from uncertainty.

Conditions such as invalid authority, replay, missing state, malformed state, failed verification, or incomplete recovery must not silently enlarge or recreate authority.

Availability is not treated as justification for manufacturing authority.

## Repository Organization

Documentation is scoped to the directory in which it appears.

Subdirectories may contain:

- `README.md` for local scope and purpose,
- `RESULTS.md` for observed results,
- `PROVENANCE.md` for artifact lineage,
- `SHA256SUMS.txt` for artifact verification,
- firmware,
- provider material,
- witness implementations,
- evidence.

Detailed procedures, implementation notes, results, and limitations are documented within the relevant subdirectory.

## Reproduction

ESP-LOCAL material is published to support inspection and reproduction of the tested behavior.

Where available, subdirectories may include the exact source, binaries, test material, state captures, witness implementations, and supporting artifacts used during testing.

## Relationship to NUVL

ESP-LOCAL is a NUVL implementation and test area focused on constrained endpoint placement.

The directory examines how recognition and enforcement can move closer to the execution endpoint while preserving externally bounded authority.
