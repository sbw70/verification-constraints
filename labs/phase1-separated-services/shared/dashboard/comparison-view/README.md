# Comparison View

This directory contains the side-by-side comparison visualization components for the benchmark environment.

The comparison view exists to display operational differences between the conventional and provider-first request paths under equivalent workload conditions.

Displayed comparisons may include:
- end-to-end latency
- denial timing
- provider visibility timing
- infrastructure activation depth
- request throughput
- timeout behavior
- resource utilization
- pre-denial data interaction
- execution path sequencing

The purpose of the comparison view is to make request-ordering behavior observable across both architectures using the same telemetry and visualization model.

The comparison layer is shared so benchmark results remain directly comparable between paths.
