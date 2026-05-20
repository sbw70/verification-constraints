# Metrics

This directory contains shared metric collection and aggregation logic for the benchmark environment.

The metrics layer exists to capture execution behavior consistently across both request paths.

Responsibilities may include:
- latency measurement
- throughput measurement
- denial timing measurement
- infrastructure activation tracking
- resource utilization tracking
- provider timing analysis
- pre-denial execution tracking
- event aggregation

The metrics layer is shared so benchmark results remain directly comparable between architectures.
