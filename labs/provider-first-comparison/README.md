# Provider-First vs Conventional Request Ordering

This lab family compares conventional enterprise request ordering against provider-first / NUVL-style request ordering.

The core question is:

> How much infrastructure activates before the provider can say no?

These labs are intended to measure operational behavior, including:
- provider visibility timing
- rejection timing
- pre-denial activation
- pre-denial data exposure
- latency
- throughput
- resource behavior under load

This is not a governance dissertation or a mathematical proof of authority drift.

It is a repeatable systems comparison focused on whether request ordering changes observable behavior.
