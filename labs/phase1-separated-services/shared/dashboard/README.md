# Dashboard

This directory contains the shared visualization and monitoring infrastructure for the benchmark environment.

The dashboard layer exists to provide live operational visibility into both benchmark paths during execution.

Dashboard components are shared so conventional and provider-first architectures are measured and displayed using the same telemetry, visualization logic, and comparison model.

Displayed information may include:
- live throughput
- latency measurements
- provider visibility timing
- denial timing
- infrastructure activation depth
- request traces
- timeout behavior
- resource utilization
- system health
- side-by-side execution comparison

The purpose of the dashboard layer is to make request-ordering behavior observable during benchmark operation.

The dashboard is not intended to act as a policy engine or execution component.

Its purpose is operational visibility and benchmark instrumentation.
