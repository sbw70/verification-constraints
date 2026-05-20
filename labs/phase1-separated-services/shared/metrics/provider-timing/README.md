# Provider Timing Metrics

This directory defines measurements related to provider visibility and provider-controlled decision timing.

Provider timing metrics exist to measure when the provider/verifier becomes involved in the execution chain relative to downstream infrastructure activation.

Measurements may include:
- time until provider sees request
- verifier processing latency
- provider decision timing
- denial timing
- allow timing
- provider visibility position within request flow
- admissibility timing
- provider response latency

The purpose of provider timing metrics is to compare how request ordering changes:
- provider visibility
- denial timing behavior
- execution depth before admissibility
- downstream activation before authorization

These measurements are central to evaluating the operational differences between intermediary-first and provider-first request ordering models.
