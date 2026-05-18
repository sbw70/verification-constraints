# Shared Components

This directory contains infrastructure and services shared between both benchmark paths.

Shared components are used to keep workload generation, identity behavior, metrics collection, and visualization consistent across the comparison environment.

The purpose of the shared layer is to reduce unnecessary variables so request ordering remains the primary comparison focus.

Shared components may include:
- identity services
- dashboard and visualization
- metrics collection
- load generation
- workload definitions
- request schemas
- shared utilities

Both paths should operate against the same:
- request types
- token behavior
- workload intensity
- outcome vocabulary
- measurement model

This helps ensure the comparison measures operational differences caused by request ordering rather than unrelated infrastructure variation.
