# Latency Metrics

This directory defines latency measurements used across both benchmark paths.

Latency metrics exist to measure how long requests spend at different points in the execution chain.

Measurements may include:
- end-to-end request latency
- per-service processing time
- gateway latency
- application activation latency
- data-service latency
- verifier latency
- denial latency
- allow latency
- timeout duration

Latency metrics are shared so conventional and provider-first paths can be compared using the same timing vocabulary.

The benchmark uses these measurements to evaluate whether changing request ordering introduces acceptable overhead while changing when infrastructure activates.
