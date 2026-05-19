# Schemas

This directory contains the shared schema definitions used throughout the benchmark environment.

Schemas exist to normalize communication, telemetry, workload structure, and event generation across both request paths.

The purpose of the schema layer is to ensure:
- both paths receive equivalent request intent
- services emit comparable telemetry
- benchmark events remain structurally consistent
- measurements can be aggregated reliably
- execution behavior can be analyzed uniformly

Schema definitions may include:
- request schemas
- response schemas
- event schemas
- metric schemas
- workload schemas
- trace schemas

The benchmark compares execution ordering and infrastructure behavior.

Shared schemas help ensure the comparison is based on operational sequencing rather than inconsistent data structures or telemetry formats.
