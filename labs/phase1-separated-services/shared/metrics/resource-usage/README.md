# Resource Usage Metrics

This directory defines infrastructure resource measurements used throughout the benchmark environment.

Resource usage metrics exist to measure how request ordering affects infrastructure consumption during benchmark execution.

Measurements may include:
- CPU utilization
- memory utilization
- request throughput
- concurrency behavior
- service saturation
- load distribution
- timeout frequency
- resource utilization under invalid traffic
- resource utilization under mixed traffic

The purpose of resource usage metrics is to compare how intermediary-first and provider-first request ordering affect infrastructure consumption during sustained operation.

These measurements help evaluate whether earlier admissibility decisions reduce unnecessary downstream execution and infrastructure activation.
