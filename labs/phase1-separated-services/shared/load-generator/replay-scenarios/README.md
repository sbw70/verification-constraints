# Replay Scenarios

This directory defines replay-oriented workload behavior used throughout the benchmark environment.

Replay scenarios exist to measure how each request path handles repeated or reused request material under equivalent workload conditions.

Replay definitions may include:
- repeated token usage
- repeated request identifiers
- repeated transaction payloads
- repeated trace identifiers
- nonce reuse attempts
- session replay attempts
- rapid duplicate submission
- delayed replay traffic
- replay burst conditions

The purpose of replay scenarios is to evaluate:
- replay visibility timing
- replay rejection timing
- downstream activation before replay denial
- stateful interaction during replay handling
- execution depth before replay detection

Both benchmark paths should receive equivalent replay conditions whenever possible so replay handling behavior remains directly comparable.
