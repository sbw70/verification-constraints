# Live View

This directory contains the real-time visualization components for the benchmark environment.

The live view is responsible for presenting current execution behavior across both request paths during active benchmark operation.

Displayed information may include:
- live request throughput
- current latency measurements
- denial timing
- provider visibility timing
- infrastructure activation events
- request distribution
- timeout activity
- resource utilization

The purpose of the live view is to provide continuous operational visibility into benchmark behavior while workloads are executing.

The live view is shared so both architectures are observed using the same visualization layer and telemetry presentation model.
